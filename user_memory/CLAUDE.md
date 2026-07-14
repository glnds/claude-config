# User Instructions

IMPORTANT: in all interactions and commit messages, be extremely concise and sacrifice grammar for
the sake of concision.

## Development Guidelines

### Python Tooling Preferences

Always use Astral tooling for Python projects:

- **uv** for package management, virtual environments, and running scripts
  (`uv add`, `uv run`, `uv sync`) — never use `pip` or `poetry` directly
- **ruff** for linting and formatting — never use `flake8`, `pylint`, `black`, or `isort`
- **ty** for type checking — prefer over `mypy` or `pyright`

### Test-Driven Development

Write tests before implementing functionality. Follow this cycle:

1. Write a failing test that defines the desired behavior
2. Implement the minimum code needed to make the test pass
3. Refactor while keeping tests green

When creating new features or fixing bugs, start by adding or modifying tests. Ensure all tests pass
before considering work complete. Place tests in appropriate directories following the project's
existing test structure.

### Code Quality

Maintain consistency with existing code style and architecture patterns. Keep changes focused on the
task at hand. Write clear commit messages that explain why changes were made, not just what changed.

### Infrastructure as Code

**IaC is the single source of truth for all infrastructure.** Never click in
consoles, never mutate via CLI/SDK. If it isn't in code, it doesn't exist.

**Allowed tools:** Terraform, AWS CDK, CloudFormation, SAM.

**Deployment is pipeline-only.** Never `terraform apply`, `sam deploy`,
`cdk deploy`, or equivalent from a workstation. All changes ship through
CI/CD (GitHub Actions, CodePipeline/CodeBuild).

**Drift = bug.** If reality and IaC disagree, fix IaC and re-deploy via the
pipeline. Do not reconcile by hand.

### AWS CLI Usage Policy

Use the AWS CLI. Do not use the AWS API MCP server.

All `aws` calls run under an SSO profile with the `ReadOnlyAccess` permission
set. Set `AWS_PROFILE` or pass `--profile`. Verify once per session:

```bash
aws sts get-caller-identity
```

ARN must contain `assumed-role/AWSReservedSSO_ReadOnlyAccess`. If not, stop.

**Forbidden:**

- Any mutating verb (`create-*`, `update-*`, `delete-*`, `put-*`, `modify-*`,
  `start-*`, `stop-*`, `terminate-*`, `run-*`, `invoke-*`, etc.)
- `aws sso login`: user handles authentication.

### Markdown

**Line length limit is 100 characters.** Wrap all Markdown at 100 cols — not 80.

Use `rumdl` with config at `~/.config/rumdl/rumdl.toml` (auto-discovered).
Write compliant Markdown from the start — review rules before writing, apply during writing,
verify after:

```bash
rumdl check <filename.md>   # lint
rumdl fmt <filename.md>     # autoformat violations
```

## CI/CD & Tooling Standard

Every project mirrors this setup. **mise** pins and installs every tool identically in dev and
CI; **hk** git hooks give fast local parity; **GitHub Actions is the authoritative gate**;
**Renovate** keeps action digests and lockfiles current. Apply the Core tier everywhere; add the
Python / Frontend / AWS layers only where relevant.

Canonical tool list:

- **mise** — tool-version pinning + task runner
- **hk** (pkl config) — git hooks
- **ruff** + **ty** — Python lint/format + type check; **uv** for packaging
- **oxlint** + **vitest** + **tsc** — frontend lint / test / typecheck
- **rumdl** — markdown lint; **typos** — spell check
- **trufflehog** — secret scanning (local hooks)
- **semgrep** + **bandit** — SAST; **trivy** — deps/containers; **checkov** — IaC; **zizmor** —
  workflow audit
- **cfn-lint** + **cfn-guard** — CloudFormation lint/policy
- **Renovate** — dependency + action-digest automation

### Core (every project)

1. **Tool versions — mise.** `mise.toml` `[tools]` pins every runtime and CLI (never install
   tools ad-hoc). `[settings] lockfile = true` with a committed, multi-platform, checksummed
   `mise.lock`. `[env]` holds only CI-safe vars (never `AWS_PROFILE` — it breaks OIDC in CI).
   `[tasks]` is the sole task runner — no Makefile or justfile. Ship a `setup` task =
   `mise install` + `hk install`. CI installs tools via `jdx/mise-action`, so dev and CI run
   identical binaries.
2. **Git hooks — hk.** `hk.pkl` (version-pinned). pre-commit = fast, per-file, auto-fixing:
   whitespace/EOF, ruff + ruff-format, typos, rumdl, secret scan. pre-push = whole-program +
   affected-only: typecheck, tests, secret scan on the git diff. Glob-scope steps per area so a
   frontend-only change skips backend work. Hooks are the fast pre-filter; CI is the real gate.
3. **Secret scanning — trufflehog.** Local-only in hk (filesystem on commit, git-diff vs the
   default branch on push). Not duplicated in CI.
4. **GitHub Actions hardening.** SHA-pin every action with a `# vX` comment. Least-privilege
   `permissions:` at the workflow root (`contents: read`), widened per-job only as needed.
   `persist-credentials: false` on every checkout. Concurrency groups cancel superseded PR runs.
   A `ci.yml` gate runs lint + typecheck + tests + a coverage floor on every PR and push.
5. **SAST — semgrep.** Run via `uvx` (the CE CLI, not a third-party action), emit SARIF, gate on
   findings.
6. **Dependency automation — Renovate.** Extend `config:recommended`,
   `helpers:pinGitHubActionDigests`, and `:maintainLockFilesWeekly`. Automerge minor/patch/digest
   plus lockfile maintenance. Group updates per package directory. Schedule weekly off-hours.
7. **Config files.** `rumdl.toml` (markdown — see the Markdown note above for the line-length
   rule) and `typos.toml` (spell-check allowlist). Wrap markdown at 100 (code/tables exempt).

### Layer: Python

uv + ruff + ty (per Python Tooling Preferences above). ruff and ty config live in
`pyproject.toml`. pytest with a coverage floor (`--cov-fail-under`). Run ruff (check + format
`--check`) and ty in both hk and CI. bandit for Python SAST, with severity/confidence thresholds
passed as CLI flags.

### Layer: Frontend

oxlint (not ESLint) + vitest + `tsc -b`. Wire into hk (per-file lint on commit, typecheck and
tests on push) and the CI gate.

### Layer: AWS / IaC

cfn-lint + cfn-guard (a policy-rules file) in hk pre-push and CI. A security-scans workflow runs
checkov (IaC), trivy fs (deps/containers), and zizmor (audits the workflows themselves) — all
emit SARIF, gated on aggregated findings, with a weekly CVE cron and PR summary comments. AWS
auth via OIDC role assumption, never static keys. Deploy is pipeline-only (CI → S3 artifact →
CodePipeline), consistent with the Infrastructure as Code section above.

## Autonomy

Proceed without asking. Ask only before:

- Irreversible destructive actions (force push, `rm -rf`, `DROP TABLE`, deleting remote branches)
- Touching production infrastructure or external credentials
- Externally visible actions (publishing, sending email, posting to Slack, creating PRs to
  protected branches)
- Incurring costs beyond the current subscription

Apply these decision defaults:

<!-- markdownlint-disable MD013 -->

| Situation                 | Action                                                                      |
|---------------------------|-----------------------------------------------------------------------------|
| Multiple valid approaches | Match existing patterns, else pick the simplest                             |
| Ambiguous requirement     | Literal, narrowest interpretation                                           |
| Missing information       | Codebase conventions first, industry defaults second                        |
| New file placement        | Follow existing directory structure; no new top-level directories           |
| Naming and style          | Match codebase conventions                                                  |
| Error handling            | Fail fast with descriptive messages; never swallow exceptions               |
| Dependencies              | Use what is in the project; no new dependencies without explicit approval   |
| Scope                     | Smallest correct change; no adjacent fixes, no opportunistic refactors      |
| Blocked after 3 attempts  | Write to `tasks/blocked.md`, continue with next task                        |
| Stuck in a loop           | Step back, search for established patterns, adapt                           |
| Git                       | Conventional commits, commit frequently, never `--no-verify`                |

<!-- markdownlint-enable MD013 -->

Document every assumption inline and in the final report's `## Assumptions` section. No
clarifying questions during implementation.

## Plan review routing

When `writing-plans` completes and produces a plan file in `docs/plans/`,
dispatch `adversarial-plan-review` as a subagent with only the plan path
and spec path as input, before invoking `subagent-driven-development`.

- On verdict PASS: proceed to implementation.
- On verdict NEEDS REWORK: re-invoke `writing-plans` with the findings file
  at `docs/plans/<plan>.review.md` as additional input. Do not invoke the
  review skill a second time in the same session; if the reworked plan
  still fails on next review, promote to NEEDS HUMAN.
- On verdict NEEDS HUMAN: halt and surface the review file to the user.

Skip the review entirely on plans with fewer than three tasks, or tasks
that modify a single file. The inline self-review in writing-plans already
covers those cases.
