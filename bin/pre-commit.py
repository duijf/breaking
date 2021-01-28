#!/usr/bin/env python
"""
Run lints before making commits.

USAGE

Run all lints, fixing any found problems automatically when
appropriate.

    ./pre-commit.py

Run all lints. Only report errors, don't fix them.

     ./pre-commit.py --check

Install this script as a pre-commit hook.

     ./pre-commit.py --install
"""

from __future__ import annotations

import enum
import os
import subprocess
import sys


class Mode(enum.Enum):
    FIX = "--fix"
    CHECK = "--check"
    INSTALL = "--install"

    def from_cli(cli_args: List[str]) -> Mode:
        arg_mode = cli_args[0] if len(cli_args) >= 1 else "--fix"
        return Mode(arg_mode)


def run_lint(command: List[str]) -> None:
    print(f"==> {command[0]}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(1)


def run_lints(mode: Mode) -> None:
    repo_root = os.environ["REPO_ROOT"]
    check_mode = mode == Mode.CHECK
    extra_args = ["--check", "--diff"] if check_mode else []

    run_lint(["black", "--quiet", repo_root] + extra_args)
    run_lint(["isort", "--skip-gitignore", repo_root] + extra_args)
    run_lint(["mypy", repo_root])


def main() -> None:
    mode = Mode.from_cli(sys.argv[1:])

    if mode == Mode.INSTALL:
        raise NotImplementedError
    else:
        run_lints(mode)


if __name__ == "__main__":
    main()
