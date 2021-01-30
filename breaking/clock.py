import time

from typing_extensions import Protocol


class Clock(Protocol):
    """Interface that all clocks must conform to."""

    def seconds_since_epoch(self) -> float:
        """Return the amount of seconds since clock epoch."""


class MonotonicClock:
    """Clock based on `time.monotonic()`"""

    def seconds_since_epoch(self) -> float:
        return time.monotonic()


class MockClock:
    """Clock that must be manually advanced for use in tests."""

    def __init__(self) -> None:
        self.time = 0.0

    def seconds_since_epoch(self) -> float:
        return self.time

    def advance_by(self, n: float) -> None:
        """Advance the clock by `n` seconds."""
        assert not n < 0, "Clock cannot go backwards"
        self.time += n
