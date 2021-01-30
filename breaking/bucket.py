import math
from dataclasses import dataclass, field

from breaking.clock import Clock, MonotonicClock


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
    last_restore: float = field(init=False)

    clock: Clock = field(default_factory=MonotonicClock)

    def __post_init__(self) -> None:
        self.last_restore = self.clock.seconds_since_epoch()
        self.capacity_current = self.capacity_max

        if self.capacity_max < 1:
            raise ValueError("capacity_max must be >= 1")

        if self.restore_rate_hz < 1:
            raise ValueError("restore_rate_hz must be >= 1")

        if math.isnan(self.restore_rate_hz):
            raise ValueError("restore_rate_hz cannot be NaN")

        if math.isinf(self.restore_rate_hz):
            raise ValueError("restore_rate_hz cannot be Inf")

    def has_tokens_left(self, n: int = 1) -> bool:
        """
        Does the bucket have capacity for `n` more items?
        """
        self._update()
        return self.capacity_current - n >= 0

    def take(self, n: int = 1) -> None:
        """
        Take `n` items from the bucket.

        It is the responsibility of the caller to check whether the bucket has
        enough tokens to take first. Otherwise, the caller risks being thrown
        exceptions.

        Raises
          ValueError - when the bucket does not have enough tokens to take.
        """
        self._update()
        if self.capacity_current - n < 0:
            raise ValueError("Tried filling more than bucket capacity")
        self.capacity_current -= n

    def _update(self) -> None:
        """
        Update the current capacity based on the restore rate.
        """
        now = self.clock.seconds_since_epoch()
        seconds_since_last_drain = now - self.last_restore

        capacity_to_restore = min(
            int(seconds_since_last_drain * self.restore_rate_hz),
            self.capacity_max,
        )
        self.capacity_current = min(
            self.capacity_current + capacity_to_restore, self.capacity_max
        )
        self.last_restore = now
