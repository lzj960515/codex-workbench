def record_manual_credit(db, account_id, credits, operation_id, operator_id):
    if type(credits) is not int or credits <= 0:
        raise ValueError("credits must be a positive integer")
    if not db.execute("SELECT id FROM accounts WHERE id=?", (account_id,)).fetchone():
        raise LookupError("account not found")
    existing = db.execute("SELECT * FROM orders WHERE id=?", (operation_id,)).fetchone()
    if existing:
        if (existing["account_id"], existing["credits"], existing["created_by"], existing["payment_method"]) != (account_id, credits, operator_id, "manual"):
            raise ValueError("operation already belongs to another credit order")
        return dict(existing)
    with db:
        db.execute("INSERT INTO orders VALUES (?,?,'manual','confirmed',NULL,0,?,?)", (operation_id, account_id, credits, operator_id))
    return dict(db.execute("SELECT * FROM orders WHERE id=?", (operation_id,)).fetchone())
