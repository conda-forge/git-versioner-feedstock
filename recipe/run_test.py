# Adapted from upstream tests
import os
import sys
import tempfile
from subprocess import run
from pathlib import Path


def version(cwd, *args):
    proc = run(
        ['git-versioner', *args],
        capture_output=True,
        cwd=cwd,
        env=os.environ,
    )
    ret = proc.stdout.strip().decode(), proc.stderr.strip().decode()
    print(*ret)
    return ret


def shell(cmd, cwd, verbose=False):
    proc = run(cmd, cwd=cwd, shell=True, capture_output=True)
    if verbose:
        print(proc.stdout.strip().decode(), proc.stderr.strip().decode())

def no_shell(cmd, cwd, verbose=False):
    proc = run(cmd, cwd=cwd, capture_output=True)
    if verbose:
        print(proc.stdout.strip().decode(), proc.stderr.strip().decode())


with tempfile.TemporaryDirectory() as tdir:
    o, e = version(tdir)
    assert not e
    assert o == ("v0.0-new"), o

    no_shell(["git", "init"], cwd=tdir)
    no_shell(["git", "config", "user.email", "gitlab@version.com"], cwd=tdir)
    no_shell(["git", "config", "user.name", "Gitlab CI"], cwd=tdir)

    o, e = version(tdir)
    assert not e
    assert o == ("v0.0-new"), o
    
    (Path(tdir) / "file").write_text("initial")
    no_shell(["git", "add", "file"], cwd=tdir, verbose=True)
    no_shell(["git", "commit", "-m", "initial"], cwd=tdir, verbose=True)

    o, e = version(tdir)
    assert not e
    assert o.startswith("v0.1-g")

    (Path(tdir) / "file").write_text("change")
    o, e = version(tdir)
    assert o.endswith("-dirty")

    no_shell(["git", "add", "file"], cwd=tdir)
    no_shell(["git", "commit", "-m", f"update{os.linesep}CHANGE: patch"], cwd=tdir)
    o, e = version(tdir)
    assert o.startswith("v0.0.1-g")
    o, e = version(tdir, "--short")
    assert o == "v0.0.1"
    # assert e == "Increment 'patch' not currently supported"

    shell("git tag v1.0-beta1", cwd=tdir)
    o, e = version(tdir)
    assert o == ("v1.0-beta1")
    o, e = version(tdir, "--python")
    assert o == ("1.0+beta1")

    (Path(tdir) / "file").write_text("update")
    o, e = version(tdir)
    assert o.startswith("v1.1-g")
    assert o.endswith("-dirty")
    o, e = version(tdir, "--python")
    assert o.startswith("1.1+g")
    assert o.endswith(".dirty")

    no_shell(["git", "add", "file"], cwd=tdir)
    no_shell(["git", "commit", "-m", "update"], cwd=tdir)
    o, e = version(tdir)
    assert o.startswith("v1.1-g")
    assert not o.endswith("-dirty")
    o, e = version(tdir, "--python")
    assert o.startswith("1.1+g")

    (Path(tdir) / "file").write_text("change")
    no_shell(["git", "add", "file"], cwd=tdir)
    no_shell(["git", "commit", "-m", "initial"], cwd=tdir)

    os.environ["VERSION_INCREMENT"] = "major"
    o, e = version(tdir)
    assert not e
    assert o.startswith("v2.0-g")

    del os.environ["VERSION_INCREMENT"]
    o, e = version(tdir)
    assert o.startswith("v1.1-g")

    (Path(tdir) / "file").write_text("major")
    no_shell(["git", "add", "file"], cwd=tdir)
    no_shell(["git", "commit", "-m", f"update{os.linesep}CHANGE: major"], cwd=tdir)
    o, e = version(tdir)
    assert o.startswith("v2.0-g")

    (Path(tdir) / "file").write_text("minor")
    no_shell(["git", "add", "file"], cwd=tdir)
    no_shell(["git", "commit", "-m", f"update{os.linesep}CHANGE: minor"], cwd=tdir)
    o, e = version(tdir)
    # should still be major change because that's in the
    # history since last tag
    assert o.startswith("v2.0-g")

    # create the tag
    o, e = version(tdir, "--tag")
    # check still correct
    o, e = version(tdir)
    assert o == "v2.0"
    o, e = version(tdir, "--python")
    assert o == "2.0"


print("Test Passed")
