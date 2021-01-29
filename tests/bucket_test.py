import time

import pytest

from breaking.bucket import TokenBucket


def test_bucket_capacity_refils() -> None:
    bucket = TokenBucket(capacity_max=50, restore_rate_hz=10)
    assert bucket.has_capacity()
    bucket.fill(50)
    assert not bucket.has_capacity()
    time.sleep(1)
    assert bucket.has_capacity()


def test_bucket_does_not_refill_beyond_max_capacity() -> None:
    bucket = TokenBucket(capacity_max=50, restore_rate_hz=10000)
    time.sleep(2)
    bucket.fill(50)
    assert not bucket.has_capacity()


def test_bucket_fill_more_than_capacity() -> None:
    bucket = TokenBucket(capacity_max=50, restore_rate_hz=1)
    with pytest.raises(ValueError):
        bucket.fill(100)
