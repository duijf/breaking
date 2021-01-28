from breaking.bucket import LeakyBucket


def test_bucket_capacity() -> None:
    bucket = LeakyBucket(capacity_max=50, drain_rate_hz=10)
    assert bucket.has_capacity()
