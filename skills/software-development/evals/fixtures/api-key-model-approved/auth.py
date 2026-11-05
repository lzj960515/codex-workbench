import hashlib
from datetime import datetime, timezone

def authenticate(db, credential):
    digest=hashlib.sha256(credential.encode()).hexdigest()
    row=db.execute("SELECT account_id,expires_at FROM sessions WHERE token_hash=?",(digest,)).fetchone()
    if not row or datetime.fromisoformat(row["expires_at"]) <= datetime.now(timezone.utc):
        raise PermissionError("invalid credential")
    return row["account_id"]
