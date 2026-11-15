#!/usr/bin/env node
/* Explicit, resumable provisioning for this notes service only. This never
   changes the billing plan or the existing english-teacher-3d Worker.
   --plan: no remote calls; --check: read-only remote checks; --apply: provision.
   Run from any directory with Node 22+. Wrangler is an ignored local tool. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const configPath = path.join(here, 'wrangler.jsonc');
const cli = path.join(root, '.audit-deps/node_modules/wrangler/bin/wrangler.js');
const ZERO = '00000000-0000-0000-0000-000000000000';
const UUID = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
const TABLES = {
  notes: ['id', 'book', 'word', 'body', 'author', 'owner_hash', 'request_id', 'created_at', 'updated_at'],
  note_limits: ['key', 'bucket', 'count']
};

export function parseJson(output) {
  const clean = output.replace(/\x1b\[[0-9;]*m/g, '').trim();
  try { return JSON.parse(clean); } catch { /* Wrangler may precede JSON with a warning. */ }
  for (let i = 0; i < clean.length; i++) if (clean[i] === '[' || clean[i] === '{') {
    const end = clean.lastIndexOf(clean[i] === '[' ? ']' : '}');
    try { return JSON.parse(clean.slice(i, end + 1)); } catch { /* Try the next start. */ }
  }
  throw new Error('Wrangler did not return valid JSON; no remote identifier was guessed.');
}
function rows(output) {
  const result = parseJson(output);
  return Array.isArray(result) ? result.flatMap(item => item.results || []) : result.results || [];
}
export function chooseAccount(auth, configured, fromEnvironment) {
  if (!auth.loggedIn) throw new Error('Cloudflare login is required.');
  const accounts = auth.accounts || [];
  const id = configured || fromEnvironment || (accounts.length === 1 ? accounts[0].id : null);
  if (!id || !accounts.some(account => account.id === id)) {
    throw new Error('Select an authorized account explicitly with CLOUDFLARE_ACCOUNT_ID; no account was chosen automatically.');
  }
  if (configured && fromEnvironment && configured !== fromEnvironment) throw new Error('Configured and environment account IDs differ.');
  return id;
}
export function validateTables(found, columns, knownBinding) {
  const user = found.filter(name => !/^sqlite_|^_cf_|^d1_migrations$/.test(name));
  if (user.some(name => !Object.hasOwn(TABLES, name))) throw new Error('Existing D1 database has unrelated tables; refusing to modify it.');
  if (user.length && !knownBinding) throw new Error('An existing nonempty-schema D1 database is not bound in this project; review its UUID before using it.');
  for (const name of user) {
    const actual = (columns[name] || []).map(col => col.name);
    if (actual.length !== TABLES[name].length || TABLES[name].some(col => !actual.includes(col))) {
      throw new Error(`Existing ${name} schema differs from this service; refusing to modify it.`);
    }
  }
}
export function command(args, { input, env = {} } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [cli, ...args], {
      cwd: root, windowsHide: true, shell: false,
      env: { ...process.env, CI: 'true', WRANGLER_SEND_METRICS: 'false', ...env },
      stdio: ['pipe', 'pipe', 'pipe']
    });
    let stdout = '', stderr = '';
    child.stdout.on('data', chunk => { stdout += chunk; });
    child.stderr.on('data', chunk => { stderr += chunk; });
    const redact = value => input ? value.replaceAll(input.trim(), '[redacted]') : value;
    child.on('error', reject);
    child.on('exit', code => {
      if (code === 0) resolve(redact(stdout));
      else reject(new Error(`Wrangler ${args.slice(0, 2).join(' ')} failed (${code}): ${redact(stderr || stdout).slice(0, 2500)}`));
    });
    child.stdin.end(input || '');
  });
}

export async function deploy({ mode = 'plan', run = command, request = fetch, log = console.log } = {}) {
  const config = JSON.parse(await fs.readFile(configPath, 'utf8'));
  const binding = config.d1_databases?.find(item => item.binding === 'NOTES');
  if (config.name !== 'english-vocabulary-notes' || config.main !== 'worker.mjs' || binding?.database_name !== 'english-vocabulary-notes') {
    throw new Error('Unexpected service or binding; refusing to target another project.');
  }
  if (!UUID.test(binding.database_id)) throw new Error('Invalid configured database UUID.');
  const plan = ['Verify Cloudflare login and account', 'Find the exact notes database; create only when absent', 'Reject unrelated or mismatched existing schemas', 'Apply the notes migration', 'Deploy only english-vocabulary-notes', 'Set RATE_SALT only if absent using CSPRNG bytes over stdin', 'Verify the actual deployment URL and database health'];
  if (mode === 'plan') { log(JSON.stringify({ mode, worker: config.name, database: binding.database_name, steps: plan }, null, 2)); return; }
  if (!['check', 'apply'].includes(mode)) throw new Error('Use --plan, --check or --apply.');
  await fs.access(cli);
  const auth = parseJson(await run(['whoami', '--json']));
  const account = chooseAccount(auth, config.account_id, process.env.CLOUDFLARE_ACCOUNT_ID);
  const env = { CLOUDFLARE_ACCOUNT_ID: account };
  const args = ['--config', configPath];
  const listed = parseJson(await run(['d1', 'list', '--json', ...args], { env }));
  if (!Array.isArray(listed)) throw new Error('Unexpected database list; no database will be created.');
  const matches = listed.filter(item => item.name === binding.database_name);
  if (matches.length > 1) throw new Error('Duplicate database names require review.');
  let database = matches[0];
  if (database && !UUID.test(database.uuid)) throw new Error('Cloudflare returned an invalid database UUID.');
  if (binding.database_id !== ZERO && (!database || database.uuid !== binding.database_id)) {
    throw new Error('The configured database UUID does not match the exact remote database name/account.');
  }
  if (database) {
    const found = rows(await run(['d1', 'execute', database.uuid, '--remote', '--json', '--command', "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", ...args], { env })).map(row => row.name);
    const columns = {};
    for (const name of Object.keys(TABLES)) if (found.includes(name)) {
      columns[name] = rows(await run(['d1', 'execute', database.uuid, '--remote', '--json', '--command', `PRAGMA table_info(${name})`, ...args], { env }));
    }
    validateTables(found, columns, binding.database_id === database.uuid);
  }
  if (mode === 'check') {
    log(JSON.stringify({ mode, authenticated: true, accountSelected: true, databaseExists: Boolean(database), schemaCompatible: true, readyToApply: true, steps: plan }, null, 2));
    return;
  }
  if (!database) {
    log('Creating the isolated notes D1 database.');
    // Re-list after creation instead of guessing a UUID from formatted output.
    await run(['d1', 'create', binding.database_name, '--update-config=false', ...args], { env });
    const after = parseJson(await run(['d1', 'list', '--json', ...args], { env }));
    const created = after.filter(item => item.name === binding.database_name);
    if (created.length !== 1 || !UUID.test(created[0].uuid)) throw new Error('Could not resolve the newly created database; rerun safely after checking D1.');
    database = created[0];
  }
  // Pin the actual returned UUID before migrations. Retrying after any later
  // failure therefore reuses this exact database rather than creating a second.
  config.account_id = account;
  binding.database_id = database.uuid;
  await fs.writeFile(configPath, JSON.stringify(config, null, 2) + '\n');
  log('Applying the notes migration to the pinned database.');
  await run(['d1', 'migrations', 'apply', binding.database_name, '--remote', ...args], { env });
  log('Deploying english-vocabulary-notes; the teacher Worker is untouched.');
  const deployed = await run(['deploy', '--strict', ...args], { env });
  const match = deployed.match(/https:\/\/english-vocabulary-notes\.[a-z0-9-]+\.workers\.dev\b/i);
  if (!match) throw new Error('The actual notes Worker URL was not returned; no URL was invented.');
  const secrets = parseJson(await run(['secret', 'list', '--format', 'json', ...args], { env }));
  if (!Array.isArray(secrets)) throw new Error('Could not check secret names.');
  if (!secrets.some(secret => secret.name === 'RATE_SALT')) {
    log('Creating the rate-limit salt without writing or printing its value.');
    const salt = crypto.randomBytes(32).toString('hex');
    await run(['secret', 'put', 'RATE_SALT', ...args], { env, input: salt + '\n' });
  }
  const url = match[0];
  let health, lastError;
  for (let attempt = 0; attempt < 6; attempt++) {
    try {
      const response = await request(url + '/health', { signal: AbortSignal.timeout(15000) });
      health = response.ok ? await response.json() : null;
      if (health?.ok && health.service === config.name) break;
    } catch (error) { lastError = error.message; }
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  if (!health?.ok || health.service !== config.name) throw new Error('Notes deployment health check failed' + (lastError ? ': ' + lastError : ''));
  const result = { deployed: true, worker: config.name, url, databaseId: database.uuid, verifiedAt: new Date().toISOString() };
  await fs.writeFile(path.join(root, '.audit-deps/notes-deployment.json'), JSON.stringify(result, null, 2) + '\n');
  log(JSON.stringify(result, null, 2));
  return result;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const flags = process.argv.slice(2);
  if (flags.length > 1 || (flags[0] && !['--plan', '--check', '--apply'].includes(flags[0]))) {
    console.error('Usage: node tools/notes_worker/deploy.mjs [--plan|--check|--apply]'); process.exitCode = 1;
  } else deploy({ mode: (flags[0] || '--plan').slice(2) }).catch(error => { console.error(error.message); process.exitCode = 1; });
}
