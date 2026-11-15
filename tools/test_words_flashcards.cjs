/* Words uses the existing home-deck study workspace, not a scrolling card list. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const { chromium } = require('../.audit-deps/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
for (const [, attrs, code] of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) if (!/\btype=/.test(attrs)) new vm.Script(code);
const data = key => JSON.parse(html.match(new RegExp('<script[^>]*id="' + key + '"[^>]*>([\\s\\S]*?)</script>'))[1]);
const vocab = data('vocab-data'), work = data('work-data');
const byId = new Map([...vocab, ...work].map(e => [e.id, e]));
const examIds = new Set(work.map(e => e.id));
let served = html;
for (const name of ['Words', 'Review']) served = served.replace('const ' + name + ' = {', 'const ' + name + ' = window.__flash' + name + ' = {');
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/favicon.ico')) { res.writeHead(204); res.end(); return; }
  res.setHeader('Content-Type', req.url.startsWith('/version.json') ? 'application/json' : 'text/html; charset=utf-8');
  res.end(req.url.startsWith('/version.json') ? fs.readFileSync(path.join(root, 'version.json')) : served);
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const contexts = [], results = [], errors = [];
  const pass = name => { results.push(name); console.log('PASS', name); };
  const open = async (learned = [], pending = []) => {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce', timezoneId: 'Europe/Istanbul' });
    contexts.push(context); await context.route('https://**/*', route => route.abort());
    await context.addInitScript(({ learned, pending }) => {
      if (sessionStorage.getItem('__flashSeeded')) return;
      localStorage.setItem('english-study-app.v1', JSON.stringify({ schemaVersion: 1, learned, settings: { uiLang: 'tr', path: 'all', showTurkish: true }, quiz: { attempts: 0, correct: 0 }, activity: {} }));
      const now = new Date(), today = Math.floor((now - now.getTimezoneOffset() * 60000) / 864e5);
      const cards = Object.fromEntries(pending.map(({ id, days = 1 }) => ['w:' + id, [today + days, 0, 230, 0, 1]]));
      localStorage.setItem('english-study-review.v1', JSON.stringify({ goal: 20, cards, saved: {}, log: {}, recall: {}, seeded: true }));
      sessionStorage.setItem('__flashSeeded', '1');
    }, { learned, pending });
    const page = await context.newPage(); page.setDefaultTimeout(12000); page.on('pageerror', error => errors.push(error.message));
    await page.goto(base + '#words'); await page.waitForFunction(() => window.__appReady === true);
    return page;
  };
  const current = page => page.evaluate(() => ({ queue: [...__flashReview.queue], mode: __flashReview.mode, level: __flashReview.level, shown: __flashReview.shown, learned: JSON.parse(localStorage.getItem('english-study-app.v1')).learned }));
  const reveal = async page => { if (!(await current(page)).shown) await page.locator('#review-card .flash-card').click(); await page.locator('#review-card .review-meaning').waitFor({ state: 'visible' }); };
  const good = async page => { await reveal(page); await page.locator('#review-card [data-rate="good"]').click(); };
  try {
    const a2 = vocab.filter(e => e.level === 'A2');
    const page = await open(a2.slice(0, 2).map(e => e.id));
    assert(await page.locator('[data-view="words"]').evaluate(el => el.classList.contains('is-active')));
    assert.equal(await page.locator('#word-list .word-card:visible').count(), 0);
    assert.equal(await page.locator('#review-card').evaluate(el => el.closest('.view').dataset.view), 'words');
    assert.equal(await page.locator('#review-card .flash-card').count(), 1);
    let state = await current(page), id = state.queue[0].slice(2);
    assert.equal(id, a2[2].id); assert.equal(state.mode, 'learn'); assert.equal(state.level, 'A2');
    assert(!state.queue.some(key => examIds.has(key.slice(2))));
    assert.equal(await page.locator('#review-card .review-meaning').count(), 0);
    await page.locator('#review-card [data-act="show"]').focus(); await page.keyboard.press('Space');
    assert.equal(await page.locator('#review-card .review-meaning').innerText(), byId.get(id).meaning);
    assert.equal(await page.locator('#review-card [data-rate]').count(), 2);
    pass('Words opens the same single-card study workspace, at the first unknown A2 word; answer stays hidden until reveal');
    await page.keyboard.press('2');
    await page.waitForFunction(id => JSON.parse(localStorage.getItem('english-study-app.v1')).learned.includes(id), id);
    state = await current(page); assert.notEqual(state.queue[0], 'w:' + id);
    await page.reload(); await page.waitForFunction(() => window.__appReady === true);
    assert(!(await current(page)).queue.includes('w:' + id));
    pass('Keyboard reveal and Learned use real progress; the next word appears and learned words stay excluded after reload');
    state = await current(page); const missed = state.queue[0].slice(2);
    await reveal(page); await page.locator('#review-card [data-rate="again"]').click();
    const failed = await page.evaluate(id => ({ card: __flashReview.state.cards['w:' + id], today: __flashReview.today(), learned: JSON.parse(localStorage.getItem('english-study-app.v1')).learned }), missed);
    assert(!failed.learned.includes(missed)); assert.equal(failed.card[0], failed.today + 1); assert.equal(failed.card[3], 0);
    pass('Again keeps the word unknown and schedules it for tomorrow');
    const b1 = await open(a2.map(e => e.id));
    assert.equal((await current(b1)).level, 'B1'); assert.equal(byId.get((await current(b1)).queue[0].slice(2)).level, 'B1');
    pass('Completing A2 starts the next unknown B1 card');
    const pendingA2 = a2[0];
    const waiting = await open(vocab.filter(e => e.id !== pendingA2.id).map(e => e.id), [{ id: pendingA2.id, days: 1 }]);
    state = await current(waiting); assert(!state.queue.some(key => examIds.has(key.slice(2))));
    assert.equal(await waiting.locator('#review-card .flash-card').count(), 0);
    const due = await open(vocab.filter(e => e.id !== pendingA2.id).map(e => e.id), [{ id: pendingA2.id, days: -1 }]);
    assert.equal((await current(due)).queue[0], 'w:' + pendingA2.id);
    pass('A postponed unknown regular word cannot unlock exams; when due it remains studyable');
    const last = vocab.at(-1);
    const transition = await open(vocab.filter(e => e.id !== last.id).map(e => e.id));
    assert.equal((await current(transition)).queue[0], 'w:' + last.id);
    await good(transition);
    // A completed short round may expose the ordinary "more words" action.
    if (!(await current(transition)).queue.length) {
      const more = transition.locator('#review-card [data-act="more"]');
      if (await more.count()) await more.click();
    }
    await transition.waitForFunction(() => __flashReview.queue.length > 0);
    state = await current(transition); assert.equal(state.level, 'EXAM'); assert(state.queue.every(key => examIds.has(key.slice(2))));
    pass('The final regular Learned answer unlocks the separate exam deck in the same study-card interface');
    const done = await open(vocab.concat(work).map(e => e.id));
    assert.equal((await current(done)).queue.length, 0); assert.equal(await done.locator('#review-card .flash-card').count(), 0);
    assert(/öğrenildi|tamam/i.test(await done.locator('#review-card').innerText()));
    pass('Completing both pools shows a truthful finished state');
    await page.evaluate(() => location.hash = 'home');
    await page.locator('#decks a[href="#review/learn/A2"]').click();
    await page.locator('[data-view="review"].is-active').waitFor();
    assert.equal(await page.locator('#review-card').evaluate(el => el.closest('.view').dataset.view), 'review');
    assert.equal((await current(page)).mode, 'learn');
    await page.evaluate(() => location.hash = 'words'); await page.locator('[data-view="words"].is-active').waitFor();
    assert.equal(await page.locator('#review-card').count(), 1);
    assert.equal(await page.locator('#review-card').evaluate(el => el.closest('.view').dataset.view), 'words');
    for (const width of [320, 390, 1440]) {
      await page.setViewportSize({ width, height: 844 }); assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    pass('Home deck navigation still works; one workspace moves between routes without duplicate IDs or narrow-screen overflow');
    assert.deepEqual(errors, []);
    const out = path.join(root, 'audits/2026-11-15'); fs.mkdirSync(out, { recursive: true });
    await page.setViewportSize({ width: 390, height: 844 }); await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({ path: path.join(out, 'words-study-390.png') });
    fs.writeFileSync(path.join(out, 'words-flashcard-checks.json'), JSON.stringify({ results, errors }, null, 2) + '\n');
  } finally { for (const context of contexts) await context.close(); await browser.close(); server.close(); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
