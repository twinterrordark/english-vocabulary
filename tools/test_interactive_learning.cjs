/* Integration checks against the built app, not isolated widget copies. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/version.json')) { res.setHeader('Content-Type', 'application/json'); res.end(fs.readFileSync(path.join(__dirname, '../version.json'))); return; }
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  let testHtml = html;
  for (const module of ['Novel', 'Review', 'NovelQuickReview']) testHtml = testHtml.replace('const ' + module + ' = {', 'const ' + module + ' = window.' + module + ' = {');
  res.end(testHtml);
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {}) });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, acceptDownloads: true });
  page.setDefaultTimeout(15000);
  const errors = [], network = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.route('https://**/*', route => { network.push(route.request().url()); return route.abort(); });
  const go = async route => { await page.evaluate(route => { location.hash = '#' + route; }, route); };
  const shot = async name => { if (process.env.INTERACTION_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.INTERACTION_SCREENSHOT_DIR, name + '.png') }); };
  try {
    await page.goto(`http://127.0.0.1:${server.address().port}/#grammar/tn/2`);
    await page.waitForFunction(() => window.__appReady === true);
    const originalProgress = await page.evaluate(() => localStorage.getItem('english-study-grammar.v1'));
    for (const index of [2, 5, 8]) {
      await go('grammar/tn/' + index);
      await page.locator('#gram-unit .gtry').waitFor();
      assert.equal(await page.locator('#gram-unit .gtry-body').count(), 0);
      await page.locator('#gram-unit .gtry summary').click();
      await page.locator('#gram-unit .gtry-controls button').first().waitFor();
      const before = await page.locator('.gtry-sentence').textContent();
      await page.locator('.gtry-controls button').last().click();
      assert.notEqual(await page.locator('.gtry-sentence').textContent(), before);
      if (index === 2) { await page.locator('.gtry-output').scrollIntoViewIfNeeded(); await shot('interactive-grammar-mobile'); }
      await page.locator('[data-gtry-quiz]').click();
      await page.locator('.gtry-options button').first().click();
      assert(await page.locator('.gtry-feedback').isVisible());
      await page.getByRole('button', { name: 'Örneklere dön', exact: true }).click();
    }
    assert.equal(await page.evaluate(() => localStorage.getItem('english-study-grammar.v1')), originalProgress);
    await go('grammar/tn/6');
    await page.waitForFunction(() => document.querySelector('#gram-unit h2')?.textContent.includes('Present Perfect ·'));
    assert.equal(await page.locator('#gram-unit .gtry').count(), 0);
    await go('grammar/pp/1');
    await page.locator('#gram-unit .vs-scene').waitFor();
    assert.equal(await page.locator('#gram-unit .vs-scene svg').count(), 0);
    await page.locator('#gram-unit .vs-scene summary').click();
    await page.locator('[data-scene-choice="between"]').click();
    assert((await page.locator('.vs-sentence').textContent()).includes('between'));
    await page.locator('.vs-stage').scrollIntoViewIfNeeded();
    await shot('visual-scene-mobile');
    await go('words');
    await page.locator('#word-search').fill('borrow');
    const card = page.locator('#word-list .word-card').filter({ has: page.locator('.vs-scene[data-visual-scene="transfer"]') }).first();
    await card.waitFor();
    assert.equal(await card.locator('.media-toggle').getAttribute('aria-pressed'), 'false');
    await card.locator('.vs-scene summary').click();
    await card.locator('[data-scene-choice="lend"]').click();
    assert((await card.locator('.vs-sentence').textContent()).includes('Ada lends'));
    assert.equal(await card.locator('.media-toggle').getAttribute('aria-pressed'), 'false');
    // Save actual reader selections, including an irregular verb and a split phrase.
    await go('novel');
    const book = { name: 'interaction-test.pdf', pages: [['Dr. Smith took his coat off.', 'She ate ice cream.', 'They went home before sunset.'], ['She found a key.']] };
    const openBook = async name => page.evaluate(({ book, name }) => {
      for (const sentence of book.pages.flat()) Novel.remember(sentence, 'Örnek cümlenin çevirisi.');
      Novel.setBook({ ...book, name: name || book.name }, 0);
    }, { book, name });
    await openBook();
    const articleText = await page.locator('#novel-text').textContent();
    for (const word of ['off', 'cream', 'went']) {
      await page.locator('#novel-text .nw').filter({ hasText: new RegExp('^' + word + '$') }).first().click();
      await page.locator('#novel-pop-save').click();
      assert(await page.locator('.novel-quick-review').isVisible());
      assert.equal(await page.locator('.nqr-form').count(), 0);
    }
    const meta = await page.evaluate(() => NovelQuickReview.snapshot());
    assert.equal(meta.length, 3);
    assert.deepEqual(meta[0].ranges.map(range => meta[0].sentence.slice(range.start, range.end)), ['took', 'off']);
    assert.deepEqual(meta[2].ranges.map(range => meta[2].sentence.slice(range.start, range.end)), ['went']);
    assert.equal(await page.locator('#novel-text').textContent(), articleText);
    assert.equal(await page.locator('#novel-text .novel-quick-review').count(), 0);
    const reviewBefore = await page.evaluate(() => JSON.stringify(Review.state));
    await page.getByRole('button', { name: 'Kısa tekrar yap', exact: true }).click();
    assert(await page.locator('#novel-pop').isHidden());
    assert((await page.locator('.nqr-sentence').textContent()).includes('_____'));
    await page.locator('#nqr-answer').press('Enter');
    assert((await page.locator('.nqr-feedback').textContent()).includes('Önce bir cevap'));
    await page.locator('#nqr-answer').fill('take off'); // Canonical form is wrong in this past-tense sentence.
    await page.locator('#nqr-answer').press('Enter');
    assert.deepEqual(await page.locator('.nqr-model mark').allTextContents(), ['took', 'off']);
    await shot('novel-quick-review-mobile');
    await page.getByRole('button', { name: 'Sonraki', exact: true }).click();
    for (const answer of ['ice cream', 'went']) {
      await page.locator('#nqr-answer').fill(answer);
      await page.locator('#nqr-answer').press('Enter');
      assert(await page.locator('.nqr-feedback.is-correct').isVisible());
      await page.locator('.nqr-model').locator('..').getByRole('button').click();
    }
    assert((await page.locator('.nqr-result').textContent()).includes('3 sorudan 2'));
    assert.equal(await page.evaluate(() => JSON.stringify(Review.state)), reviewBefore);
    await page.evaluate(() => Novel.go(1));
    assert(await page.locator('.novel-quick-review').isHidden());
    await openBook('other-book.pdf');
    assert(await page.locator('.novel-quick-review').isHidden());
    await page.evaluate(() => Novel.setBook({ name: 'interaction-test.pdf', pages: [['This replacement document contains entirely different sentences.']] }, 0));
    assert(await page.locator('.novel-quick-review').isHidden());
    await openBook();
    assert(await page.locator('.novel-quick-review').isVisible());
    // The association data is included in the existing export, and restores after reload.
    await go('settings');
    const downloading = page.waitForEvent('download');
    await page.locator('#export-progress').click();
    const download = await downloading;
    const exported = JSON.parse(fs.readFileSync(await download.path(), 'utf8'));
    assert.equal(exported.novelQuick.length, 3);
    await page.evaluate(() => NovelQuickReview.clear());
    await page.locator('#import-file').setInputFiles({ name: 'progress.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(exported)) });
    await page.locator('#confirm-ok').click();
    await page.waitForFunction(() => NovelQuickReview.snapshot().length === 3);
    assert.equal(await page.evaluate(() => Review.has('n:take off') && Review.has('n:ice cream')), true);
    const oldBackup = { ...exported };
    delete oldBackup.novelQuick;
    await page.locator('#import-file').setInputFiles({ name: 'old-progress.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(oldBackup)) });
    await page.locator('#confirm-ok').click();
    assert.equal(await page.evaluate(() => NovelQuickReview.snapshot().length), 3);
    await page.reload();
    await page.waitForFunction(() => window.__appReady === true);
    await go('novel');
    await openBook();
    assert(await page.locator('.novel-quick-review').isVisible());
    assert.equal(await page.evaluate(() => NovelQuickReview.snapshot().length), 3);
    await page.locator('#novel-text .nw').filter({ hasText: /^off$/ }).click();
    await page.locator('#novel-pop-save').click();
    assert.equal(await page.evaluate(() => NovelQuickReview.snapshot().length), 2);
    await go('settings');
    await page.locator('#ui-lang').selectOption('en');
    await go('novel');
    assert(await page.getByRole('button', { name: 'Quick review', exact: true }).isVisible());
    await page.setViewportSize({ width: 320, height: 740 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await page.context().setOffline(true);
    await page.getByRole('button', { name: 'Quick review', exact: true }).click();
    assert(await page.locator('#nqr-answer').isVisible());
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await page.context().setOffline(false);
    await go('settings');
    await page.locator('#reset-progress').click();
    await page.locator('#confirm-ok').click();
    assert.equal(await page.evaluate(() => NovelQuickReview.snapshot().length), 0);
    assert.deepEqual(errors, []);
    assert.deepEqual(network, []);
    console.log('PASS: real app integration, optional/lazy widgets, word-card isolation, precise saved ranges, source-only TTS, page/book boundaries, surface forms, export/persistence, language, offline and mobile');
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
