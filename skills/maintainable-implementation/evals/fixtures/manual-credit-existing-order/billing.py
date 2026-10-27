def invoice_rows(db, account_id):
    return [{"id": row["id"], "source": "人工发放" if row["payment_method"] == "manual" else "在线购买", "credits": row["credits"], "amount_cents": row["amount_cents"]} for row in db.execute("SELECT * FROM orders WHERE account_id=? ORDER BY id", (account_id,))]
