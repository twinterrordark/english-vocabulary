/* Integration checks against Wrangler's real local Worker+D1, not SQL mocks.
   Start tools/notes_worker with a local D1 migration and a dummy RATE_SALT.
   Never point this rate-limit suite at a production endpoint. */
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.NOTES_TEST_URL || 'http://127.0.0.1:8797';
assert(/^http:\/\/(?:127\.0\.0\.1|localhost):\d+$/.test(base), 'Local endpoint required');
const origin = 'https://twinterrordark.github.io';
const key = () => crypto.randomBytes(32).toString('hex');
const book = key(), owner = key(), another = key(), results = [];
const req = async (method, route, data, extra = {}) => {
  const response = await fetch(base + route, { method, headers: { Origin: origin, 'content-type': 'application/json', 'CF-Connecting-IP': '198.51.100.16', ...extra }, ...(data === undefined ? {} : { body: JSON.stringify(data) }) });
  return { status: response.status, headers: response.headers, data: response.status === 204 ? null : await response.json() };
};
const pass = name => { results.push(name); console.log('PASS', name); };
(async () => {
  assert.equal((await req('GET', '/health')).status, 200);
  const options = await req('OPTIONS', '/api/notes'); assert.equal(options.status, 204); assert.equal(options.headers.get('access-control-allow-origin'), origin);
  const blocked = await req('GET', '/api/notes/index?book=' + book, undefined, { Origin: 'https://unrelated.example' });
  assert.equal(blocked.status, 403); assert.equal(blocked.headers.get('access-control-allow-origin'), null);
  assert.equal((await req('GET', '/api/notes?book=invalid&word=coat')).status, 400);
  pass('Real D1 health, allowed CORS preflight, rejected foreign origin and invalid book');

  const noteData = { book, word: '  TAKE   OFF ', body: 'Bağlamda paltosunu çıkarmak anlamında.', author: 'Okur A', token: owner, requestId: crypto.randomUUID() };
  const created = await req('POST', '/api/notes', noteData); assert.equal(created.status, 201);
  assert.equal(created.data.note.word, 'take off'); assert.equal(created.data.note.author, 'Okur A');
  assert(!JSON.stringify(created.data).includes(owner)); assert(!JSON.stringify(created.data).includes('owner_hash'));
  const id = created.data.note.id;
  const duplicate = await req('POST', '/api/notes', noteData); assert.equal(duplicate.status, 200); assert.equal(duplicate.data.note.id, id); assert.equal(duplicate.data.duplicate, true);
  const read = await req('GET', `/api/notes?book=${book}&word=take%20off`); assert.equal(read.data.notes.length, 1); assert.equal(read.data.notes[0].body, noteData.body);
  assert.deepEqual((await req('GET', '/api/notes/index?book=' + book)).data.words, [{ word: 'take off', count: 1 }]);
  pass('Public persistent note read and highlight index; normalized phrases; idempotent retry without token disclosure');

  const second = await req('POST', '/api/notes', { ...noteData, token: another, author: 'Okur B', requestId: crypto.randomUUID(), body: '<script>literal note text</script>' });
  assert.equal(second.status, 201);
  assert.equal((await req('GET', `/api/notes?book=${book}&word=take%20off`)).data.notes.length, 2);
  assert.equal((await req('PUT', '/api/notes/' + id, { token: another, body: 'not mine' })).status, 403);
  assert.equal((await req('DELETE', '/api/notes/' + id, { token: another })).status, 403);
  const edited = await req('PUT', '/api/notes/' + id, { token: owner, body: 'Güncellenmiş açıklama', author: 'Okur A' });
  assert.equal(edited.status, 200); assert.equal(edited.data.note.body, 'Güncellenmiş açıklama');
  assert.equal((await req('DELETE', '/api/notes/' + id, { token: owner })).status, 200);
  const left = (await req('GET', `/api/notes?book=${book}&word=take%20off`)).data.notes;
  assert.equal(left.length, 1); assert.equal(left[0].body, '<script>literal note text</script>');
  assert.equal((await req('DELETE', '/api/notes/' + second.data.note.id, { token: another })).status, 200);
  assert.deepEqual((await req('GET', '/api/notes/index?book=' + book)).data.words, []);
  pass('Different owners can share notes, but only the original token can edit/delete; index clears after deletion');

  assert.equal((await req('POST', '/api/notes', { ...noteData, body: 'x'.repeat(1001) })).status, 400);
  assert.equal((await req('POST', '/api/notes', { ...noteData, token: 'short' })).status, 400);
  assert.equal((await req('POST', '/api/notes', { ...noteData, body: 'x'.repeat(9000) })).status, 413);
  const rateBook = key();
  for (let i = 0; i < 10; i++) {
    const item = await req('POST', '/api/notes', { ...noteData, book: rateBook, requestId: crypto.randomUUID() }, { 'CF-Connecting-IP': '198.51.100.99' });
    assert.equal(item.status, 201, 'allowed bounded write ' + i);
  }
  const limited = await req('POST', '/api/notes', { ...noteData, book: rateBook, requestId: crypto.randomUUID() }, { 'CF-Connecting-IP': '198.51.100.99' });
  assert.equal(limited.status, 429); assert.equal(limited.headers.get('retry-after'), '60');
  pass('Body/ownership limits reject invalid payloads; atomic D1 rate counter blocks the eleventh minute write');
  const out = path.join(__dirname, '../audits/2026-11-15'); fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, 'notes-worker-checks.json'), JSON.stringify({ local: true, realWorkerRuntime: true, realD1: true, results }, null, 2) + '\n');
})().catch(error => { console.error(error); process.exitCode = 1; });
