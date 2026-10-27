CREATE TABLE accounts (id TEXT PRIMARY KEY, email TEXT NOT NULL);
CREATE TABLE orders (
 id TEXT PRIMARY KEY,
 account_id TEXT NOT NULL REFERENCES accounts(id),
 payment_method TEXT NOT NULL CHECK (payment_method IN ('checkout','manual')),
 status TEXT NOT NULL CHECK (status IN ('pending','confirmed')),
 product_id TEXT,
 amount_cents INTEGER NOT NULL,
 credits INTEGER NOT NULL CHECK (credits > 0),
 created_by TEXT NOT NULL
);
CREATE TABLE requests (
 id TEXT PRIMARY KEY,
 account_id TEXT NOT NULL REFERENCES accounts(id),
 status TEXT NOT NULL CHECK (status IN ('reserved','succeeded','failed')),
 allocations TEXT NOT NULL
);
