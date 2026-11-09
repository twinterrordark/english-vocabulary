const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const { chromium } = require('../.audit-deps/node_modules/playwright');
const { default:AxeBuilder } = require('../.audit-deps/node_modules/@axe-core/playwright');
const root = path.resolve(__dirname,'..');
const out = path.join(root,'audits','2026-11-09','after');
fs.mkdirSync(out,{recursive:true});
const server = http.createServer((req,res)=>{
  if(req.url.startsWith('/favicon.ico')){res.writeHead(204);res.end();return;}
  const file=req.url.startsWith('/version.json')?'version.json':'index.html';
  res.setHeader('Content-Type',file.endsWith('.json')?'application/json':'text/html; charset=utf-8');
  const content=fs.readFileSync(path.join(root,file),'utf8');
  res.end(file==='index.html'?content.replace('const Pron = {','const Pron = window.__auditPron = {'):content);
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const context=await browser.newContext({viewport:{width:320,height:720},reducedMotion:'reduce'});
  const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('https://**/*',route=>route.abort());
  const base=`http://127.0.0.1:${server.address().port}/`;
  const results=[];
  const record=(name,detail)=>{results.push({name,detail});console.log('PASS',name,detail||'');};
  const go=async route=>{await page.evaluate(route=>{location.hash=route;},route);await page.waitForFunction(route=>document.querySelector(`.view[data-view="${route.split('/')[0]}"]`)?.classList.contains('is-active'),route);};
  const search=async query=>{
    await page.locator('#word-search').fill(query);
    await page.waitForFunction(query=>{const cards=[...document.querySelectorAll('#word-list .word-card')];return query==='zzznomatchzzz'?!document.querySelector('#word-empty').hidden:cards.length>0&&cards.every(el=>el.textContent.toLowerCase().includes(query.toLowerCase()));},query);
  };
  try{
    await page.goto(base);await page.waitForFunction(()=>window.__appReady===true);
    const initial=await page.evaluate(()=>({nodes:document.querySelectorAll('*').length,cards:document.querySelectorAll('#word-list .word-card').length,words:EnglishStudyDiagnostics.words}));
    assert(initial.nodes<8000);assert.equal(initial.cards,0);assert.equal(initial.words,2199);record('Bounded live DOM; all vocabulary retained',initial);
    for(const lang of ['tr','en']){
      await go('settings');await page.locator('#ui-lang').selectOption(lang);await go('home');
      assert(await page.locator('#nav-more').textContent().then(s=>s.includes(lang==='tr'?'Menü':'Menu')));
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      await page.locator('#nav-more').click();
      assert(await page.locator('#more-sheet').evaluate(el=>el.open&&el.matches(':modal')));
      assert(await page.evaluate(()=>getComputedStyle(document.documentElement).overflow==='hidden'));
      for(let i=0;i<18;i++){await page.keyboard.press('Tab');assert(await page.locator('#more-sheet').evaluate(el=>el.contains(document.activeElement)));}
      await page.keyboard.press('Escape');assert(await page.locator('#more-sheet').isHidden());assert(await page.locator('#nav-more').evaluate(el=>el===document.activeElement));
      await page.locator('#nav-more').click();await page.locator('#more-sheet button[data-close]').click();assert(await page.locator('#nav-more').evaluate(el=>el===document.activeElement));
      record('Menu discovery, focus containment, Escape, close and focus return',lang);
    }
    await page.screenshot({path:path.join(out,'home-320.png')});
    await page.locator('#nav-more').focus();await page.evaluate(()=>window.__auditPron.open('This is a short sentence.'));
    assert(await page.locator('#pron-sheet').evaluate(el=>el.matches(':modal')));
    for(let i=0;i<12;i++){await page.keyboard.press('Tab');assert(await page.locator('#pron-sheet').evaluate(el=>el.contains(document.activeElement)));}
    await page.keyboard.press('Escape');assert(await page.locator('#pron-sheet').isHidden());assert(await page.locator('#nav-more').evaluate(el=>el===document.activeElement));record('Pronunciation sheet focus containment, Escape and focus return');
    await go('words');await search('borrow');
    const card=page.locator('#word-list .word-card').first();
    const id=await card.getAttribute('data-id');const img=await card.locator('img').first().getAttribute('src');
    await card.locator('.media-toggle').click();assert.equal(await card.locator('.media-toggle').getAttribute('aria-pressed'),'true');
    await search('zzznomatchzzz');assert(await page.locator('#empty-reset').isVisible());
    await page.locator('#empty-reset').click();await search('borrow');assert.equal(await page.locator('#word-list .word-card').first().getAttribute('data-id'),id);assert.equal(await card.locator('.media-toggle').getAttribute('aria-pressed'),'true');
    await go('settings');await page.locator('#ui-lang').selectOption('tr');await go('words');
    assert((await card.locator('.media-toggle').getAttribute('aria-label')).includes('kelimesini'));
    assert((await card.locator('[data-action="speak"]').getAttribute('aria-label')).includes('dinle'));
    await page.reload();await page.waitForFunction(()=>window.__appReady===true);await search('borrow');
    assert.equal(await card.locator('.media-toggle').getAttribute('aria-pressed'),'true');
    assert.equal(await card.locator('img').first().getAttribute('src'),img);
    await page.locator('[data-status="learned"]').click();assert(await card.isVisible());
    record('Search, empty state, reset, learned filtering, detached-card translations and persistence');
    await go('novel');
    const chooserPromise=page.waitForEvent('filechooser');await page.locator('#novel-choose').focus();await page.keyboard.press('Enter');const chooser=await chooserPromise;await chooser.setFiles([]);
    record('Keyboard-operated PDF picker');
    await go('settings');await page.locator('input[name="theme"][value="dark"]').check();
    const darkViolations=[];
    for(const route of ['home','review','practice','rankings','words','phrases','grammar','quiz','reading','novel','speak','tutor','settings']){
      await go(route);
      const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','best-practice']).analyze();
      const violations=axe.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}));
      if(violations.length)darkViolations.push({route,violations});else record('Dark theme accessibility',route);
    }
    fs.writeFileSync(path.join(out,'dark-accessibility.json'),JSON.stringify(darkViolations,null,2));
    assert.deepEqual(darkViolations,[],'dark theme accessibility');
    await page.screenshot({path:path.join(out,'words-dark-320.png')});
    await page.goto(base+'?storage=off#words');await page.waitForFunction(()=>window.__appReady===true);
    assert.equal(await page.evaluate(()=>EnglishStudyDiagnostics.storageUsable),false);await search('borrow');await card.locator('.media-toggle').click();record('Storage unavailable: search and learned controls work in memory');
    await page.goto('file:///'+path.join(root,'index.html').replace(/\\/g,'/'));await page.waitForFunction(()=>window.__appReady===true);await go('words');await search('borrow');record('Standalone file:// initialization and search');
    assert.deepEqual(errors,[]);record('No uncaught JavaScript errors');
    const noJS=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const staticPage=await noJS.newPage();await staticPage.goto(base);
    assert.equal(await staticPage.locator('#word-list .word-card').count(),2199);assert(await staticPage.locator('#words-title').isVisible());await noJS.close();record('No JavaScript: all 2,199 original cards remain readable');
    fs.writeFileSync(path.join(out,'regression.json'),JSON.stringify({results,errors},null,2));
  }finally{await browser.close();server.close();}
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
