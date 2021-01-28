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
        # Update the capacity calculation.
        now = datetime.now(timezone.utc)
        seconds_since_last_drain = int((now - self.last_drain).total_seconds())
        self.capacity_cur = self.capacity_cur - min(
            seconds_since_last_drain * self.drain_rate_hz, self.capacity_max
        )
        self.last_drain = now

        return self.capacity_cur + n <= self.capacity_max
