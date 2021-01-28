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
import pathlib
import subprocess
import sys
from typing import List


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
    except subprocess.CalledProcessError:
        sys.exit(1)


def run_lints(mode: Mode) -> None:
    repo_root = os.environ["REPO_ROOT"]
    check_mode = mode == Mode.CHECK
    extra_args = ["--check", "--diff"] if check_mode else []

    run_lint(["black", "--quiet", repo_root] + extra_args)
    run_lint(["isort", "--skip-gitignore", repo_root] + extra_args)
    run_lint(["flake8", repo_root])
    run_lint(["mypy", "--strict", repo_root])


def install_git_hook() -> None:
    script_contents = "/usr/bin/env bash\n" "$REPO_ROOT/bin/pre-commit.py\n"

    repo_root = pathlib.Path(os.environ["REPO_ROOT"])
    script_file = repo_root / ".git" / "hooks" / "pre-commit"

    with script_file.open(mode="w") as f:
        f.write(script_contents)

    # Make the script executable, respecting permissions that were
    # previously there.
    current_perms = script_file.stat().st_mode
    script_file.chmod(current_perms + 0o111)


def main() -> None:
    mode = Mode.from_cli(sys.argv[1:])

    if mode == Mode.INSTALL:
        install_git_hook()
    else:
        run_lints(mode)


if __name__ == "__main__":
    main()
