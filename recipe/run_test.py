error_message = "Error: Could not read git repo commit / details"

try:
    import __version__
except SystemExit as e:
    if not e.args[0] == error_message:
        raise

# Adapted from upstream tests
from subprocess import run
ret = run(['git-versioner'], capture_output=True)
o = ret.stdout.strip().decode()
e = ret.stderr.strip().decode()
assert not o, o
assert e == error_message, e
