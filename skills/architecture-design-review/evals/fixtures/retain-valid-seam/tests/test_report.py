import unittest
from report import BillingReport


class MemoryLedger:
    def load(self, period):
        return [{"amount_cents": 125}, {"amount_cents": 75}] if period == "2026-08" else []


class Reports(unittest.TestCase):
    def test_period_total(self):
        self.assertEqual(BillingReport(MemoryLedger()).total("2026-08"), 200)

    def test_empty_period(self):
        self.assertEqual(BillingReport(MemoryLedger()).total("2026-09"), 0)
