from typing import Protocol, TypedDict


class LedgerEntry(TypedDict):
    amount_cents: int


class Ledger(Protocol):
    def load(self, period: str) -> list[LedgerEntry]: ...
