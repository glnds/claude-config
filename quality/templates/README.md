# Quality contract: onboarding guide

The user-level hooks enforce four principles in every Git repository. The hooks hold no tooling:
each repository declares in `.quality/contract.toml` how it checks each principle for its stack.

| Principle       | Contract key    | The check must                                                   |
|-----------------|-----------------|------------------------------------------------------------------|
| TDD             | `test`          | Run the suite, or the selected tests when `{args}` is not empty  |
| Tests written   | `diff_coverage` | Fail when lines changed since `{base}` are under the threshold   |
| Tests meaningful| `mutation`      | Mutation-test code changed since `{base}`, write the JSON report |
| Docs up to date | `docs_lint`     | Optional static doc checks; the path trigger always runs         |

Each of `test`, `diff_coverage` and `mutation` is either a shell command or a dated opt-out. A
principle that is neither is reported as unwired by the Stop gate.

```toml
[commands]
mutation = { skip = "no mature mutation tool for this stack yet", until = 2026-12-31 }

[mutation]   # partial: changes only under these paths do not trigger mutation testing
skip_paths = { paths = ["backend/**"], reason = "suite needs testcontainers", until = 2026-12-31 }
```

Skips are debt, not settings:

- `until` is required and at most 90 days out. An undated, too distant or expired skip counts as
  unwired, so the gate asks again: wire the check, or renew the skip if the reason still holds.
- Skip the smallest area that needs it. When one part of the repo is hard (a backend that needs
  containers), wire the rest (the frontend) and use `skip_paths` for that part.
- Slowness is never a reason. A run over `budget_seconds` is deferred to CI without blocking, so
  wire slow checks anyway, scoped to the changed code where the tool allows it.

## Onboarding a repository

1. Detect the stack and its tool manager (mise, uv, npm/pnpm, cargo, Go modules, Maven/Gradle).
2. Copy a template from this directory to `.quality/`, or write one for the stack using the
   table below. Keep helper scripts in `.quality/`, because trust covers the whole directory.
3. Install the tools through the project's tool manager, never ad hoc, so CI gets the same tools.
   Add it as a dev-only dependency. If the user's instructions require approval for new
   dependencies and do not pre-approve quality tooling, propose it, and until they approve, record
   `{ skip = "awaiting approval of <tool>", until = <date> }` instead of leaving it unwired.
4. Add `.quality/out/` to `.gitignore`.
5. Ask the user to review `.quality/` and run `~/.claude/quality/qg-trust` in their own terminal.
6. Run `~/.claude/quality/qg-test` once to confirm the `test` command works.

When a command exits 126 or 127, or a wrapper such as `uv run` or `npx` reports that the tool is
not found, the gate reports missing tooling instead of a failure: install it and retry. Any change
to `.quality/` needs a new `qg-trust` approval.

## Contract reference

```toml
version = 1
base = "origin/main"            # optional; default: origin/HEAD, origin/main, origin/master

[paths]                          # fnmatch globs on repo-relative paths; `*` also matches `/`
source = ["src/**"]
tests  = ["tests/**", "**/test_*.*", "**/*_test.*"]
docs   = ["README*", "CHANGELOG*", "docs/**", "adr/**"]

[commands]                       # run with the repo root as working directory
test          = "./.quality/test.sh {args}"     # never wrap {args} in quotes
diff_coverage = "./.quality/diff_coverage.sh {base}"
docs_lint     = "..."                           # optional
mutation      = "..."                           # or { skip = "reason", until = <date> }

[mutation]
report         = ".quality/out/mutation.json"
threshold      = 0.8   # minimum killed / (killed + survived)
budget_seconds = 240   # in-session time box; CI runs without it
skip_paths     = { paths = ["..."], reason = "...", until = <date> }  # optional, partial skip
```

`{base}` is the merge-base SHA of `HEAD` and `base`, or the session's start `HEAD` when that is
older, so work committed or pushed during the session stays in the change set. `{args}` holds
the shell-quoted `qg-test` arguments. A file that matches both `source` and `tests` counts as a test.

The `mutation` command writes this report. Timeouts count as killed:

```json
{"killed": 42, "survived": 7, "tool": "mutmut 3.8.0", "survivors": ["pkg.mod.fn__mutmut_3"]}
```

## Starting points per ecosystem

`python/` is the tested reference adapter (uv, pytest, coverage.py, diff-cover, ruff, pydoclint,
mutmut 3). The others are starting points to verify. diff-cover reads Cobertura, JaCoCo, Clover and
LCOV, so it can be the diff-coverage engine for most stacks.

| Ecosystem      | `test`                       | `diff_coverage`                            | `mutation`                       |
|----------------|------------------------------|--------------------------------------------|----------------------------------|
| JS, TypeScript | Vitest or Jest               | LCOV or Cobertura + diff-cover             | StrykerJS, incremental mode      |
| Java, Kotlin   | JUnit via Maven or Gradle    | JaCoCo XML + diff-cover                    | PIT, Maven SCM goal              |
| Go             | `go test`                    | cover profile to Cobertura + diff-cover    | Gremlins or go-mutesting         |
| Rust           | `cargo test` or nextest      | cargo-llvm-cov Cobertura/LCOV + diff-cover | cargo-mutants with its diff mode |

Where diff-scoped mutation testing is weak, wire it for the parts where it works and use
`skip_paths` for the rest, or record a dated `mutation = { skip = "...", until = <date> }` and run
it in CI as report-only.
