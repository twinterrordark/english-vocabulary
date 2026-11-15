CREATE TABLE IF NOT EXISTS notes (
  id TEXT PRIMARY KEY,
  book TEXT NOT NULL CHECK(length(book) = 64),
  word TEXT NOT NULL CHECK(length(word) BETWEEN 1 AND 100),
  body TEXT NOT NULL CHECK(length(body) BETWEEN 1 AND 1000),
  author TEXT NOT NULL CHECK(length(author) BETWEEN 1 AND 40),
  owner_hash TEXT NOT NULL CHECK(length(owner_hash) = 64),
  request_id TEXT NOT NULL CHECK(length(request_id) BETWEEN 10 AND 128),
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  UNIQUE(owner_hash, request_id)
);
CREATE INDEX IF NOT EXISTS notes_book_word ON notes(book, word, created_at DESC);

-- Anonymous write limits: only a keyed hash of the address and current UTC day
-- is retained. Buckets expire; raw addresses and client tokens are never stored.
CREATE TABLE IF NOT EXISTS note_limits (
  key TEXT PRIMARY KEY,
  bucket INTEGER NOT NULL,
  count INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS note_limits_bucket ON note_limits(bucket);
