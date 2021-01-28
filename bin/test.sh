#!/usr/bin/env bash

# Run the tests of the repo.

set -eufo pipefail

(
    # Subshell, so we can cd without annoyances.
    cd $REPO_ROOT
    python -m tests
)
