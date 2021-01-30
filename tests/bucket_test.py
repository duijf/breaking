import math
import time

import hypothesis.strategies as st
import pytest
from hypothesis import example, given

from breaking.bucket import TokenBucket


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
def test_bucket_capacity_refils(
    capacity_max: int, restore_rate_hz: float
) -> None:
    bucket = TokenBucket(
        capacity_max=capacity_max, restore_rate_hz=restore_rate_hz
    )
    assert bucket.has_capacity()
    bucket.fill(capacity_max)
    assert not bucket.has_capacity()
    time.sleep(1)
    assert bucket.has_capacity(int(restore_rate_hz))


def test_bucket_does_not_refill_beyond_max_capacity() -> None:
    bucket = TokenBucket(capacity_max=50, restore_rate_hz=10000)
    time.sleep(2)
    bucket.fill(50)
    assert not bucket.has_capacity()


def test_bucket_fill_more_than_capacity() -> None:
    bucket = TokenBucket(capacity_max=50, restore_rate_hz=1)
    with pytest.raises(ValueError):
        bucket.fill(100)
