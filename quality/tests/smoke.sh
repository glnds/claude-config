#!/usr/bin/env bash
# Smoke tests for the quality-gate hooks. Language agnostic: contract commands are plain sh.
# Runs against a throwaway copy of quality/ in a temp QG_HOME, so the real trust file is never touched.
set -u

REPO=$(cd "$(dirname "$0")/../.." && pwd -P)
TMP=$(cd "$(mktemp -d)" && pwd -P)
export QG_HOME="$TMP/qg-home"
export QG_TODAY=2026-06-01  # fixed "today" so skip expiry is deterministic
cp -R "$REPO/quality" "$QG_HOME" && rm -rf "$QG_HOME/tests" "$QG_HOME/trusted.json"
ERR="$TMP/stderr"
trap 'rm -rf "$TMP"' EXIT

pass=0 fail=0 out="" rc=0
ok() { pass=$((pass + 1)); echo "ok   $1"; }
bad() {
  fail=$((fail + 1)); echo "FAIL $1"; echo "     rc=$rc out=$out"
  sed 's/^/     err: /' "$ERR" 2>/dev/null | head -20
}
has() { case "$out" in *"$2"*) ok "$1" ;; *) bad "$1 (missing '$2')" ;; esac; }
lacks() { case "$out" in *"$2"*) bad "$1 (unexpected '$2')" ;; *) ok "$1" ;; esac; }
silent() { if [ -z "$out" ] && [ "$rc" = 0 ]; then ok "$1"; else bad "$1 (expected no output, exit 0)"; fi; }

hook() { # hook <script> <json> [VAR=value ...]
  local script=$1 json=$2; shift 2
  out=$(printf '%s' "$json" | env "$@" uv run --quiet --script "$QG_HOME/$script" 2>"$ERR"); rc=$?
}
qgtest() { out=$("$QG_HOME/qg-test" 2>"$ERR"); rc=$?; }
trust() {
  uv run --quiet --no-project --python '>=3.11' python -c "
import sys, json; sys.path.insert(0, '$QG_HOME'); import qglib as q
r = q.repo_root('.'); t = q.load_trust(); t[str(r)] = q.contract_hash(r)
q.TRUST_FILE.write_text(json.dumps(t))"
}
newrepo() { rm -rf "$1" && mkdir -p "$1" && cd "$1" && git init -q && git commit -q --allow-empty -m init; }

# --- Repository A: contract with sh commands (spec harness) ----------------------------------
A="$TMP/qg-smoke"
newrepo "$A"
mkdir -p .quality/out src tests && echo '.quality/out/' > .gitignore
write_contract() { # write_contract <test cmd> <mutation line> [extra [mutation] lines]
  cat > .quality/contract.toml <<EOF
version = 1
base = "HEAD"
[paths]
source = ["src/**"]
tests  = ["tests/**"]
docs   = ["README*", "docs/**"]
[commands]
test          = "$1"
diff_coverage = "sh .quality/flag.sh cov"
$2
[mutation]
report = ".quality/out/mutation.json"
threshold = 0.8
budget_seconds = 5
${3:-}
EOF
}
write_contract 'sh .quality/flag.sh test {args}' 'mutation      = "sh .quality/mut.sh"'
# A step fails when .quality/out/fail-<step> exists.
echo '[ ! -f ".quality/out/fail-$1" ]' > .quality/flag.sh
printf '%s\n' '[ -f .quality/out/slow ] && sleep 37' \
  'cp .quality/out/mut-fixture.json .quality/out/mutation.json' > .quality/mut.sh
echo '{"killed": 9, "survived": 1}' > .quality/out/mut-fixture.json

STOP="{\"cwd\":\"$A\",\"session_id\":\"t\",\"stop_hook_active\":false}"
STOP_ACTIVE="{\"cwd\":\"$A\",\"session_id\":\"t\",\"stop_hook_active\":true}"
edit() { echo "{\"cwd\":\"$A\",\"session_id\":\"t\",\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$1\"}}"; }
START="{\"cwd\":\"$A\",\"session_id\":\"t\",\"source\":\"startup\"}"

git add -A && git commit -qm c
hook stop_gate.py "$STOP"; silent "1 clean tree: no output"

echo x > src/a.py
hook stop_gate.py "$STOP"; has "2 untrusted: block" '"decision": "block"'; has "2 untrusted: reason" "not trusted"

trust; touch .quality/out/fail-test; rm -f .git/qg/stop-digest
hook stop_gate.py "$STOP"; has "3 tests fail: first" "Tests fail"
hook stop_gate.py "$STOP"; has "3 tests fail: second" "Tests fail"

rm .quality/out/fail-test; touch .quality/out/fail-cov
hook stop_gate.py "$STOP"; has "4 coverage finding" "not covered"; has "4 docs finding" "no documentation"
hook stop_gate.py "$STOP"; silent "4 same change set: no output"

hook stop_gate.py "$STOP_ACTIVE"; silent "5 stop_hook_active: no output"

rm .quality/out/fail-cov; echo d > README.md; echo '{"killed": 5, "survived": 5}' > .quality/out/mut-fixture.json
hook stop_gate.py "$STOP"; has "6 mutation below threshold" "Mutation score 50% is below 80%"

echo '{"killed": 9, "survived": 1}' > .quality/out/mut-fixture.json; touch src/b.py
hook stop_gate.py "$STOP"; silent "7 all green: no output"

touch .quality/out/slow src/c.py
t0=$SECONDS
hook stop_gate.py "$STOP"; has "8 mutation deferred" "deferred to CI"
[ $((SECONDS - t0)) -lt 20 ] && ok "8 within time budget" || bad "8 took $((SECONDS - t0))s"
pgrep -f "sleep 37" >/dev/null && bad "8 sleep left running" || ok "8 no sleep left running"

rm -f .quality/out/slow .git/qg/tdd.json
hook tdd_gate.py "$(edit "$A/src/a.py")"; has "9 no run recorded: deny" '"permissionDecision": "deny"'

touch .quality/out/fail-test; qgtest
[ "$rc" != 0 ] && ok "10 qg-test exits non-zero" || bad "10 qg-test should fail"
hook tdd_gate.py "$(edit "$A/src/a.py")"; silent "10 red: allow"

rm .quality/out/fail-test; qgtest
hook tdd_gate.py "$(edit "$A/src/a.py")"; has "11 green: ask" '"permissionDecision": "ask"'
hook tdd_gate.py "$(edit "$A/src/a.py")" QG_TDD=strict; has "11 green strict: deny" '"permissionDecision": "deny"'

hook tdd_gate.py "$(edit "$A/tests/t.py")"; silent "12 test file: allow"
hook tdd_gate.py "$(edit "$A/.quality/contract.toml")"; has "13 contract: ask" '"permissionDecision": "ask"'
hook tdd_gate.py "$(edit "$QG_HOME/stop_gate.py")"; has "14 gate script: deny" '"permissionDecision": "deny"'

hook tdd_gate.py "$(edit "$A/src/a.py")" QG_TDD=off; silent "15 QG_TDD=off: allow"
grep -q "src/a.py" .git/qg/bypass.log && ok "15 bypass logged" || bad "15 bypass not logged"

qgtest
hook session_start.py "$START"; has "16 context mentions qg-test" "qg-test"
[ ! -f .git/qg/tdd.json ] && ok "16 tdd.json reset" || bad "16 tdd.json still present"

echo '# changed' >> .quality/flag.sh; qgtest
[ "$rc" = 3 ] && ok "17 changed .quality/: qg-test exit 3" || bad "17 expected exit 3"

out=$(echo yes | "$QG_HOME/qg-trust" 2>&1); rc=$?
[ "$rc" != 0 ] && ok "18 qg-trust refuses without TTY" || bad "18 qg-trust ran without TTY"

# --- Principle coverage, missing tools, start/end checklist ----------------------------------
write_contract 'sh .quality/flag.sh test {args}' ''; trust; touch src/d.py
hook stop_gate.py "$STOP"; has "21 unwired mutation: block" '"decision": "block"'; has "21 names principle" "mutation"
has "21 says no check" "no check"
hook session_start.py "$START"; has "25 start lists unwired" "[unwired] mutation"

write_contract 'sh .quality/flag.sh test {args}' 'mutation = { skip = "no mature tool yet", until = 2026-07-01 }'; trust; touch src/e.py
hook stop_gate.py "$STOP"; silent "22 skipped mutation: no finding"
hook session_start.py "$START"; has "25 start lists skipped" "[skipped until 2026-07-01: no mature tool yet] mutation"
lacks "27 nothing open after a pass" "Open from the last quality gate"
has "25 start lists checked" "[checked] test"
has "25 start states end rule" "Before you finish"

write_contract 'nonexistent-tool-xyz {args}' 'mutation = { skip = "no mature tool yet", until = 2026-07-01 }'; trust; touch src/f.py
hook stop_gate.py "$STOP"; has "23 missing tool: block" '"decision": "block"'; has "23 says missing" "missing"
lacks "23 not reported as failing tests" "Tests fail"
hook session_start.py "$START"; has "26 start shows open item" "Open from the last quality gate"
has "26 open item names test" "test"

# Wrappers such as `uv run` exit 2, not 127, when the tool is absent.
write_contract 'uv run --no-project nonexistent-tool-xyz {args}' 'mutation = { skip = "no mature tool yet", until = 2026-07-01 }'; trust; touch src/h.py
hook stop_gate.py "$STOP"; has "23b wrapped missing tool: says missing" "tooling for \`test\` is missing"
lacks "23b not reported as failing tests" "Tests fail"
qgtest; [ "$rc" != 0 ] && [ ! -f .git/qg/tdd.json ] && ok "23b qg-test records no red" || bad "23b qg-test recorded red"

git add -A && git commit -qm docs && touch src/g.py  # only a code change pending
out=$(cd "$A" && printf '{"stop_hook_active":false}' | bash "$REPO/hooks/docs-stop.sh" 2>"$ERR"); rc=$?
silent "24 docs-stop.sh silent in contract repo"

# --- Skips expire; partial skips by path --------------------------------------------------------
write_contract 'sh .quality/flag.sh test {args}' 'mutation = { skip = "too slow" }'; trust; touch src/i.py
hook stop_gate.py "$STOP"; has "31 undated skip: block" '"decision": "block"'; has "31 asks for until" "no valid \`until\`"
hook session_start.py "$START"; has "31 start flags undated skip" "[undated skip: too slow] mutation"

write_contract 'sh .quality/flag.sh test {args}' 'mutation = { skip = "too slow", until = 2026-05-01 }'; trust; touch src/j.py
hook stop_gate.py "$STOP"; has "32 expired skip: block" "expired on 2026-05-01"
has "32 slowness is no reason" "not a reason"

write_contract 'sh .quality/flag.sh test {args}' 'mutation = { skip = "later", until = 2026-12-31 }'; trust; touch src/k.py
hook stop_gate.py "$STOP"; has "33 skip too far out: block" "more than 90 days"

PARTIAL='skip_paths = { paths = ["src/backend/**"], reason = "needs testcontainers", until = 2026-07-01 }'
echo '{"killed": 5, "survived": 5}' > .quality/out/mut-fixture.json
write_contract 'sh .quality/flag.sh test {args}' 'mutation      = "sh .quality/mut.sh"' "$PARTIAL"; trust
git add -A && git commit -qm partial && hook session_start.py "$START"  # re-anchor: change set = what follows
mkdir -p src/backend src/front && touch src/backend/x.py && echo more >> README.md
hook stop_gate.py "$STOP"; silent "34 change only in skipped path: mutation not run"
hook session_start.py "$START"; has "34 start lists partial skip" "[partial skip until 2026-07-01: src/backend/** (needs testcontainers)] mutation"
touch src/front/y.py
hook stop_gate.py "$STOP"; has "35 change outside skipped path: mutation runs" "Mutation score 50% is below 80%"

write_contract 'sh .quality/flag.sh test {args}' 'mutation      = "sh .quality/mut.sh"' \
  'skip_paths = { paths = ["src/backend/**"], reason = "needs testcontainers", until = 2026-05-01 }'; trust
touch src/backend/z.py
hook stop_gate.py "$STOP"; has "36 expired partial skip: block" "expired on 2026-05-01"
echo '{"killed": 9, "survived": 1}' > .quality/out/mut-fixture.json

# --- Repository B: no contract (onboarding) ---------------------------------------------------
B="$TMP/qg-nocontract"
newrepo "$B"
STOPB="{\"cwd\":\"$B\",\"session_id\":\"t\",\"stop_hook_active\":false}"
echo notes > NOTES.md
hook stop_gate.py "$STOPB"; silent "20 docs-only, no contract: silent"
echo 'package main' > main.go
hook stop_gate.py "$STOPB"; has "19 first code change: onboarding block" '"decision": "block"'
has "19 points to templates" "templates"
echo 'package other' > other.go
hook stop_gate.py "$STOPB"; has "19 later change: warning only" "systemMessage"; lacks "19 later change: no block" '"decision"'
hook session_start.py "{\"cwd\":\"$B\",\"session_id\":\"t\",\"source\":\"startup\"}"
has "25 no contract: principles line" "no .quality/contract.toml"

# Work committed (and pushed) during the session still counts: the session start anchors the change set.
git add -A && git commit -qm wip
hook session_start.py "{\"cwd\":\"$B\",\"session_id\":\"s2\",\"source\":\"startup\"}"
echo 'package more' > more.go && git add -A && git commit -qm more
hook stop_gate.py "{\"cwd\":\"$B\",\"session_id\":\"s2\",\"stop_hook_active\":false}"
has "28 committed change, clean tree: onboarding block" '"decision": "block"'
hook stop_gate.py "{\"cwd\":\"$B\",\"session_id\":\"s2\",\"stop_hook_active\":false}"
silent "28 same change set: no output"

# The onboarding reminder blocks once per session, not once per repository.
hook session_start.py "{\"cwd\":\"$B\",\"session_id\":\"s3\",\"source\":\"startup\"}"
echo 'package again' > again.go
hook stop_gate.py "{\"cwd\":\"$B\",\"session_id\":\"s3\",\"stop_hook_active\":false}"
has "29 new session: onboarding block again" '"decision": "block"'

# --- Repository C: clone whose default branch is master, no `base` in the contract ------------
R="$TMP/qg-remote.git" C="$TMP/qg-clone"
git init -q --bare -b master "$R" && newrepo "$TMP/qg-seed" && git push -q "$R" HEAD:master
git clone -q "$R" "$C" 2>/dev/null && cd "$C"
echo 'package c' > c.go && git add -A && git commit -qm c
hook stop_gate.py "{\"cwd\":\"$C\",\"session_id\":\"c\",\"stop_hook_active\":false}"
has "30 base defaults to origin/master: committed change seen" '"decision": "block"'

echo; echo "passed $pass, failed $fail"
[ "$fail" = 0 ]
