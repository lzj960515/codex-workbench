CREATE TABLE accounts (id TEXT PRIMARY KEY, email TEXT NOT NULL);
CREATE TABLE sessions (
 token_hash TEXT PRIMARY KEY,
 account_id TEXT NOT NULL REFERENCES accounts(id),
 expires_at TEXT NOT NULL
);
