# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Shared helpers for the Claude Code quality gates. Standard library only."""
import fnmatch
import hashlib
import json
import os
import shlex
import signal
import subprocess
import sys
import time
import tomllib
from pathlib import Path

QG_HOME = Path(os.environ.get("QG_HOME", Path.home() / ".claude" / "quality"))
TRUST_FILE = QG_HOME / "trusted.json"
TEMPLATES = "~/.claude/quality/templates/README.md"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
MISSING_TOOL = (126, 127)  # sh: not executable / command not found

# Principles, in the order Claude meets them. Each maps to a contract command;
# docs is always checked by the path trigger, docs_lint only adds to it.
PRINCIPLES = {
    "test": "TDD: write a failing test first, run it through qg-test, end with all tests green",
    "diff_coverage": "changed lines are covered by tests",
    "mutation": "tests kill mutants in the changed code",
    "docs": "user-visible changes are reflected in README, docs, CHANGELOG or ADRs",
}
CONTRACT_PRINCIPLES = ("test", "diff_coverage", "mutation")
DEFAULT_DOCS = ["*.md", "docs/**"]


def read_hook_input():
    return json.load(sys.stdin)


def git(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def repo_root(cwd):
    top = git(cwd, "rev-parse", "--show-toplevel")
    return Path(top).resolve() if top else None


def git_dir(root):
    return Path(git(root, "rev-parse", "--absolute-git-dir")).resolve()


def state_dir(root):
    d = git_dir(root) / "qg"
    d.mkdir(parents=True, exist_ok=True)
    return d


def contract_path(root):
    return root / ".quality" / "contract.toml"


def load_contract(root):
    p = contract_path(root)
    if not p.is_file():
        return None
    with p.open("rb") as f:
        return tomllib.load(f)


def command(contract, name):
    """The command string for a principle, or None when it is skipped or unwired."""
    v = (contract or {}).get("commands", {}).get(name)
    return v if isinstance(v, str) and v.strip() else None


def principles(contract):
    """[(name, status)] with status 'checked', 'skipped: <reason>' or 'unwired'."""
    out = []
    for name in CONTRACT_PRINCIPLES:
        v = contract.get("commands", {}).get(name)
        if command(contract, name):
            out.append((name, "checked"))
        elif isinstance(v, dict) and v.get("skip"):
            out.append((name, f"skipped: {v['skip']}"))
        else:
            out.append((name, "unwired"))
    out.append(("docs", "checked"))
    return out


def contract_files(root):
    qdir = root / ".quality"
    return sorted(p for p in qdir.rglob("*")
                  if p.is_file() and p.relative_to(qdir).parts[0] != "out")


def contract_hash(root):
    h = hashlib.sha256()
    for p in contract_files(root):
        h.update(p.relative_to(root).as_posix().encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()


def load_trust():
    try:
        return json.loads(TRUST_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def is_trusted(root):
    return load_trust().get(str(root)) == contract_hash(root)


def matches(rel, patterns):
    for p in patterns or []:
        if fnmatch.fnmatch(rel, p) or (p.startswith("**/") and fnmatch.fnmatch(rel, p[3:])):
            return True
    return False


def is_source(rel, contract):
    paths = contract.get("paths", {})
    return matches(rel, paths.get("source")) and not matches(rel, paths.get("tests"))


def merge_base(root, contract):
    base = (contract or {}).get("base", "origin/main")
    return (git(root, "merge-base", "HEAD", base)
            or git(root, "rev-parse", "--verify", "-q", "HEAD")
            or EMPTY_TREE)


def changed_files(root, base):
    tracked = git(root, "diff", "--name-only", base).splitlines()
    untracked = git(root, "ls-files", "--others", "--exclude-standard").splitlines()
    return sorted(set(filter(None, tracked + untracked))), untracked


def change_digest(root, base, untracked):
    h = hashlib.sha256(git(root, "diff", base).encode())
    for name in sorted(untracked):
        h.update(name.encode())
        try:
            h.update((root / name).read_bytes())
        except OSError:
            pass
    return h.hexdigest()


def render(cmd, base="", args=()):
    return cmd.replace("{base}", base).replace("{args}", " ".join(shlex.quote(a) for a in args))


def run_command(root, cmd, timeout=None, capture=True):
    """Run a contract command. On timeout, kill its whole process group and re-raise."""
    p = subprocess.Popen(cmd, shell=True, cwd=root, text=True,
                         stdout=subprocess.PIPE if capture else None,
                         stderr=subprocess.STDOUT if capture else None,
                         start_new_session=timeout is not None)
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.communicate()
        raise
    return p.returncode, out or ""


def tail(text, n=2500):
    return (text or "")[-n:]


def last_gate_path(root):
    return state_dir(root) / "last-gate.json"


def write_last_gate(root, digest, results):
    last_gate_path(root).write_text(json.dumps(
        {"ts": time.time(), "digest": digest, "results": results}, indent=2))


def open_items(root):
    """Principles the last Stop gate did not pass, as {name: result}."""
    try:
        results = json.loads(last_gate_path(root).read_text()).get("results", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return {k: v for k, v in results.items() if v not in ("pass", "skipped")}
