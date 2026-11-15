/* Two real browsers exercise the frontend against local Wrangler + D1.
   Translation is stubbed; note reads/writes are genuine HTTP API requests.
   Start the local notes worker on 8797 before running this test. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const { chromium } = require('../.audit-deps/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const api = process.env.NOTES_TEST_URL || 'http://127.0.0.1:8797';
assert(/^http:\/\/(?:127\.0\.0\.1|localhost):\d+$/.test(api), 'Only a local API is allowed');
let served = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
assert(served.includes('const NovelNotes = {'), 'Build the notes module first');
served = served.replace(/(const NovelNotes = \{[\s\S]*?API: )'[^']*',/, (_, prefix) => prefix + JSON.stringify(api) + ',')
  .replace('const NovelNotes = {', 'const NovelNotes = window.NovelNotes = {')
  .replace('const Novel = {', 'const Novel = window.Novel = {');
assert(served.includes('API: ' + JSON.stringify(api)), 'Test-only API endpoint must be injected');
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/favicon.ico')) { res.writeHead(204); res.end(); return; }
  res.setHeader('Content-Type', req.url.startsWith('/version.json') ? 'application/json' : 'text/html; charset=utf-8');
  res.end(req.url.startsWith('/version.json') ? fs.readFileSync(path.join(root, 'version.json')) : served);
});
(async () => {
  const health = await fetch(api + '/health'); assert.equal(health.status, 200, 'Local notes API must be running');
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const contexts = [], errors = [], requests = [], results = [];
  const marker = 'Edition ' + crypto.randomBytes(10).toString('hex') + '.';
  const pages = [['She took her coat off. The visitor smiled.', marker]];
  const base = `http://127.0.0.1:${server.address().port}/#novel`;
  const pass = name => { results.push(name); console.log('PASS', name); };
  const createReader = async (name, ip) => {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' }); contexts.push(context);
    await context.route(api + '/**', route => {
      requests.push({ method: route.request().method(), url: route.request().url() });
      return route.continue({ headers: { ...route.request().headers(), 'CF-Connecting-IP': ip } });
    });
    await context.route('https://**/*', route => {
      const url = new URL(route.request().url());
      if (/translate\.googleapis\.com|api\.mymemory\.translated\.net/.test(url.host)) {
        const text = url.searchParams.get('q') || '';
        const tr = text.includes('coat') ? 'Paltosunu çıkardı.' : 'Ziyaretçi gülümsedi.';
        return route.fulfill({ json: url.host.includes('mymemory') ? { responseStatus: 200, responseData: { translatedText: tr } } : [[[tr, text]]] });
      }
      return route.abort();
    });
    const page = await context.newPage(); page.setDefaultTimeout(12000);
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base); await page.waitForFunction(() => window.__appReady === true);
    await page.evaluate(({ name, pages }) => Novel.setBook({ name, title: name, pages }, 0), { name, pages });
    await page.waitForFunction(() => NovelNotes.bookKey && NovelNotes.indexLoading !== NovelNotes.bookKey);
    return page;
  };
  const openWord = async (page, word = 'off') => {
    const responsePromise = page.waitForResponse(response => response.url().startsWith(api + '/api/notes?') && response.request().method() === 'GET').catch(error => error);
    await page.locator('#novel-text .nw').filter({ hasText: new RegExp('^' + word + '$') }).first().click();
    await page.locator('#novel-note-body').waitFor({ state: 'attached' });
    if (!(await page.locator('#novel-notes').evaluate(el => el.open))) await page.locator('#novel-notes > summary').click();
    await page.locator('#novel-note-body').waitFor({ state: 'visible' });
    const response = await responsePromise;
    if (response instanceof Error) throw response;
    assert.equal(response.status(), 200);
    const result = await response.json();
    await page.waitForFunction(count => document.querySelectorAll('#novel-notes .novel-notes-list > li').length === count && (count > 0 || document.querySelector('#novel-notes [role="status"]')?.textContent.includes('henüz ortak not yok')), result.notes.length);
  };
  const post = async (page, author, body) => {
    await page.locator('#novel-note-author').fill(author); await page.locator('#novel-note-body').fill(body);
    await page.getByRole('button', { name: 'Notu paylaş', exact: true }).click();
    await page.waitForFunction(body => [...document.querySelectorAll('.novel-notes-list > li > p')].some(el => el.textContent === body), body);
  };
  const refresh = page => page.evaluate(() => NovelNotes.refresh());
  const close = async page => { if (await page.locator('#novel-pop').isVisible()) await page.locator('#novel-pop-close').click(); };
  try {
    const ipPart = crypto.randomInt(1, 250);
    const a = await createReader('same-story-A.pdf', '198.51.100.' + ipPart);
    const b = await createReader('renamed-story-B.pdf', '198.51.101.' + ipPart);
    assert.equal(await a.evaluate(() => NovelNotes.bookKey), await b.evaluate(() => NovelNotes.bookKey));
    const aToken = await a.evaluate(() => NovelNotes.identity.token), bToken = await b.evaluate(() => NovelNotes.identity.token);
    assert.notEqual(aToken, bToken);
    await openWord(a); assert.equal(await a.locator('#novel-pop-word').innerText(), 'take off');
    const first = 'Burada take off, paltosunu çıkarmak anlamında kullanılmış.';
    await post(a, 'Okur A', first);
    assert.equal(await a.locator('.novel-notes-list > li').count(), 1);
    const firstId = await a.locator('.novel-notes-list > li').getAttribute('data-note-id');
    await close(a); await refresh(b);
    assert(await b.locator('#novel-text .nw.has-public-note').filter({ hasText: /^off$/ }).count());
    await b.locator('#novel-tr').click();
    await b.locator('#novel-text .novel-pair').first().waitFor({ state: 'visible' });
    assert(await b.locator('#novel-text .nw.has-public-note').filter({ hasText: /^off$/ }).count());
    await openWord(b);
    assert.equal(await b.locator('.novel-notes-list > li > p').innerText(), first);
    assert.equal(await b.getByRole('button', { name: 'Düzenle', exact: true }).count(), 0);
    assert.equal(await b.getByRole('button', { name: 'Sil', exact: true }).count(), 0);
    const out = path.join(root, 'audits/2026-11-15'); fs.mkdirSync(out, { recursive: true });
    await b.screenshot({ path: path.join(out, 'notes-390.png') });
    pass('Different devices with renamed copies share the same content index, phrase highlight and public note; ownership controls stay private');
    const literal = '<img src=x onerror="window.__notesXss=true"><script>window.__notesXss=true</script>';
    await post(b, 'Okur B', literal);
    const secondId = await b.locator('.novel-notes-list > li').filter({ hasText: literal }).getAttribute('data-note-id');
    assert.equal(await b.locator('.novel-notes-list img, .novel-notes-list script').count(), 0);
    assert.equal(await b.evaluate(() => window.__notesXss), undefined);
    await refresh(a); await openWord(a);
    assert.equal(await a.locator('.novel-notes-list > li').count(), 2);
    const firstRow = a.locator('.novel-notes-list > li[data-note-id="' + firstId + '"]');
    const secondRow = a.locator('.novel-notes-list > li[data-note-id="' + secondId + '"]');
    assert.equal(await secondRow.getByRole('button').count(), 0);
    await firstRow.getByRole('button', { name: 'Düzenle', exact: true }).click();
    const edited = 'Güncellenmiş not: bu cümlede giysiyi çıkarmak anlamında.';
    await a.locator('#novel-note-body').fill(edited); await a.getByRole('button', { name: 'Değişikliği kaydet', exact: true }).click();
    await a.waitForFunction(edited => [...document.querySelectorAll('.novel-notes-list > li > p')].some(el => el.textContent === edited), edited);
    await refresh(b); await b.waitForFunction(edited => [...document.querySelectorAll('.novel-notes-list > li > p')].some(el => el.textContent === edited), edited);
    assert.equal(await b.locator('.novel-notes-list > li').count(), 2);
    pass('A second reader can add literal HTML text safely; each author can edit only their own note and changes reach other readers');
    let delayNext = true, release, started;
    const delayed = new Promise(resolve => { started = resolve; });
    const pattern = api + '/api/notes?**';
    await b.route(pattern, async route => {
      if (delayNext && new URL(route.request().url()).searchParams.get('word') === 'take off') {
        delayNext = false; const response = await route.fetch(); started();
        await new Promise(resolve => { release = resolve; }); await route.fulfill({ response });
      } else await route.continue();
    });
    await close(b); await b.locator('#novel-text .nw').filter({ hasText: /^off$/ }).click(); await delayed;
    await close(b); await openWord(b, 'visitor'); assert.equal(await b.locator('.novel-notes-list > li').count(), 0);
    const oldResponse = b.waitForResponse(response => response.url().startsWith(api + '/api/notes?') && new URL(response.url()).searchParams.get('word') === 'take off');
    release(); await (await oldResponse).finished(); await b.waitForTimeout(100);
    assert.equal(await b.locator('#novel-pop-word').innerText(), 'visitor');
    assert.equal(await b.locator('.novel-notes-list > li').count(), 0);
    await b.unroute(pattern); await close(b); await openWord(b);
    pass('TR layout preserves public phrase highlights; delayed notes for a previous word never replace the selected word');
    await b.screenshot({ path: path.join(out, 'notes-literal-security-390.png') });
    await firstRow.getByRole('button', { name: 'Sil', exact: true }).click(); await a.locator('#confirm-ok').click();
    await a.waitForFunction(id => !document.querySelector('[data-note-id="' + id + '"]'), firstId);
    await refresh(b); await b.waitForFunction(() => document.querySelectorAll('.novel-notes-list > li').length === 1);
    assert.equal(await b.locator('.novel-notes-list > li').getAttribute('data-note-id'), secondId);
    await close(b); assert(await b.locator('#novel-text .nw.has-public-note').filter({ hasText: /^off$/ }).count()); await openWord(b);
    await b.locator('.novel-notes-list > li').getByRole('button', { name: 'Sil', exact: true }).click(); await b.locator('#confirm-ok').click();
    await b.waitForFunction(() => document.querySelectorAll('.novel-notes-list > li').length === 0); await close(b); await refresh(a); await close(a);
    assert.equal(await a.locator('#novel-text .nw.has-public-note').count(), 0);
    assert.equal(await b.locator('#novel-text .nw.has-public-note').count(), 0);
    pass('Deletion removes only the owned note; highlight remains while another note exists and clears after the final note is deleted');
    await openWord(a, 'visitor'); await contexts[0].setOffline(true);
    const draft = 'Bağlantı gelince paylaşacağım, şu anda yalnızca yerel taslak.';
    await a.locator('#novel-note-body').fill(draft); await a.getByRole('button', { name: 'Notu paylaş', exact: true }).click();
    await a.waitForFunction(() => document.querySelector('#novel-notes [role="status"]').textContent.includes('henüz paylaşılmadı'));
    assert.equal(await a.locator('.novel-notes-list > li').count(), 0);
    await contexts[0].setOffline(false); await a.reload(); await a.waitForFunction(() => window.__appReady === true);
    await a.evaluate(({ pages }) => Novel.setBook({ name: 'same-story-A.pdf', title: 'Same story', pages }, 0), { pages });
    await a.waitForFunction(() => NovelNotes.bookKey && NovelNotes.indexLoading !== NovelNotes.bookKey); await openWord(a, 'visitor');
    assert.equal(await a.locator('#novel-note-body').inputValue(), draft);
    assert.equal(await a.locator('.novel-notes-list > li').count(), 0);
    assert.equal(await a.locator('#novel-text .nw.has-public-note').count(), 0);
    pass('Offline submit is explicitly unshared; the local draft survives reload without fabricating notes or highlights');
    for (const page of [a, b]) { await page.setViewportSize({ width: 320, height: 740 }); assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)); }
    assert.deepEqual(errors, []);
    pass('No uncaught JavaScript errors; notes fit 320px screens');
    fs.writeFileSync(path.join(out, 'novel-notes-checks.json'), JSON.stringify({ realLocalWorker: true, realD1: true, separateContexts: true, mockedTranslation: true, successfulWrites: 5, results, errors, apiRequests: requests.length }, null, 2) + '\n');
  } finally { await Promise.all(contexts.map(context => context.close())); await browser.close(); server.close(); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
