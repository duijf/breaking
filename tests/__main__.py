import subprocess
import sys

subprocess.run(["pytest"] + sys.argv[1:])
