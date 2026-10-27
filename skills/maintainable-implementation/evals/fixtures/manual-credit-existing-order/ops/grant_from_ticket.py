from orders import record_manual_credit

def grant_from_ticket(db, ticket, operator_id):
    return record_manual_credit(db, ticket["account_id"], ticket["credits"], "support-"+ticket["id"], operator_id)
