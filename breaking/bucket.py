from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TokenBucket:
    capacity: int
    drain_rate_hz: int
    current: int = field(default=0, init=False)
    last_drain: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )

    def has_capacity(self, n: int = 1) -> bool:
        self._update()
        return self.current + n <= self.capacity

    def fill(self, n: int = 1) -> None:
        self._update()
        if self.capacity < self.current + n:
            raise ValueError("Tried filling more than bucket capacity")
        self.current += n

    def _update(self) -> None:
        now = datetime.now(timezone.utc)
        seconds_since_last_drain = int((now - self.last_drain).total_seconds())
        capacity_to_refill = min(
            seconds_since_last_drain * self.drain_rate_hz, self.capacity
        )
        self.current = max(self.current - capacity_to_refill, 0)
        self.last_drain = now
