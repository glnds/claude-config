#!/usr/bin/env python3
"""Mutation-test Python modules changed since argv[1] with mutmut 3; write the normalised report."""
import json
import subprocess
import sys
from pathlib import Path

base = sys.argv[1]
out = Path(".quality/out")
out.mkdir(parents=True, exist_ok=True)
report = out / "mutation.json"


def lines(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()


files = sorted(set(lines("git", "diff", "--name-only", base, "--", "src/*.py")
                   + lines("git", "ls-files", "--others", "--exclude-standard", "--", "src/*.py")))
mods = [f.removeprefix("src/").removesuffix(".py").replace("/", ".").removesuffix(".__init__") + ".*"
        for f in files if Path(f).exists()]
if not mods:
    report.write_text(json.dumps({"killed": 0, "survived": 0, "tool": "mutmut"}))
    sys.exit(0)

subprocess.run(["uv", "run", "mutmut", "run", *mods])
subprocess.run(["uv", "run", "mutmut", "export-cicd-stats"], check=True)
stats = json.loads(Path("mutants/mutmut-cicd-stats.json").read_text())
survivors = [l.split(":")[0].strip() for l in lines("uv", "run", "mutmut", "results") if "survived" in l]
report.write_text(json.dumps({
    "killed": stats.get("killed", 0) + stats.get("timeout", 0),
    "survived": stats.get("survived", 0),
    "tool": "mutmut 3",
    "survivors": [s for s in survivors if any(s.startswith(m[:-1]) for m in mods)],
}))
