from file_ledger import FileLedger
from report import BillingReport


def total(directory, period):
    return BillingReport(FileLedger(directory)).total(period)
