/* Real-app checks of unknown-only CEFR order and the global exam-deck gate. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const { chromium } = require('../.audit-deps/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
for (const [, attrs, code] of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) if (!/\btype=/.test(attrs)) new vm.Script(code);
const data = key => JSON.parse(html.match(new RegExp('<script[^>]*id="' + key + '"[^>]*>([\\s\\S]*?)</script>'))[1]);
const vocab = data('vocab-data'), work = data('work-data');
const levels = ['A2', 'B1', 'B2', 'C1', 'C1+'];
const mainIds = new Set(vocab.map(e => e.id)), examIds = new Set(work.map(e => e.id));
const served = html.replace('const Words = {', 'const Words = window.__sequenceWords = {');
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/favicon.ico')) { res.writeHead(204); res.end(); return; }
  res.setHeader('Content-Type', req.url.startsWith('/version.json') ? 'application/json' : 'text/html; charset=utf-8');
  res.end(req.url.startsWith('/version.json') ? fs.readFileSync(path.join(root, 'version.json')) : served);
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/#words`;
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const results = [], errors = [], contexts = [];
  const pass = name => { results.push(name); console.log('PASS', name); };
  const open = async learned => {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
    contexts.push(context);
    await context.route('https://**/*', route => route.abort());
    await context.addInitScript(learned => {
      if (!sessionStorage.getItem('__sequenceSeeded')) {
        localStorage.setItem('english-study-app.v1', JSON.stringify({ schemaVersion: 1, learned, settings: { uiLang: 'tr', path: 'all', showTurkish: true }, quiz: { attempts: 0, correct: 0 }, activity: {} }));
        sessionStorage.setItem('__sequenceSeeded', '1');
      }
    }, learned);
    const page = await context.newPage(); page.setDefaultTimeout(10000);
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base); await page.waitForFunction(() => window.__appReady === true);
    return page;
  };
  const state = page => page.evaluate(() => ({ exam: __sequenceWords.exam, ids: __sequenceWords.results.map(e => e.id), levels: __sequenceWords.results.map(e => e.level) }));
  const card = (page, id) => page.locator('#word-list .word-card[data-id="' + id + '"]');
  try {
    const a2 = vocab.filter(e => e.level === 'A2');
    const known = a2.slice(0, 2).map(e => e.id);
    const page = await open(known);
    let current = await state(page);
    assert.equal(current.exam, false); assert.equal(current.ids.length, vocab.length - known.length);
    assert.equal(current.levels[0], 'A2'); assert(current.ids.every(id => mainIds.has(id) && !known.includes(id)));
    assert(current.levels.every((level, i) => !i || levels.indexOf(current.levels[i - 1]) <= levels.indexOf(level)));
    assert.equal(await page.locator('#level-filter,#sort-select,[data-status]').count(), 0);
    pass('Only unknown regular words appear, starting at A2 and maintaining CEFR order');
    const target = page.locator('#word-list .word-card').nth(8);
    const learnedId = await target.getAttribute('data-id');
    await target.scrollIntoViewIfNeeded();
    const beforeScroll = await page.evaluate(() => scrollY);
    await target.locator('.media-toggle').click();
    await page.waitForFunction(id => !document.querySelector('#word-list .word-card[data-id="' + id + '"]'), learnedId);
    assert(beforeScroll > 100); assert(await page.evaluate(() => scrollY > 100));
    assert(!(await state(page)).ids.includes(learnedId));
    await page.reload(); await page.waitForFunction(() => window.__appReady === true);
    assert(!(await state(page)).ids.includes(learnedId));
    assert.equal(await page.evaluate(() => EnglishStudyDiagnostics.progressSummary().learned), known.length + 1);
    pass('Marking a word learned removes it immediately without jumping to the top; reload preserves it');
    const examOnly = work.find(e => !vocab.some(v => [v.word, v.meaning, v.example, v.exampleTr, v.definition].filter(Boolean).join(' ').toLocaleLowerCase('tr').includes(e.word.toLocaleLowerCase('tr'))));
    assert(examOnly);
    await page.locator('#word-search').fill(examOnly.word);
    await page.waitForFunction(() => __sequenceWords.results.length === 0);
    assert.equal((await state(page)).exam, false);
    assert.equal(await page.locator('#word-list .word-card[data-level="EXAM"]').count(), 0);
    await page.locator('#reset-filters').click();
    assert((await state(page)).ids.every(id => mainIds.has(id)));
    pass('An exam-only search cannot bypass the normal-word completion gate');
    const advanced = await open(a2.map(e => e.id));
    current = await state(advanced); assert.equal(current.levels[0], 'B1');
    assert(!current.levels.includes('A2')); assert.equal(current.exam, false);
    pass('When all A2 words are learned the next unknown level begins at B1');
    const last = vocab.at(-1), alreadyExam = work.slice(0, 2).map(e => e.id);
    const transition = await open(vocab.filter(e => e.id !== last.id).map(e => e.id).concat(alreadyExam));
    current = await state(transition); assert.deepEqual(current.ids, [last.id]);
    await transition.locator('#word-search').fill(last.word);
    await card(transition, last.id).locator('.media-toggle').click();
    await transition.waitForFunction(() => __sequenceWords.exam === true && __sequenceWords.results.length > 0);
    current = await state(transition);
    assert.equal(current.ids.length, work.length - alreadyExam.length);
    assert(current.ids.every(id => examIds.has(id) && !alreadyExam.includes(id)));
    assert.equal(await transition.locator('#word-search').inputValue(), '');
    const firstExam = work.find(e => !alreadyExam.includes(e.id));
    const examCard = card(transition, firstExam.id); await examCard.waitFor({ state: 'visible' });
    assert.equal(await examCard.locator('.meaning').innerText(), firstExam.meaning);
    assert.equal(await examCard.getAttribute('data-level'), 'EXAM');
    await examCard.locator('.media-toggle').click();
    assert(!(await state(transition)).ids.includes(firstExam.id));
    await transition.reload(); await transition.waitForFunction(() => window.__appReady === true);
    current = await state(transition); assert.equal(current.exam, true); assert(!current.ids.includes(firstExam.id));
    await transition.locator('#word-search').fill(firstExam.word);
    await transition.waitForTimeout(200); assert.equal(await card(transition, firstExam.id).count(), 0);
    await transition.locator('#reset-filters').click();
    for (const width of [320, 390, 1440]) {
      await transition.setViewportSize({ width, height: 844 });
      assert(await transition.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    pass('The final regular-word click unlocks real exam cards; learned exam cards remain hidden after reload');
    const finished = await open(vocab.concat(work).map(e => e.id));
    current = await state(finished); assert.equal(current.exam, true); assert.equal(current.ids.length, 0);
    assert.equal(await finished.locator('#word-list .word-card').count(), 0);
    assert((await finished.locator('#word-empty strong').innerText()).includes('tamamladın'));
    pass('Completing both lists shows a truthful completed state');
    assert.deepEqual(errors, []);
    const out = path.join(root, 'audits/2026-11-15'); fs.mkdirSync(out, { recursive: true });
    await page.setViewportSize({ width: 390, height: 844 }); await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({ path: path.join(out, 'unknown-words-390.png') });
    await transition.setViewportSize({ width: 390, height: 844 }); await transition.evaluate(() => scrollTo(0, 0));
    await transition.screenshot({ path: path.join(out, 'exam-words-unlocked-390.png') });
    fs.writeFileSync(path.join(out, 'vocabulary-sequence-checks.json'), JSON.stringify({ results, errors, mainWords: vocab.length, examWords: work.length }, null, 2) + '\n');
  } finally { for (const context of contexts) await context.close(); await browser.close(); server.close(); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
