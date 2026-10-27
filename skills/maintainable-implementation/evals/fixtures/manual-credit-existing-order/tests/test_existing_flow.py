import unittest
from database import open_database
from ops.grant_from_ticket import grant_from_ticket
from ledger import balance, reserve, complete
from billing import invoice_rows

class ExistingFlow(unittest.TestCase):
    def test_support_credit_uses_original_order_and_billing(self):
        db=open_database()
        self.addCleanup(db.close)
        db.execute("INSERT INTO accounts VALUES ('account-1','test-account')")
        ticket={"id":"ticket-1","account_id":"account-1","credits":100}
        grant_from_ticket(db,ticket,"support-1")
        grant_from_ticket(db,ticket,"support-1")
        self.assertEqual(balance(db,"account-1"),100)
        reserve(db,"account-1","request-1",20)
        complete(db,"account-1","request-1")
        self.assertEqual(balance(db,"account-1"),80)
        self.assertEqual(invoice_rows(db,"account-1")[0]["source"],"人工发放")
