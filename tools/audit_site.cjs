/* Reproducible, isolated usability audit. Never reads a user's browser profile. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('../.audit-deps/node_modules/playwright');
const { default: AxeBuilder } = require('../.audit-deps/node_modules/@axe-core/playwright');
const root = path.resolve(__dirname, '..');
const phase = process.argv[2] || 'baseline';
const out = path.join(root, 'audits', '2026-11-09', phase);
fs.mkdirSync(out, { recursive: true });
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/favicon.ico')) { res.writeHead(204); res.end(); return; }
  const file = req.url.startsWith('/version.json') ? 'version.json' : 'index.html';
  res.setHeader('Content-Type', file.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8');
  res.end(fs.readFileSync(path.join(root, file)));
});
const routes = ['home','words','review','practice','rankings','phrases','grammar','quiz','reading','novel','speak','tutor','settings'];
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
  await context.route('https://**/*', route => route.abort());
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.addInitScript(() => {
    window.__auditPerf = { longTasks: [], lcp: [], cls: [] };
    for (const type of ['longtask', 'largest-contentful-paint', 'layout-shift']) {
      try { new PerformanceObserver(list => {
        for (const e of list.getEntries()) {
          if (type === 'longtask') window.__auditPerf.longTasks.push({ start: e.startTime, duration: e.duration });
          if (type === 'largest-contentful-paint') window.__auditPerf.lcp.push({ start: e.startTime, size: e.size });
          if (type === 'layout-shift' && !e.hadRecentInput) window.__auditPerf.cls.push(e.value);
        }
      }).observe({ type, buffered: true }); } catch (_) {}
    }
  });
  const base = `http://127.0.0.1:${server.address().port}/`;
  await page.goto(base, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__appReady === true);
  const report = { phase, testedAt: new Date().toISOString(), browser: await browser.version(), externalRequestsBlocked: true,
    bytes: fs.statSync(path.join(root,'index.html')).size, errors, routes: [], flows: {} };
  report.initial = await page.evaluate(() => ({ title: document.title, nodes: document.querySelectorAll('*').length,
    navigation: performance.getEntriesByType('navigation')[0].toJSON(), perf: window.__auditPerf,
    diagnostics: window.EnglishStudyDiagnostics, description: document.querySelector('meta[name="description"]')?.content || null }));
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: width >= 900 ? 1000 : 844 });
    for (const route of routes) {
      await page.evaluate(route => { location.hash = route; }, route);
      await page.waitForFunction(route => document.querySelector(`.view[data-view="${route}"]`).classList.contains('is-active'), route);
      const info = await page.evaluate(() => {
        const visible = el => el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden';
        const main = document.querySelector('.view.is-active');
        return { overflow: document.documentElement.scrollWidth - innerWidth,
          heading: main.querySelector('h1')?.textContent,
          smallTargets: [...document.querySelectorAll('button,a,input,select,summary,[role="button"]')].filter(visible).map(el => {
            const r = el.getBoundingClientRect(); return { tag: el.tagName, id: el.id, class: el.className, text: (el.getAttribute('aria-label') || el.textContent).trim().slice(0,75), width: Math.round(r.width), height: Math.round(r.height) };
          }).filter(r => r.width < 44 || r.height < 44),
          outOfBounds: [...main.querySelectorAll('*')].filter(visible).filter(el=>{const r=el.getBoundingClientRect();return r.right>innerWidth+1 || r.left < -1;}).slice(0,15).map(el=>({tag:el.tagName,class:el.className,text:el.textContent.slice(0,60)})) };
      });
      const item = { width, route, ...info };
      if (width === 390) {
        const axe = await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','best-practice']).analyze();
        item.accessibility = axe.violations.map(v => ({ id:v.id, impact:v.impact, description:v.description, help:v.help, helpUrl:v.helpUrl,
          nodes:v.nodes.map(n=>({target:n.target,html:n.html,summary:n.failureSummary})).slice(0,15), count:v.nodes.length }));
        item.incomplete = axe.incomplete.map(v=>({id:v.id,count:v.nodes.length}));
        console.log(route, 'axe:', item.accessibility.map(v=>`${v.id}(${v.count})`).join(', ') || 'no violations');
      }
      if ([390,1440].includes(width) && ['home','words','practice','settings'].includes(route)) await page.screenshot({ path: path.join(out, `${route}-${width}.png`) });
      report.routes.push(item);
    }
  }
  await page.setViewportSize({ width:390, height:844 });
  await page.evaluate(()=>{location.hash='home';});
  await page.locator('#nav-more').click();
  report.flows.profileDialog = await page.evaluate(() => ({ closeButton: !!document.querySelector('#more-sheet button[data-close]'), active:document.activeElement.outerHTML.slice(0,250), scrollLocked:[document.body,document.documentElement].some(el=>getComputedStyle(el).overflow==='hidden') }));
  const first = await page.evaluate(()=>document.activeElement.outerHTML);
  for(let i=0;i<12;i++) await page.keyboard.press('Tab');
  report.flows.profileDialog.tabEscaped = await page.evaluate(()=>!document.querySelector('#more-sheet').contains(document.activeElement));
  await page.keyboard.press('Escape');
  report.flows.profileDialog.escapeCloses = await page.locator('#more-sheet').isHidden();
  report.flows.profileDialog.focusRestored = await page.locator('#nav-more').evaluate(el=>el===document.activeElement);
  await page.evaluate(()=>{location.hash='words';});
  await page.locator('#word-search').fill('borrow');
  await page.waitForFunction(()=>{const cards=[...document.querySelectorAll('#word-list .word-card:not([hidden])')];return cards.length>0 && cards.every(el=>el.textContent.toLowerCase().includes('borrow'));});
  report.flows.search = { matches: await page.locator('#word-list .word-card:visible').count() };
  await page.locator('#word-search').fill('zzznomatchzzz');
  await page.locator('#empty-reset').waitFor({state:'visible'});
  report.flows.search.emptyState = await page.locator('#empty-reset').isVisible();
  await page.locator('#empty-reset').click();
  report.flows.search.reset = await page.locator('#word-search').inputValue() === '';
  await page.evaluate(()=>{location.hash='settings';});
  report.flows.settingsControls = await page.locator('.view.is-active select').evaluateAll(els=>els.map(el=>({id:el.id,options:[...el.options].map(o=>({value:o.value,text:o.text}))})));
  fs.writeFileSync(path.join(out,'audit.json'), JSON.stringify(report,null,2));
  console.log(JSON.stringify({phase,bytes:report.bytes,nodes:report.initial.nodes,errors,overflow:report.routes.filter(r=>r.overflow>1).map(r=>({width:r.width,route:r.route,overflow:r.overflow})),smallTargets:report.routes.filter(r=>r.width===390).map(r=>({route:r.route,count:r.smallTargets.length})),flows:report.flows},null,2));
  await browser.close(); server.close();
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
