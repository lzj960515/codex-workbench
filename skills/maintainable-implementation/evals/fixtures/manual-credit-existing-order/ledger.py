import json

def available_orders(db, account_id):
    orders = [dict(row) for row in db.execute("SELECT * FROM orders WHERE account_id=? AND status='confirmed' ORDER BY id", (account_id,))]
    used = {}
    for row in db.execute("SELECT allocations FROM requests WHERE account_id=? AND status IN ('reserved','succeeded')", (account_id,)):
        for allocation in json.loads(row["allocations"]):
            used[allocation["order_id"]] = used.get(allocation["order_id"], 0) + allocation["credits"]
    return [{"order_id": row["id"], "credits": row["credits"]-used.get(row["id"],0)} for row in orders]

def balance(db, account_id):
    return sum(row["credits"] for row in available_orders(db, account_id))

def reserve(db, account_id, request_id, credits):
    if type(credits) is not int or credits <= 0:
        raise ValueError("invalid requested credits")
    sources = available_orders(db, account_id)
    if sum(row["credits"] for row in sources) < credits:
        raise ValueError("insufficient credits")
    allocations = []
    remaining = credits
    for row in sources:
        used = min(row["credits"], remaining)
        if used:
            allocations.append({"order_id": row["order_id"], "credits": used})
            remaining -= used
    with db:
        db.execute("INSERT INTO requests VALUES (?,?,'reserved',?)", (request_id, account_id, json.dumps(allocations)))
    return allocations

def complete(db, account_id, request_id):
    with db:
        changed = db.execute("UPDATE requests SET status='succeeded' WHERE id=? AND account_id=? AND status='reserved'", (request_id, account_id))
    return changed.rowcount
