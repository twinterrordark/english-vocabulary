/* Persistent, public word notes. Client ownership tokens never leave the
   request body, and are stored only as SHA-256 hashes. No external packages. */
const SITE = 'https://twinterrordark.github.io';
const MAX_BODY_BYTES = 8192;
const enc = new TextEncoder();

function originAllowed(origin) {
  return origin === SITE || /^http:\/\/(?:localhost|127\.0\.0\.1)(?::\d+)?$/.test(origin || '');
}
function headers(origin) {
  const out = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff', vary: 'Origin' };
  if (originAllowed(origin)) out['access-control-allow-origin'] = origin;
  return out;
}
function json(data, status, origin, extra = {}) {
  return new Response(JSON.stringify(data), { status, headers: { ...headers(origin), ...extra } });
}
class ApiError extends Error {
  constructor(code, status = 400) { super(code); this.status = status; }
}
const fail = (code, status) => { throw new ApiError(code, status); };
async function sha(text) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', enc.encode(text)))].map(b => b.toString(16).padStart(2, '0')).join('');
}
export function wordKey(value) {
  if (typeof value !== 'string') fail('invalid_word');
  const word = value.normalize('NFKC').toLowerCase().replace(/[’‘]/g, "'").replace(/[‐‑]/g, '-').trim().replace(/\s+/g, ' ');
  if (!word || word.length > 100 || !/^[\p{L}\p{N}' .-]+$/u.test(word) || !/[\p{L}]/u.test(word)) fail('invalid_word');
  return word;
}
function bookKey(value) {
  if (typeof value !== 'string' || !/^[a-f0-9]{64}$/.test(value)) fail('invalid_book');
  return value;
}
function text(value, max, emptyDefault) {
  if (typeof value !== 'string') value = emptyDefault ?? '';
  const out = value.normalize('NFKC').trim();
  if (!out && emptyDefault) return emptyDefault;
  if (!out || out.length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(out)) fail('invalid_text');
  return out;
}
function token(value) {
  if (typeof value !== 'string' || !/^[a-f0-9]{64}$/.test(value)) fail('invalid_token');
  return value;
}
async function bodyOf(request) {
  if (!/^application\/json(?:;|$)/i.test(request.headers.get('content-type') || '')) fail('json_required', 415);
  if (Number(request.headers.get('content-length')) > MAX_BODY_BYTES) fail('body_too_large', 413);
  const reader = request.body?.getReader();
  if (!reader) fail('invalid_json');
  const chunks = []; let length = 0;
  while (true) {
    const { done, value } = await reader.read(); if (done) break;
    length += value.byteLength;
    if (length > MAX_BODY_BYTES) { await reader.cancel(); fail('body_too_large', 413); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(length); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  let data;
  try { data = JSON.parse(new TextDecoder().decode(bytes)); } catch { fail('invalid_json'); }
  if (!data || typeof data !== 'object' || Array.isArray(data)) fail('invalid_json');
  return data;
}
function note(row) {
  return { id: row.id, word: row.word, body: row.body, author: row.author, createdAt: row.created_at, updatedAt: row.updated_at };
}
async function writeLimit(request, env) {
  if (!env.RATE_SALT || env.RATE_SALT.length < 16) fail('service_unconfigured', 503);
  const now = Date.now(), day = Math.floor(now / 86400000);
  const ip = request.headers.get('CF-Connecting-IP') || 'local-development';
  const fingerprint = await sha(env.RATE_SALT + ':' + day + ':' + ip);
  // Atomic SQL ensures simultaneous requests cannot bypass a counter.
  for (const [span, max] of [[60000, 10], [86400000, 100]]) {
    const bucket = Math.floor(now / span);
    const row = await env.NOTES.prepare(`INSERT INTO note_limits(key,bucket,count) VALUES(?,?,1)
      ON CONFLICT(key) DO UPDATE SET count=count+1 WHERE count < ? RETURNING count`)
      .bind(fingerprint + ':' + span + ':' + bucket, now, max).first();
    if (!row) fail('rate_limited', 429);
  }
  await env.NOTES.prepare('DELETE FROM note_limits WHERE bucket < ?').bind(now - 2 * 86400000).run();
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin');
    try {
      const url = new URL(request.url);
      if (request.method === 'OPTIONS') {
        if (!originAllowed(origin)) fail('origin_forbidden', 403);
        return new Response(null, { status: 204, headers: { ...headers(origin), 'access-control-allow-methods': 'GET, POST, PUT, DELETE, OPTIONS', 'access-control-allow-headers': 'content-type', 'access-control-max-age': '86400' } });
      }
      if (origin && !originAllowed(origin)) fail('origin_forbidden', 403);
      if (url.pathname === '/health' && request.method === 'GET') {
        await env.NOTES.prepare('SELECT 1 FROM notes LIMIT 1').first();
        return json({ ok: true, service: 'english-vocabulary-notes' }, 200, origin);
      }
      if (url.pathname === '/api/notes/index' && request.method === 'GET') {
        const book = bookKey(url.searchParams.get('book'));
        const { results } = await env.NOTES.prepare('SELECT word, COUNT(*) AS count FROM notes WHERE book=? GROUP BY word ORDER BY word LIMIT 5000').bind(book).all();
        return json({ words: results }, 200, origin);
      }
      if (url.pathname === '/api/notes' && request.method === 'GET') {
        const book = bookKey(url.searchParams.get('book')), word = wordKey(url.searchParams.get('word'));
        const { results } = await env.NOTES.prepare('SELECT id,word,body,author,created_at,updated_at FROM notes WHERE book=? AND word=? ORDER BY created_at DESC,id DESC LIMIT 50').bind(book, word).all();
        return json({ notes: results.map(note) }, 200, origin);
      }
      if (!['POST', 'PUT', 'DELETE'].includes(request.method)) fail('not_found', 404);
      if (!originAllowed(origin)) fail('origin_forbidden', 403);
      const data = await bodyOf(request), owner = await sha(token(data.token));
      if (url.pathname === '/api/notes' && request.method === 'POST') {
        const book = bookKey(data.book), word = wordKey(data.word), body = text(data.body, 1000);
        const author = text(data.author, 40, 'Okur').replace(/\s+/g, ' ');
        if (typeof data.requestId !== 'string' || !/^[a-zA-Z0-9_-]{10,128}$/.test(data.requestId)) fail('invalid_request_id');
        const existing = await env.NOTES.prepare('SELECT * FROM notes WHERE owner_hash=? AND request_id=?').bind(owner, data.requestId).first();
        if (existing) {
          if (existing.book !== book || existing.word !== word) fail('request_id_conflict', 409);
          return json({ note: note(existing), duplicate: true }, 200, origin);
        }
        await writeLimit(request, env);
        const id = crypto.randomUUID(), now = Date.now();
        // Bound public list sizes in the same atomic INSERT as the write.
        const row = await env.NOTES.prepare(`INSERT INTO notes(id,book,word,body,author,owner_hash,request_id,created_at,updated_at)
          SELECT ?,?,?,?,?,?,?,?,? WHERE (SELECT COUNT(*) FROM notes WHERE book=? AND word=?) < 50
          AND (SELECT COUNT(*) FROM notes WHERE book=?) < 5000
          ON CONFLICT(owner_hash,request_id) DO NOTHING RETURNING *`)
          .bind(id, book, word, body, author, owner, data.requestId, now, now, book, word, book).first();
        if (!row) {
          const duplicate = await env.NOTES.prepare('SELECT * FROM notes WHERE owner_hash=? AND request_id=?').bind(owner, data.requestId).first();
          if (duplicate) {
            if (duplicate.book !== book || duplicate.word !== word) fail('request_id_conflict', 409);
            return json({ note: note(duplicate), duplicate: true }, 200, origin);
          }
          fail('note_limit', 409);
        }
        return json({ note: note(row) }, 201, origin);
      }
      const match = url.pathname.match(/^\/api\/notes\/([a-f0-9-]{36})$/);
      if (!match || !['PUT', 'DELETE'].includes(request.method)) fail('not_found', 404);
      const existing = await env.NOTES.prepare('SELECT * FROM notes WHERE id=?').bind(match[1]).first();
      if (!existing) fail('not_found', 404);
      if (existing.owner_hash !== owner) fail('not_owner', 403);
      if (request.method === 'PUT') {
        const body = text(data.body, 1000), author = text(data.author, 40, 'Okur').replace(/\s+/g, ' ');
        await writeLimit(request, env);
        const row = await env.NOTES.prepare('UPDATE notes SET body=?,author=?,updated_at=? WHERE id=? AND owner_hash=? RETURNING *').bind(body, author, Date.now(), match[1], owner).first();
        return json({ note: note(row) }, 200, origin);
      }
      await writeLimit(request, env);
      await env.NOTES.prepare('DELETE FROM notes WHERE id=? AND owner_hash=?').bind(match[1], owner).run();
      return json({ deleted: true }, 200, origin);
    } catch (error) {
      // Do not log request bodies, tokens, addresses or public note content.
      return json({ error: error instanceof ApiError ? error.message : 'service_unavailable' }, error instanceof ApiError ? error.status : 503, origin,
        error.status === 429 ? { 'retry-after': '60' } : {});
    }
  }
};
