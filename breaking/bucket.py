from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LeakyBucket:
    capacity_max: int
    drain_rate_hz: int
    capacity_cur: int = field(default=0, init=False)
    last_drain: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )

    def has_capacity(self, n: int = 1) -> bool:
        self._update_capacities()
        return self.capacity_cur + n <= self.capacity_max

    def fill(self, n: int = 1) -> None:
        self._update_capacities()
        assert self.capacity_cur + n <= self.capacity_max
        self.capacity_cur += n

    def _update_capacities(self) -> None:
        now = datetime.now(timezone.utc)
        seconds_since_last_drain = int((now - self.last_drain).total_seconds())
        capacity_to_refill = min(seconds_since_last_drain * self.drain_rate_hz, self.capacity_max)
        self.capacity_cur = max(self.capacity_cur - capacity_to_refill, 0)
        self.last_drain = now
