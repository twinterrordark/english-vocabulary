/* Real reader UI checks. Translation and speech services are explicit test doubles. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const vm = require('node:vm');
const { chromium } = require('../.audit-deps/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
for (const [, attrs, code] of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) if (!/\btype=/.test(attrs)) new vm.Script(code);
assert(html.includes('id="novel-tr"'));
assert(!html.includes('id="study-home"'));
const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(html.replace('const Novel = {', 'const Novel = window.Novel = {')
    .replace('const Speech = (() => {', 'const Speech = window.__parallelSpeech = (() => {'));
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
  const page = await context.newPage(); page.setDefaultTimeout(10000);
  const errors = [], requests = [], results = [];
  page.on('pageerror', error => errors.push(error.message));
  const tr = {
    'Dr. Smith took his coat off.': 'Dr. Smith paltosunu çıkardı.',
    'She ate ice cream.': 'Dondurma yedi.',
    'The visitor smiled.': 'Ziyaretçi gülümsedi.',
    'A slow visitor arrived.': 'Yavaş bir ziyaretçi geldi.',
    'A fast visitor left.': 'Hızlı bir ziyaretçi ayrıldı.',
    'He took his coat off before leaving.': 'Gitmeden önce paltosunu çıkardı.',
    'An uncached sentence appeared.': 'Önbellekte olmayan bir cümle belirdi.'
  };
  let failing = false, googleFailing = false, releaseSlow;
  await context.route('https://**/*', async route => {
    const url = new URL(route.request().url());
    if (!/translate\.googleapis\.com|api\.mymemory\.translated\.net/.test(url.host)) return route.abort();
    const text = url.searchParams.get('q'); requests.push({ host: url.host, text });
    if (text.includes('A slow visitor arrived.')) await new Promise(resolve => { releaseSlow = resolve; });
    if (failing || (googleFailing && url.host.includes('googleapis'))) return route.fulfill({ status: 503, body: '{}' });
    const translated = text.split('\n').map(line => tr[line] || 'Test çevirisi.').join('\n');
    return route.fulfill({ json: url.host.includes('mymemory') ? { responseStatus: 200, responseData: { translatedText: translated } } : [[[translated, text]]] });
  });
  const pass = name => { results.push(name); console.log('PASS', name); };
  const open = pages => page.evaluate(pages => Novel.setBook({ name: 'parallel-test.pdf', title: 'Parallel test', pages }, 0), pages);
  const waitLines = lines => page.waitForFunction(lines => JSON.stringify([...document.querySelectorAll('#novel-text .novel-tr')].map(e => e.textContent)) === JSON.stringify(lines), lines);
  try {
    await page.goto(`http://127.0.0.1:${server.address().port}/#words`);
    await page.waitForFunction(() => window.__appReady === true);
    await page.locator('#word-search').fill('classroom');
    const word = page.locator('#word-list [data-id="extra-classroom"] .media-toggle'); await word.waitFor(); await word.click();
    await page.evaluate(() => {
      localStorage.setItem('english-study-novel.v1', JSON.stringify({ v: 3, name: 'earlier.pdf', marks: { 'earlier.pdf': 42 }, totals: { 'earlier.pdf': 100 }, titles: {}, size: 1.12, auto: false, paper: 'sepia' }));
      location.hash = 'novel';
    });
    await page.waitForFunction(() => document.querySelector('[data-view="novel"]').classList.contains('is-active'));
    await open([['Dr. Smith took his coat off. She ate ice cream.', 'The visitor smiled.']]);
    assert.equal(await page.locator('#novel-tr').getAttribute('aria-pressed'), 'false');
    assert.equal(await page.locator('#novel-text .novel-tr').count(), 0);
    await page.locator('#novel-tr').focus(); await page.keyboard.press('Enter');
    await waitLines([tr['Dr. Smith took his coat off.'], tr['She ate ice cream.'], tr['The visitor smiled.']]);
    assert.equal(await page.locator('#novel-tr').getAttribute('aria-pressed'), 'true');
    const pairs = await page.locator('#novel-text .novel-pair').evaluateAll(nodes => nodes.map(pair => {
      const en = pair.querySelector('.novel-sent'), translated = en.nextElementSibling;
      return { en: en.textContent, tr: translated.textContent, lang: translated.lang, adjacent: translated.classList.contains('novel-tr') };
    }));
    assert.deepEqual(pairs.map(p => p.en), ['Dr. Smith took his coat off.', 'She ate ice cream.', 'The visitor smiled.']);
    assert(pairs.every(p => p.adjacent && p.lang === 'tr'));
    assert(requests.some(r => r.text.includes('\n')), 'The page must batch sentence translation requests');
    pass('Top TR button works by keyboard; each complete English sentence has its own Turkish directly below');
    await page.locator('#novel-text .nw').filter({ hasText: /^off$/ }).click();
    await page.waitForFunction(() => document.querySelector('#novel-pop-line').textContent === 'Dr. Smith paltosunu çıkardı.');
    assert.equal(await page.locator('#novel-pop-word').innerText(), 'take off');
    assert.equal(await page.locator('#novel-pop-context').innerText(), 'Dr. Smith took his coat off.');
    await page.locator('#novel-pop-close').click();
    const speech = await page.evaluate(() => {
      window.__spoken = []; __parallelSpeech.hasTTS = true;
      __parallelSpeech.speakNow = text => { __spoken.push(text); return true; };
      Novel.startReading(); const queue = Novel.reading.queue.map(item => item.text); Novel.stopReading();
      return { queue, spoken: __spoken };
    });
    assert.deepEqual(speech.queue, pairs.map(p => p.en)); assert.deepEqual(speech.spoken, [pairs[0].en]);
    pass('Word and phrasal-verb lookup survives parallel layout; speech reads only English');
    await page.locator('#novel-tr').click();
    assert.equal(await page.locator('#novel-text .novel-pair').count(), 0);
    assert.deepEqual(await page.locator('#novel-text p').allTextContents(), ['Dr. Smith took his coat off. She ate ice cream.', 'The visitor smiled.']);
    const count = requests.length; await page.locator('#novel-tr').click();
    await waitLines(pairs.map(p => p.tr)); assert.equal(requests.length, count);
    pass('TR off restores original paragraphs; toggling back reuses cached translations');
    await open([['A slow visitor arrived.'], ['A fast visitor left.']]);
    await page.waitForFunction(() => document.querySelector('#novel-text .novel-sent')?.textContent === 'A slow visitor arrived.');
    for (let i = 0; !releaseSlow && i < 100; i++) await new Promise(resolve => setTimeout(resolve, 10));
    assert(releaseSlow); await page.evaluate(() => Novel.go(1)); await waitLines([tr['A fast visitor left.']]);
    releaseSlow(); await page.waitForTimeout(100);
    assert.equal(await page.locator('#novel-text .novel-sent').innerText(), 'A fast visitor left.');
    assert.equal(await page.locator('#novel-text .novel-tr').innerText(), tr['A fast visitor left.']);
    pass('Late translation from an old page cannot overwrite the current page');
    await open([['He took his coat'], ['\u2060off before leaving.']]);
    await page.evaluate(() => Novel.go(1)); await page.locator('#novel-text .nw').filter({ hasText: /^off$/ }).click();
    assert.equal(await page.locator('#novel-pop-context').innerText(), 'He took his coat off before leaving.');
    assert.equal(await page.locator('#novel-pop-word').innerText(), 'take off'); await page.locator('#novel-pop-close').click();
    pass('Word lookup keeps complete context across continued PDF pages while TR is on');
    failing = true; await open([['A failed translation needs a retry.']]);
    await page.locator('#novel-tr-retry').waitFor({ state: 'visible' });
    assert.equal(await page.locator('#novel-text .novel-sent').innerText(), 'A failed translation needs a retry.');
    failing = false; await page.locator('#novel-tr-retry').click(); await waitLines(['Test çevirisi.']);
    googleFailing = true; await open([['Fallback sentence.']]); await waitLines(['Test çevirisi.']);
    assert(requests.some(r => r.host.includes('mymemory') && r.text === 'Fallback sentence.')); googleFailing = false;
    pass('Service failure preserves English with a working retry; fallback service also translates');
    await context.setOffline(true); await open([['Dr. Smith took his coat off.']]); await waitLines([tr['Dr. Smith took his coat off.']]);
    await open([['An uncached sentence appeared.']]); await page.locator('#novel-tr-retry').waitFor({ state: 'visible' });
    await context.setOffline(false); await page.locator('#novel-tr-retry').click(); await waitLines([tr['An uncached sentence appeared.']]);
    pass('Cached sentences work offline; uncached sentences recover after reconnecting');
    await page.setViewportSize({ width: 320, height: 720 }); await page.evaluate(() => scrollTo(0, 0));
    assert(await page.locator('#novel-tr').isVisible()); assert(await page.locator('#novel-aa').isVisible());
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.waitForFunction(() => JSON.parse(localStorage.getItem('english-study-tr.v1') || '{}')['An uncached sentence appeared.']);
    await page.reload(); await page.waitForFunction(() => window.__appReady === true);
    await open([['Dr. Smith took his coat off.']]); await waitLines([tr['Dr. Smith took his coat off.']]);
    assert.equal(await page.locator('#novel-tr').getAttribute('aria-pressed'), 'true');
    const saved = await page.evaluate(() => ({ novel: JSON.parse(localStorage.getItem('english-study-novel.v1')), learned: EnglishStudyDiagnostics.progressSummary().learned }));
    assert.equal(saved.novel.tr, true); assert.equal(saved.novel.marks['earlier.pdf'], 42); assert(saved.learned >= 1);
    pass('TR choice, original bookmarks, cache and learned vocabulary survive reload; 320px layout fits');
    assert.deepEqual(errors, []);
    const out = path.join(root, 'audits/2026-11-12'); fs.mkdirSync(out, { recursive: true });
    await page.screenshot({ path: path.join(out, 'novel-parallel-320.png') });
    fs.writeFileSync(path.join(out, 'novel-parallel-checks.json'), JSON.stringify({ results, errors, requests: requests.length, mockedServices: true }, null, 2) + '\n');
  } finally { if (releaseSlow) releaseSlow(); await context.close(); await browser.close(); server.close(); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
