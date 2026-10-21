# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Shared helpers for the Claude Code quality gates. Standard library only."""
import fnmatch
import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
import tomllib
from datetime import date
from pathlib import Path

QG_HOME = Path(os.environ.get("QG_HOME", Path.home() / ".claude" / "quality"))
TRUST_FILE = QG_HOME / "trusted.json"
TRUST_KEEP = 20  # approved .quality/ versions remembered per repository
TEMPLATES = "~/.claude/quality/templates/README.md"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
MISSING_TOOL = (126, 127)  # sh: not executable / command not found
# Wrappers report a missing tool with their own exit code (uv run: 2), so match their messages too.
MISSING_TOOL_RE = re.compile(r"Failed to spawn|command not found|could not determine executable to run"
                             r"|error: no such command|executable file not found")

# Principles, in the order Claude meets them. Each maps to a contract command;
# docs is always checked by the path trigger, docs_lint only adds to it.
PRINCIPLES = {
    "test": "TDD: write a failing test first, run it through qg-test, end with all tests green",
    "diff_coverage": "changed lines are covered by tests",
    "mutation": "tests kill mutants in the changed code",
    "docs": "user-visible changes are reflected in README, docs, CHANGELOG or ADRs",
}
CONTRACT_PRINCIPLES = ("test", "diff_coverage", "mutation")
SKIP_MAX_DAYS = 90
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


def today():
    return date.fromisoformat(os.environ["QG_TODAY"]) if os.environ.get("QG_TODAY") else date.today()


def skip_state(reason, until, what="skip"):
    """(kind, label) for a skip: kind is 'skipped', 'expired' or 'undated'. Skips are debt, so
    they must expire within SKIP_MAX_DAYS; an expired or undated skip counts as unwired."""
    try:
        d = until if isinstance(until, date) else date.fromisoformat(str(until)) if until else None
    except ValueError:
        d = None
    if d is None:
        return "undated", f"undated {what}: {reason}"
    if d < today():
        return "expired", f"{what} expired on {d}: {reason}"
    if (d - today()).days > SKIP_MAX_DAYS:
        return "undated", f"undated {what}: {reason} (until {d} is more than {SKIP_MAX_DAYS} days out)"
    return "skipped", f"{'skipped' if what == 'skip' else what} until {d}: {reason}"


def principles(contract):
    """[(name, kind, label)]; kind is checked, skipped, expired, undated or unwired."""
    out = []
    for name in CONTRACT_PRINCIPLES:
        v = contract.get("commands", {}).get(name)
        if command(contract, name):
            out.append((name, "checked", "checked"))
        elif isinstance(v, dict) and v.get("skip"):
            out.append((name, *skip_state(v["skip"], v.get("until"))))
        else:
            out.append((name, "unwired", "unwired"))
    out.append(("docs", "checked", "checked"))
    return out


def partial_skip(contract):
    """(kind, label, paths) for `[mutation] skip_paths`, or None. Changes only in these paths do
    not trigger mutation testing until the skip expires."""
    sp = (contract or {}).get("mutation", {}).get("skip_paths")
    if not isinstance(sp, dict) or not sp.get("paths"):
        return None
    paths = list(sp["paths"])
    kind, label = skip_state(f"{', '.join(paths)} ({sp.get('reason', 'no reason given')})",
                             sp.get("until"), "partial skip")
    return kind, label, paths


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


def repo_key(root):
    """Trust key shared by all worktrees of a repository: its common Git directory."""
    common = git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return str(Path(common).resolve()) if common else str(root)


def approved_hashes(trust, root):
    """Every .quality/ version a human approved for this repository. Entries keyed by the
    worktree path (the format before repo keys) still count."""
    out = set()
    for key in (repo_key(root), str(root)):
        v = trust.get(key)
        out.update(v if isinstance(v, list) else [v] if v else [])
    return out


def is_trusted(root):
    return contract_hash(root) in approved_hashes(load_trust(), root)


def approve(root):
    """Record the current .quality/ version as approved for this repository (qg-trust only)."""
    trust, key, h = load_trust(), repo_key(root), contract_hash(root)
    v = trust.get(key)
    hashes = [x for x in (v if isinstance(v, list) else [v] if v else []) if x != h]
    trust[key] = (hashes + [h])[-TRUST_KEEP:]
    TRUST_FILE.write_text(json.dumps(trust, indent=2, sort_keys=True))


def matches(rel, patterns):
    for p in patterns or []:
        if fnmatch.fnmatch(rel, p) or (p.startswith("**/") and fnmatch.fnmatch(rel, p[3:])):
            return True
    return False


def is_source(rel, contract):
    paths = contract.get("paths", {})
    return matches(rel, paths.get("source")) and not matches(rel, paths.get("tests"))


def default_base(root):
    """The remote's default branch. origin/HEAD is only set by `git clone`, hence the fallbacks."""
    head = git(root, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD")
    if head:
        return head
    for ref in ("origin/main", "origin/master"):
        if git(root, "rev-parse", "--verify", "-q", ref):
            return ref
    return "HEAD"


def session_head_path(root, session_id):
    return state_dir(root) / f"session-{session_id}.head"


def record_session_head(root, session_id, overwrite):
    p = session_head_path(root, session_id)
    head = git(root, "rev-parse", "--verify", "-q", "HEAD")
    if session_id and head and (overwrite or not p.exists()):
        p.write_text(head)


def merge_base(root, contract, session_id=None):
    """Merge-base of HEAD and `base`, moved back to the session's start HEAD when that is older,
    so work committed or pushed during the session stays in the change set."""
    base = (contract or {}).get("base") or default_base(root)
    mb = (git(root, "merge-base", "HEAD", base)
          or git(root, "rev-parse", "--verify", "-q", "HEAD")
          or EMPTY_TREE)
    p = session_head_path(root, session_id) if session_id else None
    if p and p.exists() and mb != EMPTY_TREE:
        mb = git(root, "merge-base", mb, p.read_text().strip()) or mb
    return mb


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


def mutation_report(root, contract):
    return root / contract.get("mutation", {}).get("report", ".quality/out/mutation.json")


def mutation_verdict(root, contract):
    """("pass" | "fail", finding or "") from the normalised mutation report."""
    m = contract.get("mutation", {})
    try:
        stats = json.loads(mutation_report(root, contract).read_text())
        killed, survived = int(stats["killed"]), int(stats["survived"])
    except (OSError, ValueError, KeyError) as e:
        return "fail", f"Mutation report missing or invalid ({e}). Check the contract's `mutation` command."
    total, threshold = killed + survived, float(m.get("threshold", 0.8))
    if total and killed / total < threshold:
        survivors = "\n".join(stats.get("survivors", [])[:30])
        return "fail", (f"Mutation score {killed / total:.0%} is below {threshold:.0%} "
                        f"({survived} of {total} mutants survived). Strengthen the assertions "
                        f"so the tests fail for these mutants:\n{survivors}")
    return "pass", ""


def mutation_stage(contract):
    """Where mutation testing runs: "stop" (the Stop gate, default) or "pre-push" (`qg-mutation`)."""
    return contract.get("mutation", {}).get("stage", "stop")


def missing_tool(rc, out):
    return rc in MISSING_TOOL or (rc != 0 and bool(MISSING_TOOL_RE.search(tail(out, 4000))))


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
