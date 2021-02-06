"""
A clock interface and implementations.

## Why?

It's tricky to test software that relies on clocks without controlling the
passage of time yourself. Race conditions can be hard to reliably trigger
or write regression tests for. And even in the simplest cases, there is the
question of performance: you don't want to make your test suite take a minute
just because you want to `time.sleep(60)` somewhere.

This clock interface makes it easy for us to test the logic of
`breaking.bucket.TokenBucket` and `breaking.breaker.CircuitBreaker`. Both
classes accept a `clock` parameter which implements the `Clock` protocol.
Depending on the implementation we pass, we can choose whether we're checking
actual system clock, or just a test version. This pattern is called "dependency
injection".
"""
import time

from typing_extensions import Protocol


class Clock(Protocol):
    """Interface that all clocks must conform to.

    You will get a `TypeError` if you try to instantiate this class. This is
    a `typing_extensions.Protocol`, which you can think of as an abstract base
    class.
    """

    def seconds_since_epoch(self) -> float:
        """Return the amount of seconds since clock epoch."""


class MonotonicClock:
    """Clock based on `time.monotonic()`"""

    def seconds_since_epoch(self) -> float:
        """Returns `time.monotonic()`"""
        return time.monotonic()


class MockClock:
    """Clock that must be manually advanced for use in tests."""

    def __init__(self) -> None:
        self.time = 0.0

    def seconds_since_epoch(self) -> float:
        """Return the stored time value.

        This value does not increase by itself. You have to manually call
        `MockClock.advance_by()` in order to move this clock forward in time.
        """
        return self.time

    def advance_by(self, n: float) -> None:
        """Advance the clock by `n` seconds."""
        assert not n < 0, "Clock cannot go backwards"
        self.time += n
