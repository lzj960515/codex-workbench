def require_admin(actor):
    if actor["role"] != "admin":
        raise PermissionError("admin required")

def account_detail(db, actor, account_id):
    require_admin(actor)
    row=db.execute("SELECT id,email FROM accounts WHERE id=?",(account_id,)).fetchone()
    if not row:
        raise LookupError("account not found")
    return dict(row)
