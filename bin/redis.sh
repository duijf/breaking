#!/usr/bin/env bash
set -eufo pipefail

# Run Redis and pass the configuration on stdin. This allows us to
# use environment variables in the Redis config file (normally,
# these aren't supported).
envsubst < "$REPO_ROOT/config/redis.conf.envsubst" | redis-server -
