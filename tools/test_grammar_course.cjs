/* Run with node tools/test_grammar_course.cjs; optional PLAYWRIGHT_MODULE/CHANNEL. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const vm = require('node:vm');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
for (const match of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) if (!/\btype=/.test(match[1])) new vm.Script(match[2]);
const grammar = JSON.parse(html.match(/<script type="application\/json" id="grammar-data">([\s\S]*?)<\/script>/)[1]);
const added = grammar.topics.filter(topic => topic.reference);
assert.equal(grammar.topics.length, 14);
assert.equal(added.flatMap(topic => topic.units).length, 52);
assert.equal(added.flatMap(topic => topic.sets).flatMap(set => set.items).length, 208);
const ids = grammar.topics.flatMap(topic => topic.units.map(unit => unit.id));
assert.equal(new Set(ids).size, ids.length);
for (const topic of added) {
  assert.equal(topic.levels.length, new Set(topic.levels).size);
  for (const unit of topic.units) {
    assert(/^[a-z]{2}:[\w-]{1,80}$/.test(unit.id));
    assert.equal(unit.book.length, 0); // No invented examples attributed to the novels.
    const lesson = topic.lessons[unit.lesson];
    assert.equal(lesson.forms.length, 3);
    assert(lesson.forms.every(row => row.length === 2 && row.every(Boolean)));
    assert(lesson.examples.length >= 2);
    assert(lesson.sections.length >= 3);
    assert.equal(lesson.comparisons.length, 2);
    assert(lesson.sections.every(section => section.title && section.paragraphs.every(Boolean)));
    assert(lesson.examples.every(([en]) => lesson.exampleNotes[en]));
    const set = topic.sets.find(set => set.id === lesson.quiz.set);
    assert(set && set.items.length === 4);
    for (const item of set.items) {
      assert.equal(new Set(item.options).size, 4);
      assert.equal(item.options.filter(option => option === item.answer).length, 1);
      assert(item.tr && item.why && item.q.includes('___'));
    }
  }
}
const legacy = grammar.topics.find(topic => topic.id === 'cj');
const saved = { learned: { [legacy.units[0].id]: 1 }, best: { [legacy.sets[0].id]: 2 }, last: 'cj' };
const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', req.url.startsWith('/version.json') ? 'application/json' : 'text/html; charset=utf-8');
  res.end(req.url.startsWith('/version.json') ? fs.readFileSync(path.join(__dirname, '../version.json'))
    : html.replace('const Grammar = {', 'const Grammar = window.Grammar = {'));
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {}) });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.setDefaultTimeout(15000);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.route('https://**/*', route => route.abort());
  await page.addInitScript(saved => {
    if (!localStorage.getItem('english-study-grammar.v1')) localStorage.setItem('english-study-grammar.v1', JSON.stringify(saved));
  }, saved);
  const navigate = async (topic, index) => {
    const hash = '#grammar' + (topic ? '/' + topic : '') + (index == null ? '' : '/' + index);
    await page.evaluate(hash => { location.hash = hash; }, hash);
    await page.waitForFunction(([topic, index]) => topic
      ? Grammar.topic?.id === topic && Grammar.unit === index
      : Grammar.mode === 'home', [topic, index == null ? null : index]);
  };
  try {
    await page.goto(`http://127.0.0.1:${server.address().port}/#grammar`);
    await page.waitForFunction(() => window.__appReady === true);
    assert.equal(await page.locator('#gram-topics .gram-topic').count(), 15); // 14 topics plus writing.
    assert((await page.locator('#gram-filter-status').textContent()).includes('260'));
    await page.locator('#gram-search').fill('Present Perfect');
    await page.locator('#gram-search').press('Tab');
    assert(await page.locator('#gram-topics a[href="#grammar/tn/6"]').isVisible());
    await page.locator('#gram-topics a[href="#grammar/tn/6"]').click();
    await page.waitForFunction(() => Grammar.topic?.id === 'tn' && Grammar.unit === 6);
    assert(await page.locator('.gram-forms').isVisible());
    assert(await page.locator('.gram-mistake').isVisible());
    assert.equal(await page.locator('#gram-unit .gram-analysis').count(), 2);
    assert.equal(await page.locator('#gram-unit .gram-comparison').count(), 2);
    const currentHash = await page.evaluate(() => location.hash);
    await page.locator('#gram-unit .gram-contents button').last().click();
    assert.equal(await page.evaluate(() => location.hash), currentHash);
    assert.equal(await page.locator('#gram-section-3 h3').evaluate(heading => heading === document.activeElement), true);
    assert(await page.locator('#gram-section-3').isVisible());
    assert.equal(await page.locator('#gram-filters').isVisible(), false);
    // A reference lesson opens directly before earlier lessons have been completed.
    await navigate('tn', 16);
    assert((await page.locator('#gram-unit h2').textContent()).includes('Future Perfect Continuous'));
    await navigate(null);
    await page.locator('#gram-search').fill('Future Perfect');
    await page.locator('#gram-level').selectOption('A1');
    assert.equal(await page.locator('#gram-topics .gram-topic').count(), 0);
    await page.locator('#gram-search').fill('zzznomatchinglesson');
    assert.equal(await page.locator('#gram-topics .gram-topic').count(), 0);
    await page.locator('#gram-search').fill('');
    await page.locator('#gram-level').selectOption('');
    assert.equal(await page.locator('#gram-topics .gram-topic').count(), 15);
    // Failed mini test does not mark the lesson learned; retry remains available.
    await navigate('bs', 0);
    await page.locator('#gram-unit [data-step="3"]').click();
    for (let i = 0; i < 3; i++) {
      const wrong = await page.evaluate(() => Grammar.run.items[Grammar.run.at].options.find(option => option !== Grammar.run.items[Grammar.run.at].answer));
      await page.locator('#gram-unit').getByRole('button', { name: wrong, exact: true }).click();
      assert(await page.locator('#gram-unit .gram-feedback.is-wrong').isVisible());
      assert((await page.locator('#gram-unit .gram-why').textContent()).trim());
      await page.locator('#gram-unit [data-act="next"]').click();
    }
    assert.equal(await page.evaluate(id => Boolean(Grammar.learned[id]), added[0].units[0].id), false);
    assert(await page.locator('#gram-unit [data-step="3"]').isVisible());
    // Exercise every new unit through its real delegated click handlers, offline.
    await page.context().setOffline(true);
    let completed = 0;
    for (const topic of added) for (let index = 0; index < topic.units.length; index++) {
      await navigate(topic.id, index);
      // Re-open a unit left on its result screen during the failure test.
      await page.evaluate(() => Grammar.step(1));
      const result = await page.evaluate(() => {
        const unit = Grammar.topic.units[Grammar.unit];
        if (document.querySelectorAll('#gram-unit .gram-forms div').length !== 3) throw new Error('Missing form reference: ' + unit.id);
        if (document.querySelectorAll('#gram-unit .gram-examples li').length < 2) throw new Error('Missing examples: ' + unit.id);
        if (document.querySelectorAll('#gram-unit .gram-analysis').length !== 2) throw new Error('Missing worked examples: ' + unit.id);
        if (document.querySelectorAll('#gram-unit .gram-comparison').length !== 2) throw new Error('Missing comparisons: ' + unit.id);
        if (document.querySelectorAll('#gram-unit .gram-explanation').length < 4) throw new Error('Missing detailed explanation: ' + unit.id);
        document.querySelector('#gram-unit [data-step="3"]').click();
        for (let i = 0; i < 3; i++) {
          const answer = Grammar.run.items[Grammar.run.at].answer;
          const option = [...document.querySelectorAll('#gram-unit .gram-option')].find(button => button.dataset.option === answer);
          if (!option) throw new Error('Answer not rendered: ' + unit.id);
          option.click();
          if (!document.querySelector('#gram-unit .gram-feedback.is-right .gram-why')?.textContent) throw new Error('No explanation: ' + unit.id);
          document.querySelector('#gram-unit [data-act="next"]').click();
        }
        return { learned: Boolean(Grammar.learned[unit.id]), score: document.querySelector('#gram-unit .gram-score').textContent };
      });
      assert.deepEqual(result, { learned: true, score: '3 / 3' });
      completed++;
    }
    await page.context().setOffline(false);
    console.log('PASS: all', completed, 'new lessons, form references, explanations, quizzes and progress work offline');
    // Full practice set also records a score rather than changing the unit record.
    await navigate('tn', null);
    await page.locator('[data-gtab="practice"]').click();
    await page.locator('#gram-practice [data-set="tn-1"]').click();
    for (let i = 0; i < 4; i++) {
      const answer = await page.evaluate(() => Grammar.run.items[Grammar.run.at].answer);
      await page.locator('#gram-practice').getByRole('button', { name: answer, exact: true }).click();
      await page.locator('#gram-practice [data-act="next"]').click();
    }
    assert.equal(await page.evaluate(() => Grammar.best['tn-1']), 4);
    await page.reload();
    await page.waitForFunction(() => window.__appReady === true);
    const persistence = await page.evaluate(() => ({ learned: Grammar.learned, best: Grammar.best, sanitized: Grammar.sanitize(JSON.parse(localStorage.getItem(Grammar.KEY))) }));
    assert.equal(Object.keys(persistence.learned).length, 53);
    assert.equal(persistence.best[legacy.sets[0].id], 2);
    assert.equal(Object.keys(persistence.sanitized.learned).length, 53);
    assert.equal(persistence.best['tn-1'], 4);
    // Existing topic access and route behaviour still work.
    await navigate('cj', 0);
    assert(await page.locator('#gram-unit h2').isVisible());
    await navigate('rc', null);
    assert(await page.locator('#gram-novel-tab').isVisible());
    await page.setViewportSize({ width: 390, height: 844 });
    await navigate(null);
    await page.locator('#gram-search').fill('zaman');
    assert.equal(await page.locator('#gram-topics .gram-topic').first().getAttribute('href'), '#grammar/tn');
    assert(await page.locator('#gram-search').isVisible());
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    if (process.env.GRAMMAR_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.GRAMMAR_SCREENSHOT_DIR, 'grammar-search-mobile.png') });
    await navigate('tn', 6);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    assert(await page.locator('#gram-unit .gram-forms').isVisible());
    if (process.env.GRAMMAR_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.GRAMMAR_SCREENSHOT_DIR, 'grammar-present-perfect-mobile.png'), fullPage: true });
    assert.deepEqual(errors, []);
    console.log('PASS: search, combined level filter, direct lesson access, failed/retried quizzes, practice scores, legacy progress, export/import validation and mobile layout');
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
