/* End-to-end checks of the built standalone application. Media tests use explicit test doubles. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const { chromium } = require('../.audit-deps/node_modules/playwright');
const { default: AxeBuilder } = require('../.audit-deps/node_modules/@axe-core/playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'audits', '2026-11-10');
fs.mkdirSync(out, { recursive: true });
const original = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
for (const [, attrs, code] of original.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) if (!/\btype=/.test(attrs)) new vm.Script(code);
let served = original;
for (const name of ['Study', 'Review', 'Grammar', 'Writer', 'Tutor']) served = served.replace('const ' + name + ' = {', 'const ' + name + ' = window.' + name + ' = {');
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/favicon.ico')) { res.writeHead(204); res.end(); return; }
  if (req.url.startsWith('/version.json')) { res.setHeader('Content-Type', 'application/json'); res.end(fs.readFileSync(path.join(root, 'version.json'))); return; }
  res.setHeader('Content-Type', 'text/html; charset=utf-8'); res.end(served);
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce', timezoneId: 'Europe/Istanbul' });
  await context.route('https://**/*', route => route.abort());
  await context.addInitScript(() => {
    const RealDate = Date;
    window.__studyNow = Number(sessionStorage.getItem('__studyTestNow')) || new RealDate('2026-11-10T12:00:00+03:00').getTime();
    window.Date = class extends RealDate { constructor(...args) { super(...(args.length ? args : [window.__studyNow])); } static now() { return window.__studyNow; } };
  });
  const page = await context.newPage();
  page.setDefaultTimeout(12000);
  const errors = [], results = [], scans = [];
  page.on('pageerror', error => errors.push(error.message));
  const base = `http://127.0.0.1:${server.address().port}/`;
  const pass = (name, detail) => { results.push({ name, detail }); console.log('PASS', name, detail ? JSON.stringify(detail) : ''); };
  const go = async route => {
    await page.evaluate(route => { location.hash = route; }, route);
    await page.waitForFunction(route => document.querySelector(`.view[data-view="${route.split('/')[0]}"]`)?.classList.contains('is-active'), route);
  };
  const snapshot = () => page.evaluate(() => Study.snapshot());
  const current = () => page.evaluate(() => Study.day());
  const outputDone = () => page.evaluate(() => Study.steps().find(step => step.id === 'output').done);
  try {
    await page.goto(base); await page.waitForFunction(() => window.__appReady === true);
    assert.equal(await page.evaluate(() => EnglishStudyDiagnostics.version), '2.8.0');
    assert.equal(await page.locator('.study-step').count(), 5);
    assert.equal(await page.locator('.study-library').evaluate(el => el.open), false);
    assert.equal(await page.evaluate(() => Study.steps().filter(step => step.done).length), 0);
    assert.equal((await current()).config.minutes, 30);
    for (const route of ['study/output', 'reading', 'grammar', 'home']) await go(route);
    assert.equal(await page.evaluate(() => Study.steps().filter(step => step.done).length), 0);
    pass('Opening activities does not complete them; daily plan and library hierarchy');

    await page.locator('#study-next').click();
    const target = (await current()).config.reviewTarget;
    for (let i = 0; i < target; i++) {
      await page.locator('#review-card .flash-card').click();
      await page.locator('#review-card [data-rate="good"]').click();
    }
    const reviewed = (await current()).reviewed;
    assert.equal(reviewed.length, target); assert.equal(new Set(reviewed).size, target);
    await page.evaluate(id => Study.noteReview(id), reviewed[0]);
    assert.equal((await current()).reviewed.length, target);
    await go('home'); assert.equal(await page.locator('[data-study-step="review"]').evaluate(el => el.classList.contains('is-done')), true);
    pass('Actual distinct card answers complete recall practice; duplicates do not count', { target });

    await page.locator('#study-next').click();
    assert((await page.evaluate(() => location.hash)).startsWith('#grammar/'));
    await page.locator('#gram-unit [data-step="3"]').click();
    for (let i = 0; i < 3; i++) {
      const answer = await page.evaluate(() => Grammar.run.items[Grammar.run.at].answer);
      await page.locator('#gram-unit').getByRole('button', { name: answer, exact: true }).click();
      await page.locator('#gram-unit [data-act="next"]').click();
    }
    assert.equal(await page.evaluate(() => Study.steps().find(step => step.id === 'grammar').done), true);
    pass('Passing the real grammar unit test completes the grammar step');

    await go('home'); await page.locator('#study-next').click();
    await page.locator('#reading-list a[href="#reading"]').waitFor({ state: 'visible' });
    assert.equal(await page.locator('#reading-list article.reading').count(), 1);
    const passage = await page.evaluate(() => Study.passage());
    const q = page.locator('#reading-list .choice-q');
    await q.nth(0).locator('button.option').nth((passage.questions[0].answer + 1) % 3).click();
    assert.equal(await page.evaluate(() => Study.steps().find(step => step.id === 'input').done), false);
    await q.nth(0).locator(':scope > button').click();
    for (let i = 0; i < passage.questions.length; i++) await q.nth(i).locator('button.option').nth(passage.questions[i].answer).click();
    assert.equal(await page.evaluate(() => Study.steps().find(step => step.id === 'input').done), true);
    pass('Assigned graded reading opens alone; comprehension requires correct answers', { passage: passage.id });

    await go('study/output');
    await page.locator('#study-writing').fill('I like this idea.'); await page.locator('#study-writing-save').click();
    assert.equal(await outputDone(), false);
    const writing = 'I usually buy fresh food at the market because I enjoy talking to local people. Last week I went there with a friend and we chose some vegetables for dinner. Next time I would like to try a different fruit and ask the farmer about it.';
    await page.locator('#study-writing').fill(writing); await page.locator('#study-writing-save').click(); assert.equal(await outputDone(), true);
    await page.locator('.study-mode a[href="#study/speak"]').click(); await page.locator('#study-record-start').waitFor({ state: 'visible' });
    assert(await page.locator('#study-writing').isHidden());
    await page.locator('.study-mode a[href="#study/output"]').click(); await page.locator('#study-writing').waitFor({ state: 'visible' });
    assert.equal(await page.locator('#study-writing').inputValue(), writing);
    await page.reload(); await page.waitForFunction(() => window.__appReady === true);
    assert.equal(await page.locator('#study-writing').inputValue(), writing); assert.equal(await outputDone(), true);
    await page.locator('#study-writing-review').click(); await page.locator('#story-editor').waitFor({ state: 'visible' });
    assert.equal(await page.locator('#story-text').inputValue(), writing);
    pass('Writing validation, local draft persistence and feedback handoff');

    const learnedBefore = await page.evaluate(() => EnglishStudyDiagnostics.progressSummary().learned);
    await go('study/recall');
    const wrongId = await page.evaluate(() => Study.run.queue[0]);
    await page.locator('#study-answer').fill('zzzwroong'); await page.locator('#study-answer').press('Enter');
    assert.equal((await current()).recall[wrongId].correct, false);
    assert.equal((await current()).recall[wrongId].attempts, 1);
    assert(await page.evaluate(id => Review.state.cards['w:' + id][4] > 0, wrongId));
    await page.locator('#study-recall-next').click();
    assert.notEqual(await page.evaluate(() => Study.run.queue[0]), wrongId);
    const hintId = await page.evaluate(() => Study.run.queue[0]);
    await page.locator('#study-hint').click(); await page.reload(); await page.waitForFunction(() => window.__appReady === true);
    assert(await page.locator('#study-recall-hint').isVisible());
    const hintWord = await page.evaluate(() => { const id = Study.run.queue[0]; const entry = JSON.parse(document.querySelector('#vocab-data').textContent).find(e => e.id === id); return entry.word; });
    await page.locator('#study-answer').fill(hintWord); await page.locator('#study-check').click();
    assert.equal((await current()).recall[hintId].first, false); assert.equal((await current()).recall[hintId].correct, false);
    await page.locator('#study-recall-next').click();
    let attempts = 0;
    while (await page.locator('#study-answer').count()) {
      assert(++attempts < 30, 'recall round did not finish');
      const word = await page.evaluate(() => { const id = Study.run.queue[0]; return JSON.parse(document.querySelector('#vocab-data').textContent).find(e => e.id === id).word; });
      await page.locator('#study-answer').fill(word.toUpperCase()); await page.locator('#study-answer').press('Enter'); await page.locator('#study-recall-next').click();
    }
    assert.equal(await page.evaluate(() => Study.steps().filter(step => step.done).length), 5);
    assert.equal(await page.evaluate(() => EnglishStudyDiagnostics.progressSummary().learned), learnedBefore);
    const recall = (await current()).recall;
    assert.equal(recall[wrongId].first, false); assert.equal(recall[hintId].first, false);
    pass('Typed recall: errors, persistent hints, intervening questions, first-attempt honesty and completion');

    const exported = await snapshot(); assert(!JSON.stringify(exported).includes('blob:'));
    await go('settings'); const downloadPromise = page.waitForEvent('download'); await page.locator('#export-progress').click(); const download = await downloadPromise;
    const exportedFile = JSON.parse(fs.readFileSync(await download.path(), 'utf8')); assert.deepEqual(exportedFile.study, exported);
    await page.evaluate(() => Study.clear()); assert.equal(await page.evaluate(() => Study.steps().filter(step => step.done).length), 0);
    await page.locator('#import-file').setInputFiles({ name: 'study-progress.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(exportedFile)) });
    await page.locator('#confirm-ok').click(); await page.waitForFunction(() => Study.steps().filter(step => step.done).length === 5);
    pass('Progress export and validated import include the guided study record');

    await page.evaluate(() => { window.__studyNow += 864e5; sessionStorage.setItem('__studyTestNow', window.__studyNow); }); await go('home');
    assert.equal(await page.evaluate(() => Study.steps().filter(step => step.done).length), 0);
    assert.equal(Object.keys((await snapshot()).days).length, 2);
    const savedConfig = (await current()).config;
    await page.reload(); await page.waitForFunction(() => window.__appReady === true);
    assert.deepEqual((await current()).config, savedConfig);
    pass('A new local day starts fresh while history and the current plan survive reload');

    await go('home'); await page.locator('.study-options summary').click();
    for (const level of ['A2', 'B1', 'B2', 'C1']) {
      await page.locator('#study-level').selectOption(level);
      if (!(await page.locator('#study-minutes').isVisible())) await page.locator('.study-options summary').click();
      for (const minutes of ['15', '30', '45']) {
        await page.locator('#study-minutes').selectOption(minutes);
        assert.equal((await current()).config.minutes, Number(minutes));
        assert.equal((await current()).config.level, level);
        if (!(await page.locator('#study-minutes').isVisible())) await page.locator('.study-options summary').click();
      }
    }
    pass('All four vocabulary paths and three daily durations can be selected');
    await go('reading'); await page.locator('#reading-level').waitFor({ state: 'visible' });
    assert.equal(await page.locator('.reading-tile').count(), 9);
    for (const [level, count] of [['A2', 2], ['B1', 3], ['B2', 3], ['C1', 2]]) { await page.locator('#reading-level').selectOption(level); assert.equal(await page.locator('.reading-tile').count(), count); }
    pass('Reading library presents nine compact, level-filtered texts');

    await go('study/speak');
    await page.evaluate(() => { Object.defineProperty(navigator.mediaDevices, 'getUserMedia', { configurable: true, writable: true, value: async () => { throw new DOMException('denied', 'NotAllowedError'); } }); });
    await page.locator('#study-record-start').click();
    await page.waitForFunction(() => document.querySelector('#study-record-status').textContent.includes('Mikrofon açılamadı'));
    assert.equal(await outputDone(), false);
    await page.evaluate(() => { window.__stoppedTracks = 0; navigator.mediaDevices.getUserMedia = () => new Promise(resolve => { window.__resolveMedia = resolve; }); });
    await page.locator('#study-record-start').click(); await page.waitForFunction(() => !!window.__resolveMedia); await go('home');
    await page.evaluate(() => window.__resolveMedia({ getTracks: () => [{ stop: () => window.__stoppedTracks++ }] }));
    await page.waitForFunction(() => window.__stoppedTracks === 1);
    await go('study/speak');
    await page.evaluate(() => {
      navigator.mediaDevices.getUserMedia = async () => ({ getTracks: () => [{ stop: () => window.__stoppedTracks++ }] });
      window.MediaRecorder = class {
        constructor() { this.state = 'inactive'; this.mimeType = 'audio/webm'; }
        start() { this.state = 'recording'; }
        stop() { this.state = 'inactive'; this.ondataavailable({ data: new Blob(['test'], { type: this.mimeType }) }); this.onstop(); }
      };
    });
    await page.locator('#study-record-start').click(); await page.waitForFunction(() => Study.recorder?.state === 'recording');
    await go('home'); assert(await page.evaluate(() => Study.recorder.state === 'inactive' && window.__stoppedTracks >= 2));
    assert.equal(await outputDone(), false);
    await page.evaluate(() => { Study.discardRecording(); });
    assert.equal(await page.evaluate(() => Study.recording), null);
    pass('Microphone denial falls back to writing; late permission and active recordings release tracks', { simulatedMedia: true });

    // The AI reply endpoint is stubbed; no real message or microphone data is sent.
    await context.route('https://english-teacher-3d.twinterrordark.workers.dev/api/chat', async route => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ reply: 'What do you enjoy about learning a language?', correction: '', tip: 'Bir örnek vererek cevabını genişletebilirsin.' }) });
    });
    await go('tutor'); await page.waitForFunction(() => !Tutor.busy && Tutor.history.length > 0);
    assert(!(await page.locator('#tutor-status').textContent()).includes('dinliyor'));
    await page.locator('#tutor-keyboard').click();
    for (const text of ['I enjoy learning new words in a story.', 'I would like to talk about my daily routine.']) {
      await page.locator('#tutor-input').fill(text); await page.locator('#tutor-type').getByRole('button', { name: 'Gönder', exact: true }).click(); await page.waitForFunction(() => !Tutor.busy);
    }
    assert.equal(await outputDone(), true); assert.equal(await page.locator('#tutor-chat .tutor-acc').count(), 0);
    pass('Successful learner turns count as output; AI feedback has no invented accuracy percentage', { simulatedAI: true });

    await go('settings'); await page.locator('#ui-lang').selectOption('en'); await go('home'); assert((await page.locator('#study-home').textContent()).includes('What should I study today?'));
    await go('study/output'); assert((await page.locator('#study-app').textContent()).includes('Your own English text'));
    await go('settings'); await page.locator('#ui-lang').selectOption('tr');
    const surfaces = ['home', 'study/output', 'study/speak', 'study/recall', 'reading', 'reading/' + (await current()).config.passage, 'practice'];
    for (const theme of ['light', 'dark']) {
      await go('settings'); await page.locator(`input[name="theme"][value="${theme}"]`).check();
      for (const width of [320, 390, 768, 1440]) {
        await page.setViewportSize({ width, height: width > 1000 ? 1000 : 844 });
        for (const route of surfaces) {
          await go(route); assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${theme}/${width}/${route}`);
          if (width === 390) {
            const axe = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice']).analyze();
            const violations = axe.violations.map(v => ({ id: v.id, nodes: v.nodes.map(n => ({ target: n.target, summary: n.failureSummary })) }));
            scans.push({ theme, route, violations });
          }
          if ([390, 1440].includes(width)) await page.screenshot({ path: path.join(out, `after-${theme}-${route.split('/')[0]}-${route.includes('/recall') ? 'recall-' : ''}${width}.png`) });
        }
      }
    }
    fs.writeFileSync(path.join(out, 'study-accessibility.json'), JSON.stringify(scans, null, 2));
    assert.deepEqual(scans.filter(scan => scan.violations.length), []);
    await page.setViewportSize({ width: 1440, height: 1000 }); await go('home'); await page.locator('#side-toggle').click();
    assert(await page.getByRole('link', { name: 'Rehberli çalışma', exact: true }).isVisible());
    const collapsed = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice']).analyze();
    assert.deepEqual(collapsed.violations.map(v => v.id), []);
    await page.locator('#side-toggle').click();
    pass('Collapsed desktop navigation retains accessible link names');
    pass('Both languages, both themes and four viewport widths', { viewportChecks: surfaces.length * 8, accessibilityScans: scans.length });
    await page.goto(base + '?storage=off#study/output'); await page.waitForFunction(() => window.__appReady === true);
    assert.equal(await page.evaluate(() => EnglishStudyDiagnostics.storageUsable), false); assert(await page.locator('#study-writing').isVisible());
    await page.goto('file:///' + path.join(root, 'index.html').replace(/\\/g, '/') + '#study/output'); await page.waitForFunction(() => window.__appReady === true); assert(await page.locator('#study-writing').isVisible());
    pass('Unavailable storage and standalone file:// guided study');
    assert.deepEqual(errors, []); pass('No uncaught JavaScript errors');
    fs.writeFileSync(path.join(out, 'study-regression.json'), JSON.stringify({ results, errors, simulatedMedia: true, simulatedAI: true }, null, 2));
  } finally { await browser.close(); server.close(); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
