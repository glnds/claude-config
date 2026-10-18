# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Stop: verify every principle for the change set. Blocks at most once per change set."""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qglib as q  # noqa: E402


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason[:9000]}))
    sys.exit(0)


def notify(msg):
    print(json.dumps({"systemMessage": msg[:2000]}))
    sys.exit(0)


data = q.read_hook_input()
if data.get("stop_hook_active"):
    sys.exit(0)
root = q.repo_root(data.get("cwd", "."))
if root is None:
    sys.exit(0)

contract = q.load_contract(root)
base = q.merge_base(root, contract)
changed, untracked = q.changed_files(root, base)
if not changed:
    sys.exit(0)
digest = q.change_digest(root, base, untracked)
marker = q.state_dir(root) / "stop-digest"
if marker.exists() and marker.read_text() == digest:
    sys.exit(0)


def remember():
    marker.write_text(digest)


if contract is None:
    mode = os.environ.get("QG_MISSING_CONTRACT", "onboard")
    remember()
    if mode == "off" or all(q.matches(f, q.DEFAULT_DOCS) for f in changed):
        sys.exit(0)
    onboarded = q.state_dir(root) / "onboarded"
    if mode == "block" or (mode == "onboard" and not onboarded.exists()):
        onboarded.touch()
        block("This repository has no .quality/contract.toml, so this change is not checked against "
              "the quality principles (TDD, tests for changed lines, mutation testing, docs). Propose a "
              f".quality/ contract for this stack to the user (see {q.TEMPLATES}), or tell them briefly "
              "why this repository does not need one. This reminder is shown once per repository.")
    if mode in ("onboard", "warn"):
        notify("Quality gate skipped: no .quality/contract.toml in this repository.")
    sys.exit(0)
if not q.is_trusted(root):
    remember()
    block("The quality contract in .quality/ is not trusted, so its commands were not run. "
          "Ask the user to review .quality/ and run ~/.claude/quality/qg-trust in their own terminal.")
if not any(q.is_source(f, contract) for f in changed):
    remember()
    sys.exit(0)

status = dict(q.principles(contract))
results, findings = {}, {}  # principle -> pass|fail|missing-tool|deferred|unwired|skipped|not-run


def unwired(name):
    return (f"Principle `{name}` ({q.PRINCIPLES[name]}) has no check here. Choose a tool for this "
            f"stack (see {q.TEMPLATES}), install it with the project's tool manager and add it to "
            f"[commands] in .quality/contract.toml, or record `{name} = {{ skip = \"<reason>\" }}`.")


def missing_tool(name, out):
    return (f"The tooling for `{name}` is missing. Install it with the project's tool manager "
            f"(mise, uv, npm, cargo, ...) and retry:\n{out}")


def run(name, timeout):
    try:
        rc, out = q.run_command(root, q.render(q.command(contract, name), base=base), timeout=timeout)
    except subprocess.TimeoutExpired:
        return "fail", f"`{name}` timed out after {timeout}s."
    if rc in q.MISSING_TOOL:
        return "missing-tool", q.tail(out)
    return ("pass" if rc == 0 else "fail"), q.tail(out)


def checklist():
    lines = ["Quality gate for this change set. Fix each open item, or explain in one or two "
             "sentences why it does not apply:"]
    for name in q.PRINCIPLES:
        r = results.get(name, "not-run")
        if r == "pass":
            lines.append(f"[x] {name}")
        elif r == "skipped":
            lines.append(f"[-] {name} ({status[name]})")
        elif name in findings:
            lines.append(f"[ ] {name}\n    " + findings[name].replace("\n", "\n    "))
        else:
            lines.append(f"[ ] {name} (not run: fix the items above first)")
    return "\n".join(lines)


def finish():
    q.write_last_gate(root, digest, results)
    if "missing-tool" not in results.values():  # missing tooling is re-checked next turn
        remember()


for name in q.CONTRACT_PRINCIPLES:
    if status[name] == "unwired":
        results[name], findings[name] = "unwired", unwired(name)
    elif status[name] != "checked":
        results[name] = "skipped"

if status["test"] == "checked":
    results["test"], out = run("test", 240)
    if results["test"] != "pass":  # digest not recorded: failing tests are re-checked next turn
        q.write_last_gate(root, digest, results)
        if results["test"] == "missing-tool":
            block(missing_tool("test", out))
        block("Tests fail. Fix the implementation, not the tests, unless a test is wrong:\n\n" + out)

if status["diff_coverage"] == "checked":
    results["diff_coverage"], out = run("diff_coverage", 300)
    if results["diff_coverage"] == "fail":
        findings["diff_coverage"] = "Changed lines are not covered well enough. Add tests for them:\n" + out
    elif results["diff_coverage"] == "missing-tool":
        findings["diff_coverage"] = missing_tool("diff_coverage", out)

results["docs"] = "pass"
if not any(q.matches(f, contract.get("paths", {}).get("docs")) for f in changed):
    results["docs"] = "fail"
    findings["docs"] = ("Source changed but no documentation did. Run the doc-auditor subagent on this diff, "
                        "then update README, docs, CHANGELOG or ADRs, or state briefly why no update is needed.")
if q.command(contract, "docs_lint"):
    r, out = run("docs_lint", 60)
    if r != "pass":
        results["docs"] = r
        findings["docs"] = "\n\n".join(filter(None, [
            findings.get("docs"),
            missing_tool("docs_lint", out) if r == "missing-tool" else "Documentation checks failed:\n" + out]))

if status["mutation"] == "checked" and not findings:
    m = contract.get("mutation", {})
    report = root / m.get("report", ".quality/out/mutation.json")
    report.unlink(missing_ok=True)
    try:
        rc, out = q.run_command(root, q.render(q.command(contract, "mutation"), base=base),
                                timeout=int(m.get("budget_seconds", 240)))
        if rc in q.MISSING_TOOL:
            results["mutation"], findings["mutation"] = "missing-tool", missing_tool("mutation", q.tail(out))
        else:
            stats = json.loads(report.read_text())
            killed, survived = int(stats["killed"]), int(stats["survived"])
            total, threshold = killed + survived, float(m.get("threshold", 0.8))
            results["mutation"] = "pass"
            if total and killed / total < threshold:
                survivors = "\n".join(stats.get("survivors", [])[:30])
                results["mutation"] = "fail"
                findings["mutation"] = (f"Mutation score {killed / total:.0%} is below {threshold:.0%} "
                                        f"({survived} of {total} mutants survived). Strengthen the assertions "
                                        f"so the tests fail for these mutants:\n{survivors}")
    except subprocess.TimeoutExpired:
        results["mutation"] = "deferred"
        finish()
        notify("Mutation testing exceeded its time budget and was deferred to CI.")
    except (OSError, ValueError, KeyError) as e:
        results["mutation"] = "fail"
        findings["mutation"] = f"Mutation report missing or invalid ({e}). Check the contract's `mutation` command."

finish()
if findings:
    block(checklist())
