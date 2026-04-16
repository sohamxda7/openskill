import os
import subprocess


BASE_VERSION = "0.1.0"


def _run_git(*args):
    try:
        return (
            subprocess.check_output(args, stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return None


def _from_env():
    version = os.environ.get("OPENSKILL_BUILD_VERSION")
    if version:
        return version
    ref_name = os.environ.get("GITHUB_REF_NAME", "")
    if ref_name.startswith("v"):
        return ref_name[1:]
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        return "%s.dev0+g%s" % (BASE_VERSION, sha[:7].lower())
    return None


def _from_git():
    tag = _run_git("git", "describe", "--tags", "--exact-match")
    if tag and tag.startswith("v"):
        return tag[1:]
    sha = _run_git("git", "rev-parse", "--short", "HEAD")
    if sha:
        return "%s.dev0+g%s" % (BASE_VERSION, sha.lower())
    return None


__version__ = _from_env() or _from_git() or BASE_VERSION
