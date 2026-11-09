/* Standalone behavior checks: node tools/test_grammar_try.cjs */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const vm = require('node:vm');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const source = fs.readFileSync(path.join(__dirname, 'grammar_try.js'), 'utf8');
const css = fs.readFileSync(path.join(__dirname, 'grammar_try.css'), 'utf8');
new vm.Script(source);
const helper = `function h(tag, attrs, ...children) {
  const node=document.createElement(tag);
  for(const [key,value] of Object.entries(attrs||{})) {
    if(value==null||value===false)continue;
    if(key==='text')node.textContent=value;
    else node.setAttribute(key,value===true?'':String(value));
  }
  for(const child of children.flat())if(child!=null&&child!==false)node.append(child instanceof Node?child:String(child));
  return node;
}`;
const html = `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>
:root { --line:#d5d9e1;--radius:12px;--space-4:16px;--surface:#fff;--surface-2:#f5f7fa;--text:#17212f;--muted:#526072;--primary:#067052;--on-primary:#fff;--primary-soft:#d6f8ed;--accent-text:#005942;--success-soft:#d6f8ed;--success:#005942;--error-soft:#ffe8e8;--error:#971f2d; }
body { font-family:system-ui; margin:8px; } main { max-width:760px; margin:auto; }
${css}</style><main></main><script>${helper}\n${source}\nwindow.GrammarTry=GrammarTry;</script></html>`;
const expected = [
  { index: 2, answer: 1, first: 'She reads every evening.', second: 'She is reading now.' },
  { index: 5, answer: 1, first: 'I read the report last night.', second: 'I was reading the report at nine last night.' },
  { index: 8, answer: 0, first: 'I lost my key yesterday.', second: "I have lost my key, so I can't open the door." }
];
const server = http.createServer((req, res) => { res.setHeader('Content-Type', 'text/html; charset=utf-8'); res.end(html); });
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  try {
    browser = await chromium.launch({ headless:true, ...(process.env.PLAYWRIGHT_CHANNEL ? { channel:process.env.PLAYWRIGHT_CHANNEL } : {}) });
    const page = await browser.newPage({ viewport:{ width:736, height:900 } });
    page.setDefaultTimeout(10000);
    const errors=[], external=[];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => { if(request.url().startsWith('https:'))external.push(request.url()); });
    await page.goto(`http://127.0.0.1:${server.address().port}/`);
    assert.equal(await page.evaluate(() => GrammarTry.create('tn',6)), null);
    assert.equal(await page.evaluate(() => GrammarTry.create('pp',1)), null);
    for(const lesson of expected) {
      await page.evaluate(index => document.querySelector('main').replaceChildren(GrammarTry.create('tn',index)), lesson.index);
      assert.equal(await page.locator('.gtry').getAttribute('lang'), 'tr');
      assert.equal(await page.locator('.gtry-body').count(),0);
      await page.locator('.gtry summary').focus();
      await page.locator('.gtry summary').press('Enter');
      await page.locator('.gtry-body').waitFor();
      assert.equal(await page.locator('.gtry-sentence').textContent(),lesson.first);
      assert.equal(await page.locator('[data-state="0"]').getAttribute('aria-pressed'),'true');
      await page.locator('[data-state="1"]').click();
      assert.equal(await page.locator('.gtry-sentence').textContent(),lesson.second);
      assert.equal(await page.locator('[data-state="1"]').getAttribute('aria-pressed'),'true');
      assert((await page.locator('.gtry-timeline').getAttribute('aria-label')).length>30);
      await page.locator('[data-gtry-quiz]').click();
      assert.equal(await page.locator('.gtry-body h3').evaluate(node => node===document.activeElement),true);
      await page.locator('[data-answer="'+(1-lesson.answer)+'"]').click();
      assert(await page.locator('.gtry-feedback.is-wrong').isVisible());
      assert.equal(await page.locator('.gtry-feedback').evaluate(node => node===document.activeElement),true);
      assert.equal(await page.locator('.gtry-options button:disabled').count(),2);
      await page.getByRole('button',{name:'Örneklere dön',exact:true}).click();
      assert.equal(await page.locator('.gtry-sentence').textContent(),lesson.second);
      await page.locator('[data-gtry-quiz]').click();
      await page.locator('[data-answer="'+lesson.answer+'"]').click();
      assert(await page.locator('.gtry-feedback.is-right').isVisible());
      assert((await page.locator('.gtry-feedback').textContent()).startsWith('Doğru. '));
      await page.getByRole('button',{name:'Örneklere dön',exact:true}).click();
      await page.locator('.gtry summary').click();
      await page.locator('.gtry summary').click();
      assert.equal(await page.locator('.gtry-sentence').textContent(),lesson.second);
      await page.setViewportSize({width:320,height:844});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth>innerWidth),false);
      await page.locator('[data-gtry-quiz]').click();
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth>innerWidth),false);
      await page.setViewportSize({width:736,height:900});
    }
    assert.equal(await page.evaluate(() => localStorage.length),0);
    assert.deepEqual(external,[]);
    assert.deepEqual(errors,[]);
    console.log('PASS: three authored pairs, lazy disclosure, keyboard focus, preserved exploration state, correct/incorrect feedback, 320px layout and no network/storage side effects');
  } finally {
    if(browser)await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode=1; });
