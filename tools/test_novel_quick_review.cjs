/* Isolated integration tests; run with PLAYWRIGHT_MODULE/PLAYWRIGHT_CHANNEL if needed. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const source = fs.readFileSync(path.join(__dirname, 'novel_quick_review.js'), 'utf8');
const css = fs.readFileSync(path.join(__dirname, 'novel_quick_review.css'), 'utf8');
new vm.Script(source);
(async () => {
  const browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {}) });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  let networkCalls = 0;
  await page.route('**/*', route => { networkCalls++; return route.abort(); });
  try {
    await page.setContent('<style>:root {--line:#ddd;--surface:#fff;--surface-2:#f5f5f5;--text:#17202c;--muted:#526070;--font:Arial,sans-serif;--primary:#087658;--on-primary:#fff;--focus:#845cff;--primary-soft:#def7ed;--accent-text:#065d46}body{margin:16px}</style><article id="reader"><p>Original book text.</p></article>');
    await page.addStyleTag({ content: css });
    await page.addScriptTag({ content: source + '\nwindow.NQR = NovelQuickReview;' });
    await page.evaluate(() => {
      window.quickStore = new Map();
      window.reviewCards = new Set();
      window.openCount = 0;
      window.quickOptions = { article: document.querySelector('#reader'),
        store: { read: key => quickStore.get(key) || null, write: (key, value) => quickStore.set(key, value) },
        isSaved: id => reviewCards.has(id), language: () => 'tr', onOpen: () => openCount++ };
      NQR.init(quickOptions);
      NQR.onPage({ book: 'book-a', page: 1 });
    });
    assert(await page.locator('.novel-quick-review').isHidden());
    await page.evaluate(() => {
      const save = (book, page, id, word, meaning, sentence, terms) => {
        let from = 0;
        const ranges = terms.map(term => { const start = sentence.indexOf(term, from); from = start + term.length; return { start, end: from }; });
        reviewCards.add(id);
        NQR.saved({ book, page, id, word, meaning, sentence, ranges }, true);
      };
      save('book-a', 1, 'n:take off', 'take off', '(giysi) çıkarmak', 'She took her coat off before leaving.', ['took', 'off']);
      save('book-a', 1, 'n:go', 'go', 'gitmek', 'He went home after the meeting.', ['went']);
      const sentence = 'The cat watched another cat from the window.';
      const start = sentence.indexOf('cat', sentence.indexOf('cat') + 3);
      reviewCards.add('n:cat');
      NQR.saved({ book: 'book-a', page: 1, id: 'n:cat', word: 'cat', meaning: 'kedi', sentence, ranges: [{ start, end: start + 3 }] }, true);
      save('book-b', 1, 'n:walk', 'walk', 'yürümek', 'They walked along the river yesterday.', ['walked']);
      save('book-a', 2, 'n:read', 'read', 'okumak', 'I read a book before dinner.', ['read']);
      NQR.saved({ book: 'book-a', page: 1, id: 'n:bad', word: 'bad', meaning: 'eksik', sentence: 'A chapter without punctuation', ranges: [{ start: 2, end: 9 }] }, true);
      NQR.saved({ book: 'book-a', page: 1, id: 'n:partial', word: 'partial', meaning: 'eksik', sentence: 'The cat watched another cat.', ranges: [{ start: 4, end: 6 }] }, true);
      NQR.saved({ book: 'book-a', page: 1, id: 'n:null', word: 'null', meaning: 'eksik', sentence: 'This is a complete sentence.', ranges: [null] }, true);
      window.savedBeforeQuickReview = JSON.stringify([...reviewCards]);
    });
    assert.equal(await page.evaluate(() => NQR.records.length), 5);
    assert.equal(await page.locator('.nqr-form').count(), 0); // Never opens while saving/reading.
    assert((await page.locator('.nqr-launch-copy').textContent()).includes('3 kayıtlı'));
    assert.equal(await page.locator('#reader p').count(), 1); // Not included in reader TTS.
    await page.getByRole('button', { name: 'Kısa tekrar yap', exact: true }).click();
    assert.equal(await page.evaluate(() => openCount), 1);
    assert.equal(await page.locator('#nqr-sentence').textContent(), 'She _____ her coat _____ before leaving.');
    await page.getByRole('button', { name: 'Kontrol et', exact: true }).click();
    assert((await page.locator('.nqr-feedback').textContent()).includes('Önce bir cevap'));
    assert.equal(await page.evaluate(() => NQR.session.answered), false);
    await page.locator('#nqr-answer').fill('take off');
    await page.locator('#nqr-answer').press('Enter');
    assert.equal(await page.evaluate(() => NQR.session.correct), 0); // Canonical form is not the sentence's past form.
    assert.deepEqual(await page.locator('.nqr-model mark').allTextContents(), ['took', 'off']);
    await page.getByRole('button', { name: 'Sonraki', exact: true }).click();
    await page.locator('#nqr-answer').fill('went');
    await page.locator('#nqr-answer').press('Enter');
    assert.equal(await page.evaluate(() => NQR.session.correct), 1);
    await page.getByRole('button', { name: 'Sonraki', exact: true }).click();
    assert.equal(await page.locator('#nqr-sentence').textContent(), 'The cat watched another _____ from the window.');
    await page.locator('#nqr-answer').fill('CAT');
    await page.getByRole('button', { name: 'Kontrol et', exact: true }).click();
    await page.getByRole('button', { name: 'Bitir', exact: true }).click();
    assert((await page.locator('.nqr-result').textContent()).includes('3 sorudan 2'));
    assert.equal(await page.evaluate(() => JSON.stringify([...reviewCards]) === savedBeforeQuickReview), true);
    assert.deepEqual(await page.evaluate(() => [...quickStore.keys()]), ['english-study-novel-quick.v1']);
    await page.getByRole('button', { name: 'Okumaya dön', exact: true }).click();
    assert.equal(await page.locator('.nqr-form').count(), 0);
    await page.evaluate(() => NQR.onPage({ book: 'book-b', page: 1 }));
    assert((await page.locator('.nqr-launch-copy').textContent()).includes('1 kayıtlı'));
    await page.getByRole('button', { name: 'Kısa tekrar yap', exact: true }).click();
    await page.getByRole('button', { name: 'Cevabı göster', exact: true }).click();
    assert.equal(await page.evaluate(() => NQR.session.correct), 0);
    assert.deepEqual(await page.locator('.nqr-model mark').allTextContents(), ['walked']);
    await page.evaluate(() => { NQR.init(quickOptions); NQR.onPage({ book: 'book-a', page: 1 }); });
    assert.equal(await page.evaluate(() => NQR.eligible().length), 3); // Metadata survives reinitialization.
    const exported = await page.evaluate(() => {
      window.validQuickSnapshot = NQR.snapshot();
      const detached = NQR.snapshot();
      detached[0].ranges[0].start = 999;
      return { count: validQuickSnapshot.length, detached: NQR.records[0].ranges[0].start !== 999 };
    });
    assert.deepEqual(exported, { count: 5, detached: true });
    await page.evaluate(() => NQR.clear());
    assert(await page.locator('.novel-quick-review').isHidden());
    assert.equal(await page.evaluate(() => quickStore.get(NQR.KEY)), '[]');
    await page.evaluate(() => NQR.restore([null, { broken: true }, ...validQuickSnapshot, validQuickSnapshot[0]]));
    assert.equal(await page.evaluate(() => NQR.records.length), 5); // Invalid and duplicate import rows are removed.
    assert.equal(await page.evaluate(() => NQR.eligible().length), 3);
    assert.equal(await page.evaluate(() => NQR.sanitize(Array.from({ length: 300 }, (_, i) => ({ ...validQuickSnapshot[0], page: i }))).length), 240);
    await page.evaluate(() => { NQR.restore({ invalid: true }); });
    assert.equal(await page.evaluate(() => NQR.records.length), 0);
    await page.evaluate(() => NQR.restore(validQuickSnapshot));
    await page.evaluate(() => { reviewCards.delete('n:go'); NQR.saved({ id: 'n:go' }, false); });
    assert.equal(await page.evaluate(() => NQR.eligible().length), 2);
    await page.setViewportSize({ width: 320, height: 720 });
    await page.getByRole('button', { name: 'Kısa tekrar yap', exact: true }).click();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await page.evaluate(() => { quickStore.set(NQR.KEY, '{broken'); NQR.init(quickOptions); });
    assert(await page.locator('.novel-quick-review').isHidden());
    assert.equal(networkCalls, 0);
    assert.deepEqual(errors, []);
    console.log('PASS: page/book isolation, explicit start, exact split phrases and inflections, repeated-token offsets, feedback/reveal, persistence, snapshot/import/reset, removals, malformed data, mobile, no network and unchanged review state');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
