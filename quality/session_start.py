# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""SessionStart: reset TDD state and tell Claude which principles this repository holds it to."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qglib as q  # noqa: E402


def emit(msg):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}}))
    sys.exit(0)


data = q.read_hook_input()
root = q.repo_root(data.get("cwd", "."))
if root is None:
    sys.exit(0)
fresh = data.get("source") in ("startup", "clear")  # resume, compact and fork keep their state
if fresh:
    (q.state_dir(root) / "tdd.json").unlink(missing_ok=True)
q.record_session_head(root, data.get("session_id"), overwrite=fresh)

contract = q.load_contract(root)
if contract is None:
    emit("Quality principles: TDD, tests for changed lines, mutation testing, up-to-date docs. "
         "This repository has no .quality/contract.toml yet. If you change code, propose one to "
         f"the user for this stack (see {q.TEMPLATES}).")

lines = ["Quality principles for this repository (.quality/contract.toml):"]
hints = {"unwired": f" -> wire up a check ({q.TEMPLATES}) or record a dated skip",
         "expired": " -> wire up the check, or renew the skip if the reason still holds",
         "undated": f" -> skips must expire: set `until` within {q.SKIP_MAX_DAYS} days"}
for name, kind, label in q.principles(contract):
    lines.append(f"- [{label}] {name}: {q.PRINCIPLES[name]}{hints.get(kind, '')}")
partial = q.partial_skip(contract)
if partial:
    lines.append(f"- [{partial[1]}] mutation{hints.get(partial[0], '')}")
if any(kind != "checked" for _, kind, _ in q.principles(contract)) or partial:
    lines.append("Skips are debt: when your change touches a skipped area, try to wire the check.")
open_items = q.open_items(root)
if open_items:
    lines.append("Open from the last quality gate: "
                 + ", ".join(f"{k} ({v})" for k, v in open_items.items()) + ". Address these first.")
if q.is_trusted(root):
    lines.append("Work test-first: write a failing test, run tests only through "
                 "`~/.claude/quality/qg-test [selectors]`, then implement. Source edits are blocked "
                 "until a failing qg-test run is recorded.")
else:
    lines.append("The contract is not trusted yet. Before running tests, ask the user to review "
                 ".quality/ and run `~/.claude/quality/qg-trust` in their own terminal.")
lines.append("Before you finish, verify each principle for your change; the Stop gate checks the same list.")
emit("\n".join(lines))
