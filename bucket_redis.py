#!/usr/bin/env python
import time
from dataclasses import dataclass
from typing import Tuple

import redis

REDIS = redis.Redis(unix_socket_path="ignore/redis/redis.sock")

TOKEN_BUCKET_LUA = """
redis.replicate_commands()

local capacity_current_key = KEYS[1]
local last_restore_key = KEYS[2]

local capacity_max = ARGV[1]
local restore_rate_hz = ARGV[2]
local n = ARGV[3]

-- This returns a Lua table of two strings: [seconds, microseconds]
local now = redis.call("TIME")
now = tonumber(now[1]) + (tonumber(now[2]) / 1000000)

local last_restore = tonumber(redis.call("GET", last_restore_key)) or now
local capacity_current = redis.call("GET", capacity_current_key)
    or capacity_max

local seconds_since_last_restore = now - last_restore
local capacity_to_restore = math.floor(
    seconds_since_last_restore * restore_rate_hz
)

capacity_current = math.min(
    capacity_current + capacity_to_restore,
    capacity_max
)
local has_capacity_left = capacity_current - n >= 0

if not has_capacity_left then
    return {0, false}
end

capacity_current = capacity_current - n

-- TODO: Key expiration.
redis.call("SET", capacity_current_key, capacity_current)
redis.call("SET", last_restore_key, now)

return {capacity_current, has_capacity_left}
"""
TOKEN_BUCKET_SCRIPT = REDIS.register_script(TOKEN_BUCKET_LUA)  # type: ignore


@dataclass()
class RedisBucket:
    key_name_base: str
    capacity_max: int
    restore_rate_hz: float

    def has_tokens_left(self, n: int = 1) -> bool:
        # Just check whether there are still tokens left. Do not decrement
        # the counter in redis.
        capacity_current, _ = self._call_redis_script(
            self.capacity_max, self.restore_rate_hz, 0
        )
        return capacity_current - n >= 0

    def take(self, n: int = 1) -> None:
        _, has_capacity_left = self._call_redis_script(
            self.capacity_max, self.restore_rate_hz, n
        )

        if not has_capacity_left:
            raise ValueError("Tried taking more than bucket capacity")

    def _call_redis_script(
        self, capacity_max: int, restore_rate_hz: float, n: int
    ) -> Tuple[int, bool]:
        capacity_current_key = f"{self.key_name_base}_capacity_current"
        last_restore_key = f"{self.key_name_base}_last_restore"

        capacity_current, has_capacity_left = TOKEN_BUCKET_SCRIPT(
            keys=[capacity_current_key, last_restore_key],
            args=[capacity_max, restore_rate_hz, n],
        )

        # Deserialize the Redis encoded Lua booleans. 1 is True, None
        # is False. Anything else means we have a bug in our code.
        if has_capacity_left == 1:
            has_capacity_left = True
        elif has_capacity_left is None:
            has_capacity_left = False
        else:
            raise ValueError("Received unexpected reply from Redis")

        assert isinstance(capacity_current, int)
        assert isinstance(has_capacity_left, bool)

        return capacity_current, has_capacity_left


bucket = RedisBucket(key_name_base="asdf", capacity_max=10, restore_rate_hz=1)
assert bucket.has_tokens_left(), "Bucket should start with tokens left"
bucket.take(10)
assert not bucket.has_tokens_left(), "Bucket shouldn't have any tokens left"
time.sleep(1)
assert bucket.has_tokens_left(), "Bucket should have replenished tokens"
