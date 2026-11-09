/* Independent browser checks for the optional, offline meaning scenes. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const source = fs.readFileSync(path.join(__dirname, 'visual_scenes.js'), 'utf8');
const css = fs.readFileSync(path.join(__dirname, 'visual_scenes.css'), 'utf8');
const app = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
const appStyle = app.match(/<style>([\s\S]*?)<\/style>/)[1];
const html = `<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>${appStyle}\n${css}\n.test-host{max-width:760px;margin:16px auto;padding:0 12px}body{padding:0}</style><body><div class="test-host" id="scene-host"></div><script>${source.replace('const VisualScenes = (() => {', 'const VisualScenes = window.VisualScenes = (() => {')}</script></body></html>`;
const server = http.createServer((req, res) => { res.setHeader('Content-Type', 'text/html; charset=utf-8'); res.end(html); });
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {}) });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  page.setDefaultTimeout(10000);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.route('https://**/*', route => route.abort());
  try {
    await page.goto(`http://127.0.0.1:${server.address().port}/`);
    await page.evaluate(() => {
      window.parentClicks = 0;
      const host = document.getElementById('scene-host');
      host.addEventListener('click', () => window.parentClicks++);
      host.append(VisualScenes.forWord('borrow'), VisualScenes.forWord('lend'), VisualScenes.forGrammar('pp', 1), VisualScenes.forWord('find'));
      if (VisualScenes.forWord('bread') !== null || VisualScenes.create('not-a-scene') !== null) throw new Error('Unexpected scene');
    });
    assert.equal(await page.locator('.vs-scene').count(), 4);
    assert.equal(await page.locator('.vs-drawing').count(), 0); // No scene work before opening.
    const borrow = page.locator('.vs-scene').nth(0);
    await borrow.locator('summary').click();
    await borrow.locator('.vs-drawing').waitFor();
    assert.equal(await borrow.locator('.vs-sentence').textContent(), 'Bora borrows a book from Ada.');
    assert.equal(await borrow.locator('.vs-person.is-active text').textContent(), 'Bora');
    await borrow.getByRole('button', { name: 'lend', exact: true }).click();
    assert.equal(await borrow.locator('.vs-sentence').textContent(), 'Ada lends her book to Bora.');
    assert.equal(await borrow.locator('.vs-person.is-active text').textContent(), 'Ada');
    assert.equal(await borrow.getByRole('button', { name: 'lend', exact: true }).getAttribute('aria-pressed'), 'true');
    assert.equal(await borrow.getByRole('button', { name: 'lend', exact: true }).evaluate(button => button === document.activeElement), true);
    // Native keyboard selection still works; card click-to-learn must not fire.
    await borrow.getByRole('button', { name: 'borrow', exact: true }).focus();
    await page.keyboard.press('Enter');
    assert.equal(await borrow.locator('.vs-sentence').textContent(), 'Bora borrows a book from Ada.');
    assert.equal(await page.evaluate(() => window.parentClicks), 0);

    const positions = page.locator('.vs-scene').nth(2);
    await positions.locator('summary').click();
    for (const key of ['in', 'on', 'under', 'between', 'behind', 'in front of']) {
      await positions.getByRole('button', { name: key, exact: true }).click();
      assert.equal(await positions.locator('.vs-drawing').getAttribute('data-scene-state'), key);
      assert.equal(await positions.locator('.vs-sentence mark').textContent(), key);
      assert.equal(await positions.locator('.vs-drawing').count(), 1);
      assert.equal(await positions.locator('[aria-pressed="true"]').count(), 1);
    }
    assert((await positions.locator('.vs-note').textContent()).includes('önünü'));
    const search = page.locator('.vs-scene').nth(3);
    await search.locator('summary').click();
    assert.equal(await search.locator('.vs-sentence').textContent(), 'Ada has found her key.');
    assert(await search.locator('.vs-key.is-found').isVisible());
    await search.getByRole('button', { name: 'look for', exact: true }).click();
    assert.equal(await search.locator('.vs-sentence').textContent(), 'Ada is looking for her key.');
    assert.equal(await search.locator('.vs-key.is-found').count(), 0);
    assert(await search.locator('.vs-question').isVisible());
    await page.locator('.vs-scene').nth(1).locator('summary').click();
    const duplicateIds = await page.evaluate(() => {
      const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
      return ids.length - new Set(ids).size;
    });
    assert.equal(duplicateIds, 0);
    await page.setViewportSize({ width: 320, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    const sizes = await positions.locator('.vs-choice').evaluateAll(buttons => buttons.map(button => ({ width: button.getBoundingClientRect().width, height: button.getBoundingClientRect().height })));
    assert(sizes.every(size => size.width >= 44 && size.height >= 44));
    if (process.env.VISUAL_SCENES_SCREENSHOT_DIR) await positions.screenshot({ path: path.join(process.env.VISUAL_SCENES_SCREENSHOT_DIR, 'visual-scene-position.png') });
    await page.evaluate(() => document.documentElement.dataset.theme = 'dark');
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await page.evaluate(() => {
      const english = VisualScenes.create('transfer', 'lend', { lang: 'en' });
      document.getElementById('scene-host').append(english);
      english.open = true;
    });
    const english = page.locator('.vs-scene').last();
    await english.locator('.vs-note').waitFor();
    assert((await english.locator('summary').textContent()).startsWith('See the meaning'));
    assert((await english.locator('.vs-note').textContent()).includes('giving the book'));
    await page.evaluate(() => VisualScenes.relabel('en'));
    assert((await borrow.locator('summary').textContent()).startsWith('See the meaning'));
    assert.equal(await borrow.locator('.vs-sentence').textContent(), 'Bora borrows a book from Ada.');
    assert((await borrow.locator('.vs-note').textContent()).includes('receiving the book'));
    assert.deepEqual(errors, []);
    console.log('PASS: lazy scenes, borrow/lend perspective, all six positions, search/result, keyboard/focus, no parent click, unique SVG IDs, 320px layout, dark theme and English copy');
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
