from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TokenBucket:
    """
    Impose an upper bound on a number of events over a time interval.

    USE CASES

     - Rate limiting the number of requests for clients.
     - Circuit breaking after a certain number of exceptions have happened.

    BEHAVIOR

     - At most `capacity_max` events can happen at once.
     - When events happen, `capacity_current` is decremented.
     - When `capacity_current` is `0`, there is no more capacity for extra
       events.
     - Capacity is restored at a rate of `restore_rate_hz`. The bucket
       keeps track of when this last happens and restores as appropriate.

    N.B. You might also have heard of a "leaky bucket". Here's a brief
    comparison between a leaky and a token bucket:

     - Leaky buckets take a bursty stream of events and output them at a
       constant rate.
     - Token buckets take a (potentially bursty) stream of events and impose
       a maximum on the amount of burstiness.
    """

    capacity_max: int = field()
    capacity_current: int = field(init=False)

    restore_rate_hz: float = field()
    last_restore: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )

    def __post_init__(self) -> None:
        self.capacity_current = self.capacity_max

    def has_capacity(self, n: int = 1) -> bool:
        """
        Does the bucket have capacity for `n` more items?
        """
        self._update()
        return self.capacity_current - n > 0

    def fill(self, n: int = 1) -> None:
        """
        Fill the bucket with `n` extra items.

        It is the responsibility of the caller to check whether the bucket has
        enough capacity first. Otherwise, the caller risks being thrown
        exceptions.

        Raises
          ValueError - when the bucket does not have enough capacity to store
            `n` extra values.
        """
        self._update()
        if self.capacity_current - n < 0:
            raise ValueError("Tried filling more than bucket capacity")
        self.capacity_current -= n

    def _update(self) -> None:
        """
        Update the current capacity based on the restore rate.
        """
        now = datetime.now(timezone.utc)
        seconds_since_last_drain = int(
            (now - self.last_restore).total_seconds()
        )
        capacity_to_restore = min(
            int(seconds_since_last_drain * self.restore_rate_hz),
            self.capacity_max,
        )
        self.capacity_current = min(
            self.capacity_current + capacity_to_restore, self.capacity_max
        )
        self.last_restore = now
