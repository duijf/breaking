#!/usr/bin/env bash

# Launch a development shell for `breaking`:
#
#  - Find out the root of the repository relative to this file and makes
#    it available under $REPO_ROOT. (This is nice for any scripts, they
#    don't have to duplicate a bunch of logic.)
#  - Change directory to $REPO_ROOT.
#  - Launch the Nix dev environment in your default shell.

set -eufo pipefail

# NB: Does not follow symlinks.
export REPO_ROOT="$(realpath "$(dirname "$0")/..")"

cd "$REPO_ROOT"
nix-shell --command $SHELL
