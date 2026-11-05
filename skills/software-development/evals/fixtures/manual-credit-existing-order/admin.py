from ledger import balance
from billing import invoice_rows

def require_admin(actor):
    if actor["role"] != "admin":
        raise PermissionError("admin required")

def account_detail(db, actor, account_id):
    require_admin(actor)
    return {"credits": balance(db, account_id), "orders": invoice_rows(db, account_id)}
