/* Verify reviewed content in data, static cards, search, quizzes and review.
   --live checks the exact deployed build as well as the real browser UI. */
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const { chromium } = require('../.audit-deps/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'tools/vocabulary_corrections.json'), 'utf8'));
const data = id => JSON.parse(source.match(new RegExp('<script[^>]*id="' + id + '"[^>]*>([\\s\\S]*?)</script>'))[1]);
const vocab = data('vocab-data'), work = data('work-data'), sentences = data('sentence-data');
const byId = new Map([...vocab, ...work].map(e => [e.id, e]));
const esc = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#x27;');
const results = [];
const pass = detail => { results.push(detail); console.log('PASS', detail); };
assert.equal(vocab.length, 2200);
assert.equal(work.length, 3806);
assert.equal(byId.size, vocab.length + work.length);
for (const fix of catalogue.corrections) {
  const entry = byId.get(fix.id);
  assert.equal(entry.word, fix.word);
  for (const [field, value] of Object.entries(fix.after)) assert.equal(entry[field], value, fix.id + ':' + field);
  if (vocab.includes(entry)) {
    const card = source.match(new RegExp('<article class="word-card" data-id="' + fix.id + '"[\\s\\S]*?</article>'))[0];
    for (const [field, value] of Object.entries(fix.after)) assert(card.includes(esc(value)), fix.id + ':' + field + ' static markup');
  }
  if (fix.sentenceGroups) assert.deepEqual(sentences[entry.word.toLowerCase()], fix.sentenceGroups);
}
assert(!vocab.some(e => /ISO 639|ISO 3166|language code for/.test(e.definition || '')), 'Dictionary metadata must not be a learner definition');
pass(`${catalogue.corrections.length} corrections agree across JSON, examples and static cards; no language-code definitions`);
const classroom = byId.get('extra-classroom');
assert.equal(classroom.word, 'classroom'); assert.equal(classroom.meaning, 'derslik, sınıf');
assert(!/programlama/.test(classroom.meaning));
assert.equal(byId.get('wk-ai-48').meaning, 'sınıf, ders');
assert(!JSON.stringify(sentences.class).includes('Each class should do one thing well'));
assert(!/programlama/.test(byId.get('wk-ai-48').meaning));
assert.equal(vocab.filter(e => e.word.toLowerCase() === 'classroom').length, 1);
pass('Class and classroom are distinct entries; all previous 6005 word IDs retained');
let served = source;
for (const name of ['Quiz', 'Review']) served = served.replace('const ' + name + ' = {', 'const ' + name + ' = window.__content' + name + ' = {');
const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'text/html; charset=utf-8'); res.end(served);
});
(async () => {
  const live = process.argv.includes('--live');
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const build = JSON.parse(fs.readFileSync(path.join(root, 'version.json'), 'utf8')).build;
  const base = live ? 'https://twinterrordark.github.io/english-vocabulary/?v=' + build : `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    if (live) {
      const response = await fetch(base, { signal: AbortSignal.timeout(30000) }); assert.equal(response.status, 200);
      const sha = s => crypto.createHash('sha256').update(s).digest('hex');
      assert.equal(sha(Buffer.from(await response.arrayBuffer())), sha(Buffer.from(source)));
      pass('Published HTML exactly matches the tested local build');
    }
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
    const page = await context.newPage(); const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base + '#words'); await page.waitForFunction(() => window.__appReady === true);
    assert.equal(await page.evaluate(() => EnglishStudyDiagnostics.words), 2200);
    for (const id of ['extra-classroom', 'wk-ai-48', 'wk-ai-43', 'wk-ai-103', 'wk-des-26']) {
      const entry = byId.get(id);
      await page.locator('#word-search').fill(entry.word);
      const card = page.locator('#word-list .word-card[data-id="' + id + '"]');
      await card.waitFor({ state: 'visible' });
      assert.equal(await card.locator('.meaning').innerText(), entry.meaning);
      assert.equal(await card.locator('.example').innerText(), entry.example);
      assert.equal(await card.locator('.tr-line').first().innerText(), entry.exampleTr);
    }
    pass('Browser search cards show corrected class/library/ticket/finish and separate classroom');
    await page.locator('#word-search').fill('classroom');
    await page.waitForFunction(() => [...document.querySelectorAll('#word-list .word-card')].every(e => e.textContent.toLowerCase().includes('classroom')));
    for (const width of [320, 390, 1440]) {
      await page.setViewportSize({ width, height: 844 });
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    const out = path.join(root, 'audits/2026-11-10');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator('#word-list .word-card[data-id="extra-classroom"]').scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(out, live ? 'vocabulary-live-classroom.png' : 'vocabulary-classroom.png'), fullPage: false });
    pass('Corrected classroom card fits mobile and desktop widths');
    if (!live) {
      const checks = await page.evaluate(ids => {
        const entries = JSON.parse(document.getElementById('vocab-data').textContent).concat(JSON.parse(document.getElementById('work-data').textContent));
        return ids.map(id => {
          const entry = entries.find(e => e.id === id);
          // Use actual runtime objects so quizzes and reviews read the same corrected entry.
          const question = window.__contentQuiz.makeQuestion(entry, 'en-tr');
          const reverse = window.__contentQuiz.makeQuestion(entry, 'tr-en');
          const content = window.__contentReview.content('w:' + id);
          return { id, meaning: entry.meaning, answer: question.options.find(o => o.correct).text, reverse: reverse.prompt, review: content };
        });
      }, ['wk-ai-48', 'extra-classroom', 'wk-exam-add3e676ab', 'wk-exam-22ad1709eb']);
      for (const check of checks) {
        assert.equal(check.answer, check.meaning);
        assert(check.reverse.includes(check.meaning));
        assert(JSON.stringify(check.review).includes(check.meaning));
      }
      pass('Both quiz directions and review use corrected word meanings');
    }
    assert.deepEqual(errors, []); pass('No uncaught browser errors');
    fs.writeFileSync(path.join(out, live ? 'vocabulary-live-checks.json' : 'vocabulary-checks.json'), JSON.stringify({ build, live, corrections: catalogue.corrections.length, words: vocab.length, examWords: work.length, results, errors }, null, 2) + '\n');
    await context.close();
  } finally { await browser.close(); server.close(); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
