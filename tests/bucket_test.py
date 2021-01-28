import time

from breaking.bucket import LeakyBucket


def test_bucket_capacity_refils() -> None:
    bucket = LeakyBucket(capacity_max=50, drain_rate_hz=10)
    assert bucket.has_capacity()
    bucket.fill(50)
    assert not bucket.has_capacity()
    time.sleep(1)
    assert bucket.has_capacity()


def test_bucket_does_not_refill_beyond_max_capacity() -> None:
    bucket = LeakyBucket(capacity_max=50, drain_rate_hz=10000)
    time.sleep(2)
    bucket.fill(50)
    assert not bucket.has_capacity()
