/* Run with node tools/test_novel_reader.cjs. PLAYWRIGHT_MODULE can point to a bundled installation. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const vm = require('node:vm');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
for (const match of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) {
  if (!/\btype=/.test(match[1])) new vm.Script(match[2]);
}
assert(!html.includes('id="novel-tr"'));
const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', req.url.startsWith('/version.json') ? 'application/json' : 'text/html; charset=utf-8');
  // Expose the otherwise private module only in this test server's response.
  res.end(req.url.startsWith('/version.json') ? fs.readFileSync(path.join(__dirname, '../version.json')) : html.replace('const Novel = {', 'const Novel = window.Novel = {'));
});
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {}) });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.setDefaultTimeout(10000);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  let requests = [], failing = false, googleFailing = false;
  const translations = {
    'Dr. Smith took his coat off.': 'Dr. Smith paltosunu çıkardı.',
    'She ate ice cream in front of the post office.': 'Postanenin önünde dondurma yedi.',
    'The well-known visitor smiled.': 'Tanınmış ziyaretçi gülümsedi.',
    'We saw a quokka.': 'Bir kısa kuyruklu kanguru gördük.',
    'She saw a cat near another cat.': 'Bir kedinin yanında başka bir kedi gördü.',
    quokka: 'kısa kuyruklu kanguru',
    'Slow sentence.': 'Yavaş cümle.',
    'Fast sentence.': 'Hızlı cümle.',
    'He took his coat off before leaving.': 'Gitmeden önce paltosunu çıkardı.'
  };
  await page.route('https://**/*', async route => {
    const url = new URL(route.request().url());
    if (!/translate\.googleapis\.com|api\.mymemory\.translated\.net/.test(url.host)) return route.abort();
    const text = url.searchParams.get('q');
    requests.push({ host: url.host, text });
    if (text === 'Slow sentence.') await sleep(180);
    if (failing || (googleFailing && url.host.includes('googleapis'))) return route.fulfill({ status: 503, body: '{}' });
    const tr = translations[text] || 'Deneme çevirisi.';
    return route.fulfill({ json: url.host.includes('mymemory')
      ? { responseStatus: 200, responseData: { translatedText: tr } }
      : [[[tr, text]]] });
  });
  try {
    await page.goto(`http://127.0.0.1:${server.address().port}/#novel`);
    await page.waitForFunction(() => window.__appReady === true);
    // The actual reader, event delegation, dialog and network path are exercised below.
    const open = async paragraphs => page.evaluate(paragraphs => {
      Novel.setBook({ name: 'reader-test.pdf', title: 'Reader test', pages: [paragraphs] }, 0);
    }, paragraphs);
    const click = async word => page.locator('#novel-text .nw').filter({ hasText: new RegExp('^' + word + '$') }).first().click();
    await open(['Dr. Smith took his coat off.', 'She ate ice cream in front of the post office.', 'The well-known visitor smiled.', 'We saw a quokka.']);
    await click('off');
    await page.waitForFunction(() => document.querySelector('#novel-pop-line').textContent === 'Dr. Smith paltosunu çıkardı.');
    assert.equal(await page.locator('#novel-pop-word').textContent(), 'take off');
    assert.equal(await page.locator('#novel-pop-context').textContent(), 'Dr. Smith took his coat off.');
    assert.equal(await page.locator('#novel-pop-tr').textContent(), '(giysi) çıkarmak');
    assert.deepEqual(await page.locator('#novel-pop-context mark').allTextContents(), ['took', 'off']);
    assert.deepEqual(await page.locator('#novel-pop-line mark').allTextContents(), ['çıkardı']);
    assert.deepEqual(await page.locator('#novel-text .nw.is-on').allTextContents(), ['took', 'off']);
    await click('cream');
    assert.equal(await page.locator('#novel-pop-word').textContent(), 'ice cream');
    assert.equal(await page.locator('#novel-pop-tr').textContent(), 'dondurma');
    assert.deepEqual(await page.locator('#novel-pop-context mark').allTextContents(), ['ice cream']);
    await page.waitForFunction(() => document.querySelector('#novel-pop-line mark')?.textContent === 'dondurma');
    await click('front');
    assert.equal(await page.locator('#novel-pop-word').textContent(), 'in front of');
    await click('office');
    assert.equal(await page.locator('#novel-pop-word').textContent(), 'post office');
    assert.deepEqual(await page.locator('#novel-pop-context mark').allTextContents(), ['post office']);
    await page.waitForFunction(() => document.querySelector('#novel-pop-line mark')?.textContent === 'Postanenin');
    assert.equal(await page.locator('#novel-text .nw').filter({ hasText: /^well-known$/ }).count(), 1);
    await click('quokka');
    await page.waitForFunction(() => document.querySelector('#novel-pop-tr').textContent === 'kısa kuyruklu kanguru');
    assert.equal(await page.locator('#novel-pop-line').textContent(), 'Bir kısa kuyruklu kanguru gördük.');
    assert.deepEqual(await page.locator('#novel-pop-context mark').allTextContents(), ['quokka']);
    assert.deepEqual(await page.locator('#novel-pop-line mark').allTextContents(), ['kısa kuyruklu kanguru']);
    assert(await page.locator('#novel-pop-save').isVisible());
    await page.locator('#novel-pop-save').click();
    assert.equal(await page.locator('#novel-pop-save').getAttribute('aria-pressed'), 'true');
    await open(['She saw a cat near another cat.']);
    await page.locator('#novel-text .nw').filter({ hasText: /^cat$/ }).nth(1).click();
    await page.waitForFunction(() => document.querySelector('#novel-pop-line mark')?.textContent === 'kedinin');
    assert.deepEqual(await page.locator('#novel-pop-context mark').allTextContents(), ['cat']);
    assert.equal(await page.locator('#novel-pop-context mark').evaluate(mark => mark.previousSibling.textContent), 'She saw a cat near another ');
    assert.deepEqual(await page.locator('#novel-pop-line mark').allTextContents(), ['kedinin', 'kedi']);
    const marking = await page.evaluate(() => {
      const box = document.createElement('div');
      Novel.highlightText(box, '<b>cat</b>', [{ start: 3, end: 6 }]);
      return {
        literalText: box.textContent, htmlElement: Boolean(box.querySelector('b')), marked: box.querySelector('mark').textContent,
        noun: Novel.senseRanges('kitap', 'Kitaplık kırıldı.'),
        auxiliary: Novel.senseRanges('iptal etmek', 'Toplantıyı iptal etti.').map(range => 'Toplantıyı iptal etti.'.slice(range.start, range.end))
      };
    });
    assert.equal(marking.literalText, '<b>cat</b>');
    assert.equal(marking.htmlElement, false);
    assert.equal(marking.marked, 'cat');
    assert.deepEqual(marking.noun, []);
    assert.deepEqual(marking.auxiliary, ['iptal', 'etti']);
    const pure = await page.evaluate(() => {
      const phrase = (s, word) => {
        const tokens = Novel.phraseTokens(s);
        return Novel.findPhrase(tokens, tokens.findIndex(token => token.text === word))?.phrase || null;
      };
      const text = 'Mr. Smith paid 3.50 dollars. “Really?” she asked. He left.';
      const ranges = Novel.sentenceRanges(text);
      const segmenter = Intl.Segmenter;
      let fallback;
      try { Intl.Segmenter = undefined; fallback = Novel.sentences(text); }
      finally { Intl.Segmenter = segmenter; }
      return {
        ranges, fallback, exact: ranges.every(part => text.slice(part.start, part.start + part.text.length) === part.text),
        split: phrase('She put the phone down.', 'phone'),
        particle: phrase('She put the phone down.', 'down'),
        literal: phrase('She put the cup on the table.', 'put'),
        clause: phrase('She turned and he looked up.', 'turned'),
        punct: phrase('She ate ice, cream and bread.', 'ice'),
        longest: phrase('He ran out of bread.', 'out'),
        chunks: Novel.translationChunks('A long sentence with café and words. '.repeat(80))
      };
    });
    assert(pure.exact);
    assert.equal(pure.ranges[0].text, 'Mr. Smith paid 3.50 dollars.');
    assert.equal(pure.fallback[0], 'Mr. Smith paid 3.50 dollars.');
    assert.equal(pure.split, null); // The object is not part of the phrasal verb.
    assert.equal(pure.particle, 'put down');
    assert.equal(pure.literal, null);
    assert.equal(pure.clause, null);
    assert.equal(pure.punct, null);
    assert.equal(pure.longest, 'run out of');
    assert(pure.chunks.every(chunk => Buffer.byteLength(chunk) <= 480));
    assert.equal(pure.chunks.join(' '), 'A long sentence with café and words. '.repeat(80).trim());
    // A sentence interrupted by a PDF page remains complete from either page.
    await page.evaluate(() => Novel.setBook({ name: 'continued.pdf', pages: [['He took his coat'], ['\u2060off before leaving.']] }, 0));
    await click('took');
    assert.equal(await page.locator('#novel-pop-context').textContent(), 'He took his coat off before leaving.');
    assert.equal(await page.locator('#novel-pop-word').textContent(), 'take off');
    await page.evaluate(() => Novel.go(1));
    await click('off');
    assert.equal(await page.locator('#novel-pop-context').textContent(), 'He took his coat off before leaving.');
    assert.equal(await page.locator('#novel-pop-word').textContent(), 'take off');
    // Fast clicks and closing the card must not let an older response change it.
    await open(['Slow sentence.', 'Fast sentence.']);
    await click('Slow');
    await click('Fast');
    await page.waitForFunction(() => document.querySelector('#novel-pop-line').textContent === 'Hızlı cümle.');
    await sleep(250);
    assert.equal(await page.locator('#novel-pop-line').textContent(), 'Hızlı cümle.');
    assert.deepEqual(await page.locator('#novel-pop-context mark').allTextContents(), ['Fast']);
    assert(!(await page.locator('#novel-pop-line mark').allTextContents()).includes('Yavaş'));
    await page.locator('#novel-pop-close').click();
    assert(await page.locator('#novel-pop').isHidden());
    // In-flight and persistent caching avoid repeat requests.
    const count = requests.length;
    await page.evaluate(() => Promise.all([Novel.translate('cached test'), Novel.translate('cached test')]));
    assert.equal(requests.length - count, 1);
    await page.evaluate(() => Novel.translate('cached test'));
    assert.equal(requests.length - count, 1);
    googleFailing = true;
    assert.equal(await page.evaluate(() => Novel.translate('fallback service test')), 'Deneme çevirisi.');
    assert.equal(requests.at(-1).host, 'api.mymemory.translated.net');
    googleFailing = false;
    // Failure remains visible and retry recovers; no invented word meaning is saved.
    failing = true;
    await open(['The zzzunknown failed.']);
    await click('zzzunknown');
    await page.waitForFunction(() => !document.querySelector('#novel-pop-retry').hidden);
    await page.waitForFunction(() => !document.querySelector('#novel-pop-line').textContent.includes('…'));
    assert.equal(await page.locator('#novel-pop-line mark').count(), 0);
    assert(await page.locator('#novel-pop-line').isVisible());
    assert.deepEqual(await page.locator('#novel-pop-context mark').allTextContents(), ['zzzunknown']);
    assert(await page.locator('#novel-pop-save').isHidden());
    failing = false;
    await page.locator('#novel-pop-retry').click();
    await page.waitForFunction(() => document.querySelector('#novel-pop-line').textContent === 'Deneme çevirisi.');
    // Cached translations remain usable offline; new ones show an explicit error.
    await page.context().setOffline(true);
    await open(['Dr. Smith took his coat off.', 'The uncachedword appeared.']);
    await click('off');
    await page.waitForFunction(() => document.querySelector('#novel-pop-line').textContent === 'Dr. Smith paltosunu çıkardı.');
    await click('uncachedword');
    await page.waitForFunction(() => document.querySelector('#novel-pop-line').textContent.includes('internet'));
    await page.context().setOffline(false);
    // Both source and translated sentence remain visible on a phone.
    await page.setViewportSize({ width: 390, height: 844 });
    await click('off');
    assert(await page.locator('#novel-pop-sentence').isVisible());
    assert(await page.locator('#novel-pop-line').isVisible());
    await page.waitForFunction(() => document.querySelector('#novel-pop-line mark')?.textContent === 'çıkardı');
    assert.deepEqual(await page.locator('#novel-pop-context mark').allTextContents(), ['took', 'off']);
    assert.deepEqual(await page.locator('#novel-pop-line mark').allTextContents(), ['çıkardı']);
    assert.equal(await page.locator('#novel-tr').count(), 0);
    assert(await page.locator('#novel-aa').isVisible());
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    assert.equal(overflow, false);
    if (process.env.NOVEL_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.NOVEL_SCREENSHOT_DIR, 'novel-reader-mobile.png') });
    await sleep(900); // Wait for the app's debounced persistent cache write.
    const cachedCount = requests.length;
    await page.reload();
    await page.waitForFunction(() => window.__appReady === true);
    assert.equal(await page.evaluate(() => Novel.translate('Dr. Smith took his coat off.')), 'Dr. Smith paltosunu çıkardı.');
    assert.equal(requests.length, cachedCount);
    assert.deepEqual(errors, []);
    console.log('PASS: syntax, initialization, word and sentence translations, compounds, phrasal verbs, page continuations, stale responses, cache, failure/retry, offline and mobile layout');
  } catch (error) {
    console.error(await page.evaluate(() => ({ word: document.querySelector('#novel-pop-word')?.textContent, line: document.querySelector('#novel-pop-line')?.textContent, context: document.querySelector('#novel-pop-context')?.textContent, text: document.querySelector('#novel-text')?.textContent })));
    console.error('Requests:', requests);
    throw error;
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
