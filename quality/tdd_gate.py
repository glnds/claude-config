# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""PreToolUse: protect gate files and enforce red-before-green on source files."""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qglib as q  # noqa: E402


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason}}))
    sys.exit(0)


data = q.read_hook_input()
ti = data.get("tool_input") or {}
target = ti.get("file_path") or ti.get("notebook_path")
if not target:
    sys.exit(0)
path = (Path(data.get("cwd", ".")) / target).resolve()

if path.is_relative_to(q.QG_HOME.resolve()):
    decide("deny", "The quality gate scripts are not editable by Claude.")

probe = path.parent
while not probe.exists():
    probe = probe.parent
root = q.repo_root(probe)
if root is None or not path.is_relative_to(root):
    sys.exit(0)
if path.is_relative_to(q.git_dir(root) / "qg"):
    decide("deny", "The quality gate state is not editable by Claude.")

rel = path.relative_to(root).as_posix()
if rel.startswith(".quality/") and not rel.startswith(".quality/out/"):
    decide("ask", "Changing .quality/ changes the quality gate. It needs human review and re-approval with qg-trust.")

contract = q.load_contract(root)
if contract is None or q.command(contract, "test") is None:  # no contract, or TDD skipped/unwired
    sys.exit(0)
mode = os.environ.get("QG_TDD", "on")
if mode == "off":
    with (q.state_dir(root) / "bypass.log").open("a") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {data.get('session_id')} {rel}\n")
    sys.exit(0)
if not q.is_source(rel, contract):
    sys.exit(0)

state = q.state_dir(root) / "tdd.json"
last = json.loads(state.read_text()).get("last_run") if state.exists() else None
if last == "red":
    sys.exit(0)
if last == "green":
    decide("deny" if mode == "strict" else "ask",
           f"TDD: tests are green. Editing {rel} is only allowed as a refactor without new behaviour. "
           "For new behaviour, write a failing test and run it with ~/.claude/quality/qg-test first.")
decide("deny", f"TDD: no failing test recorded in this session. Write or extend a test for the behaviour "
               f"you want, run ~/.claude/quality/qg-test to see it fail, then edit {rel}.")
