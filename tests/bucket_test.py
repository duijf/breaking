import math

import hypothesis.strategies as st
import pytest
from hypothesis import example, given

from breaking import MockClock, TokenBucket


def test_bucket_init_validation() -> None:
    with pytest.raises(ValueError):
        TokenBucket(capacity_max=0, restore_rate_hz=10)
    with pytest.raises(ValueError):
        TokenBucket(capacity_max=10, restore_rate_hz=-5)
    with pytest.raises(ValueError):
        TokenBucket(capacity_max=10, restore_rate_hz=math.nan)
    with pytest.raises(ValueError):
        TokenBucket(capacity_max=10, restore_rate_hz=math.inf)


@given(
    capacity_max=st.integers(min_value=1),
    restore_rate_hz=st.floats(
        min_value=1, allow_nan=False, allow_infinity=False
    ),
)
@example(capacity_max=2, restore_rate_hz=1.0)
@example(capacity_max=1, restore_rate_hz=1.0)
@example(capacity_max=1, restore_rate_hz=2.0)
def test_bucket_capacity_refils(
    capacity_max: int, restore_rate_hz: float
) -> None:
    clock = MockClock()
    bucket = TokenBucket(
        capacity_max=capacity_max, restore_rate_hz=restore_rate_hz, clock=clock
    )
    assert bucket.has_tokens_left()
    bucket.take(capacity_max)
    assert not bucket.has_tokens_left()
    clock.advance_by(1.0)
    assert bucket.has_tokens_left(min(capacity_max, int(restore_rate_hz)))


def test_bucket_does_not_refill_beyond_max_capacity() -> None:
    clock = MockClock()
    bucket = TokenBucket(capacity_max=50, restore_rate_hz=10000, clock=clock)
    clock.advance_by(2)
    bucket.take(50)
    assert not bucket.has_tokens_left()


def test_bucket_fill_clips_between_max_capacity() -> None:
    clock = MockClock()
    bucket = TokenBucket(capacity_max=50, restore_rate_hz=1, clock=clock)
    assert bucket.take(70) == 20
    assert not bucket.has_tokens_left()
    assert bucket.fill(70) == 20

    bucket.take(50)
    clock.advance_by(1)
    assert bucket.fill(50) == 1
