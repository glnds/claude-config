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

### Clarification Before Implementation

**NEVER start implementing when unclear requirements or ambiguities exist.** Ask questions until every
detail is crystal clear. Do not make assumptions. Do not fill in gaps. Do not interpret vague requirements.
If multiple approaches are possible, explicitly confirm the intended direction before writing code.
Ambiguity means stop and ask, not guess and proceed.

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

### AWS API MCP Usage Policy

**ONLY Allowed (read-only):**

- `describe-*`, `list-*`, `get-*` commands
- Status checks, log queries, metric reads

**Forbidden:**

- Any mutating operation (`create-*`, `update-*`, `delete-*`, `put-*`, `modify-*`, `start-*`,
  `stop-*`, `invoke-*`, etc.)

**Infrastructure changes MUST use:**

- **IaC:** Terraform, AWS CDK, CloudFormation, or SAM
- **CI/CD:** GitHub Actions, CodePipeline/CodeBuild

### Markdown Linting

Use `markdownlint-cli2` with config at `~/.markdownlint.yaml`. Write compliant Markdown from
the start — review rules before writing, apply during writing, verify after:

```bash
markdownlint-cli2 <filename.md> --config ~/.markdownlint.yaml
```
