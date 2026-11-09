const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const zlib = require('node:zlib');
const { execFileSync } = require('node:child_process');
const { pathToFileURL } = require('node:url');
const root = path.resolve(__dirname, '..');
const phase = process.argv[2] || 'baseline';
const live = process.argv.includes('--live');
const out = path.join(root,'audits','2026-11-09',phase);
fs.mkdirSync(out,{recursive:true});
const snapshot = process.argv.includes('--git-baseline');
const files = Object.fromEntries(['index.html','version.json'].map(file=>{
  const raw = snapshot ? execFileSync('git',['show',`HEAD:${file}`],{cwd:root,maxBuffer:64*1024*1024}) : fs.readFileSync(path.join(root,file));
  return [file,{raw,gzip:zlib.gzipSync(raw)}];
}));
const server = http.createServer((req,res)=>{
  if(req.url.startsWith('/favicon.ico')){res.writeHead(204);res.end();return;}
  const pathname=new URL(req.url,'http://localhost').pathname;
  if(!['/','/index.html','/version.json'].includes(pathname)){res.writeHead(404,{'Content-Type':'text/plain'});res.end('Not found');return;}
  const file = req.url.startsWith('/version.json')?'version.json':'index.html';
  res.setHeader('Content-Type',file.endsWith('.json')?'application/json':'text/html; charset=utf-8');
  const raw=files[file].raw;
  const body=req.headers['accept-encoding']?.includes('gzip')?files[file].gzip:raw;
  if(body!==raw)res.setHeader('Content-Encoding','gzip');
  res.setHeader('Content-Length',body.length);
  res.end(body);
});
(async()=>{
  const {default:lighthouse} = await import(pathToFileURL(path.join(root,'.audit-deps/node_modules/lighthouse/core/index.js')));
  const chromeLauncher = await import(pathToFileURL(path.join(root,'.audit-deps/node_modules/chrome-launcher/dist/index.js')));
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const url = live?'https://twinterrordark.github.io/english-vocabulary/':`http://127.0.0.1:${server.address().port}/`;
  for(const mode of ['mobile','desktop']){
    const chrome = await chromeLauncher.launch({chromePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',chromeFlags:['--headless=new','--disable-gpu','--no-first-run'],handleSIGINT:false});
    try{
      const flags={port:chrome.port,output:['json','html'],logLevel:'error',onlyCategories:['performance','accessibility','best-practices','seo']};
      const config=mode==='desktop'?{extends:'lighthouse:default',settings:{formFactor:'desktop',screenEmulation:{mobile:false,width:1440,height:900,deviceScaleFactor:1,disabled:false},throttling:{rttMs:40,throughputKbps:10240,cpuSlowdownMultiplier:1,requestLatencyMs:0,downloadThroughputKbps:0,uploadThroughputKbps:0}}}:undefined;
      const result=await lighthouse(url,flags,config);
      const name=`lighthouse-${live?'live-':''}${mode}`;
      fs.writeFileSync(path.join(out,`${name}.json`),result.report[0]);
      fs.writeFileSync(path.join(out,`${name}.html`),result.report[1]);
      console.log(JSON.stringify({mode,live,url,categories:Object.fromEntries(Object.entries(result.lhr.categories).map(([k,v])=>[k,v.score])),metrics:Object.fromEntries(['first-contentful-paint','largest-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index','total-byte-weight','dom-size','document-latency-insight'].map(k=>[k,result.lhr.audits[k]?.displayValue])),warnings:result.lhr.runWarnings},null,2));
    }finally{await chrome.kill();}
  }
  server.close();
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
