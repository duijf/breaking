#!/usr/bin/env python
from __future__ import annotations

import enum
import os
import subprocess
import sys
from typing import List


class Mode(enum.Enum):
    BUILD = "--build"
    SERVE = "--serve"

    @classmethod
    def from_cli(cls, cli_args: List[str]) -> Mode:
        arg_mode = cli_args[0] if len(cli_args) >= 1 else "--serve"
        return cls(arg_mode)


repo_root = os.environ["REPO_ROOT"]
docs_root = f"{repo_root}/breaking"
mode = Mode.from_cli(sys.argv[1:])

if mode == Mode.SERVE:
    subprocess.run(["pdoc", docs_root])
elif mode == Mode.BUILD:
    subprocess.run(["pdoc", "--output-directory", "docs", docs_root])
