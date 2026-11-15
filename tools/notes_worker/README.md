# Shared novel notes service

This isolated Cloudflare Worker stores public, plain-text word notes in D1.
It does not modify the existing English teacher service. The GitHub Pages app
calls it over HTTPS; no Cloudflare administrative credential belongs in that app.

## API

- `GET /health`: verifies the database schema can be read.
- `GET /api/notes/index?book=<SHA256>`: `{words:[{word,count}]}`.
- `GET /api/notes?book=<SHA256>&word=<word>`: `{notes:[...]}`.
- `POST /api/notes`: `{book,word,body,author,token,requestId}`; returns `{note}`.
- `PUT /api/notes/<id>`: `{body,author,token}`; returns `{note}`.
- `DELETE /api/notes/<id>`: `{token}`; returns `{deleted:true}`.

The book identifier is a lowercase 64-character SHA-256 digest. Word keys use
NFKC, lowercase, collapsed spaces, ASCII apostrophes and normalized hyphens.
Public note fields are `id`, `word`, `body`, `author`, `createdAt`, `updatedAt`;
timestamps are Unix milliseconds. Note bodies and names must always be rendered
with `textContent`, never interpreted as HTML. Names are self-selected labels,
not verified identities. A random 32-byte lowercase-hex ownership token is kept
on the device; the service stores only its SHA-256 hash. Losing that token loses
editing/deletion capability for the notes it owns.

Notes allow 1,000 characters and names 40. Each word has at most 50 notes per
book; each book at most 5,000. Request IDs make accidental POST retries safe.
Atomic D1 counters limit writes to 10/minute and 100/day per address; only a
daily salted hash is stored, and old counters expire after two days. New reads
always query current notes. Origin checks allow the existing GitHub Pages
origin and localhost development; they are not user authentication.

## Provisioning and deployment

The checked-in database UUID is intentionally a placeholder until the user has
an authorized Cloudflare session. Do not deploy that placeholder configuration.

1. Authenticate Wrangler using the existing account.
2. Create `english-vocabulary-notes` in D1 and copy the returned database UUID
   into `wrangler.jsonc` without changing its binding name, `NOTES`.
3. Apply `wrangler d1 migrations apply english-vocabulary-notes --remote --config tools/notes_worker/wrangler.jsonc`.
4. Set a newly generated random `RATE_SALT` with `wrangler secret put`.
   Never commit or print the secret.
5. Deploy this config and copy the actual returned Worker URL into the app's
   notes configuration. Verify health and cross-browser read/write/delete.

The repeatable helper is `node tools/notes_worker/deploy.mjs`. Its default
`--plan` makes no remote calls; `--check` performs only authenticated read-only
checks; `--apply` performs the above provisioning and deployment. It lists D1
first, pins the actual returned UUID before migrations, refuses unrelated
schemas and mismatched account/database IDs, preserves an existing rate salt,
and obtains the service URL from Wrangler's deployment result. Re-running after
a partial failure reuses the exact notes database instead of creating another.
The temporary deployment result is written to ignored
`.audit-deps/notes-deployment.json`; no secret value is written there.

For an expired session, the supported browser flow can be started without
automatically opening a window:

```
.\.audit-deps\node_modules\.bin\wrangler.cmd login --browser=false --scopes account:read user:read workers_scripts:write d1:write
```

Wrangler prints the official OAuth URL and listens on localhost port 8976 for
the return. It automatically includes `offline_access` for refresh. A device
flow is also available with `--device` when a localhost callback cannot be used.

The existing Worker service, billing plan and teacher secrets must remain
untouched. Cloudflare's Workers Free plan includes D1; usage is bounded by
the provider's daily limits. This service does not switch plans or enable
paid add-ons. See [D1 pricing](https://developers.cloudflare.com/d1/platform/pricing/)
and [Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/).

## Local verification

Use the workspace's ignored Wrangler dependency under `.audit-deps`. Apply
the migration locally, start `wrangler dev --local` with a dummy `RATE_SALT`,
then run `node tools/test_notes_worker.cjs`. Use the same `--persist-to` path
for the migration and dev commands. The test requires a localhost endpoint
and uses synthetic notes; it refuses production URLs.

Automated tests exercise the real local Worker runtime and D1 database,
including two-owner sharing, authorization, idempotency, limits and CORS.
