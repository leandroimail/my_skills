"""Imports orders from the partner API into the local repository."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: str
    total_cents: int
    currency: str


@dataclass(frozen=True)
class SyncResult:
    fetched: int
    saved: int
    skipped: int


class OrderSync:
    def __init__(self, client, repo):
        self._client = client  # HTTP client for the partner API: fetch_orders(since=...) -> list[dict]
        self._repo = repo      # database repository: exists(order_id) -> bool, save_many(list[Order])

    def run(self, since: str) -> SyncResult:
        raw = self._client.fetch_orders(since=since)
        orders = [self._normalize(r) for r in raw if r.get("status") != "cancelled"]
        new = [o for o in orders if not self._repo.exists(o.id)]
        if new:
            self._repo.save_many(new)
        return SyncResult(fetched=len(raw), saved=len(new), skipped=len(raw) - len(new))

    def _normalize(self, raw: dict) -> Order:
        return Order(
            id=str(raw["id"]).strip(),
            total_cents=round(float(raw["total"]) * 100),
            currency=raw.get("currency", "BRL").upper(),
        )
