import math
from dataclasses import dataclass, field

from breaking.clock import Clock, MonotonicClock


@dataclass
class TokenBucket:
    """
    Impose an upper bound on a number of events over a time interval.

    Use cases:

     - Rate limiting the number of requests for clients.
     - Circuit breaking after a certain number of exceptions have happened.

    ### How this works

    I will slowly build up to how token buckets work and why they are
    nice by showing other ways you could implement this (and
    limitations of those approaches).

    There are many related datastructures / algorithms in this space
    eith different trade-offs. What follows is a brief comparison
    between them.

    #### Fixed window counters

    Divide time in a series of buckets, and for each bucket keep track
    of the number of events that have happened.

    Example implementation using a `Dict[Time, Count]`:

    ```
    # An event happens at time `1612604808`
    { 1612604808: 1 }

    # Another event happens within the same second.
    { 1612604808: 2 }

    # Time moves forward into the next second.

    # A new event happens. Remove the counter for the previous
    # second and start anew.
    { 1612604808: 2, 1612604809: 1 }
      ^              ^ Limit checks now use this counter.
      Previous key. Will be deleted.
    ```

    Based on these counters, you can implement your rate limiting logic.
    Conceptually, this is very simple. However, there is a major limitation.

    **You can only consider event rates for the current
    bucket**. (Otherwise you would need to loop over the entire dict,
    which is inefficient). This introduces inaccuracies in counting
    when events happen when your buckets roll over.

    Consider:

    ```
    # We'd like to limit the number of requests to 10/second.

    # At `1612604808.95` (near the end of second `1612604808`), 10
    # requests come in.
    { 1612604808: 10 }

    # At `1612604809.05` (the beginning of second `1612604809`), 11
    # more requests come in.
    { 1612604808: 10, 1612604809: 10 }
      ^               ^ Used for comparison
      Not used anymore
    ```

    You conceptually had a rate limit of 10 requests / second. However
    at the second boundaries, you can actually allow up to 20 requests.

    #### Sliding window counter

    This is an approach to fix the inaccuracies above.

     - Store all event times in a sorted set, with millisecond accuracy.
     - When new events come in, add their time values to the new set.
     - Clean up all old requests from the set every second (this is fast
       because the set is sorted).

    This is more accurate, but trades accuracy for memory. Depending
    on the limits that you set, this could be a dealbreaker.

    #### Token buckets

    Token buckets are a way to fix the accuracy and the memory usage
    problems with the implementations above.

    Each bucket starts out full of tokens.

    ```
    |---| <- capacty_current, capacity_max
    |   |
    |   |
    |___|
    ```

    When events happen, the current capcaity is decremented:

    ```
    |   | <- capacity_max
    |   |
    |---| <- capacity_current
    |___|
    ```

    When the bucket runs out of tokens, no new events are allowed:

    ```
    |   | <- capacity_max
    |   |
    |   |
    |___| <- capacity_current
    ```

    Over time, the capacity is restored at `restore_rate_hz`, and
    new events are allowed again:

    ```
    |   | <- capacity_max
    |---| <- capacity_current
    |   |
    |___|
    ```

    By keeping track of the `last_restore` time, we can perform this
    restoration calcuation every time we try to take from the bucket.

    We get the full accuracy offered by the sorted set, but with less
    memory requirements. Nice.

    (This class also has a `fill()` operation, which is helpful when
    implementing circuit breakers.)

    #### Leaky Buckets

    **Token buckets and leaky buckets have different goals and usecases.**
    But since they appear very similar on the surface, I'm mentioning them
    for completeness.

    Both leaky and token buckets contain a backpressure mechanism, but
    they have different goals:

     - Leaky buckets turn bursty streams of events into a stream of
       constant rate.
     - Token buckets make sure no more than `X` events happen over a
       certain time window. The resulting stream has an upper bound on
       the number of elements, but is still allowed to be bursty.

    Or more concretely:

     - Leaky buckets buffer requests and output them at a steady rate. Limits
       are imposed when the buffer is full.
     - Token buckets allow reqeusts immediately. Limits are imposed when more
       than X requests happen in a period of time.

    Here is a table which compares the two:

    | bucket type             | token                  | leaky              |
    |-------------------------|------------------------|--------------------|
    | goal                    | impose upper bound     | control burstiness |
    | requests happen         | immediately            | at leak rate       |
    | backpressure when       | empty                  | full               |
    | analogous datastructure | replenishing semaphore | bounded queue      |

    """

    capacity_max: int = field()
    capacity_current: int = field(init=False)

    restore_rate_hz: float = field()
    """How much capacity should be restored every second?"""
    last_restore: float = field(init=False)
    """Time the last capacity restore took place."""

    clock: Clock = field(default_factory=MonotonicClock)
    """Clock implementation to use.

    This is configurable because to facilitate testing the behavior of
    this class without waiting for actual time to pass. See `breaking.clock`
    for further details."""

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
        assert n >= 1, "`n` must be >= 1"

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
        assert n >= 1, "`n` must be >= 1"

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
