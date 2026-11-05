class BillingReport:
    def __init__(self, ledger):
        self.ledger = ledger

    def total(self, period):
        entries = self.ledger.load(period)
        return sum(entry["amount_cents"] for entry in entries)
