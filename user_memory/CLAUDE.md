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

**Infrastructure changes MUST use:**

- **IaC:** Terraform, AWS CDK, CloudFormation, or SAM
- **CI/CD:** GitHub Actions, CodePipeline/CodeBuild

### Markdown

**Line length limit is 100 characters.** Wrap all Markdown at 100 cols — not 80.

Use `markdownlint-cli2` with config at `~/.markdownlint.yaml`. Write compliant Markdown from
the start — review rules before writing, apply during writing, verify after:

```bash
markdownlint-cli2 <filename.md> --config ~/.markdownlint.yaml
```

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
