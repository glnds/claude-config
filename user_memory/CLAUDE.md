# User Instructions

IMPORTANT: in all interactions and commit messages, be extremely concise and sacrifice grammar for
the sake of concision.

## Development Guidelines

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

### GitHub Issue Integration

Before starting work, check if a relevant GitHub issue exists. If working on a specific issue,
reference it in commit messages using the issue number (e.g., "Fixes #123" or "Addresses #123").

When encountering bugs or identifying potential improvements during development, create GitHub issues
to track them rather than immediately implementing fixes outside the current scope.

For significant changes, review related issues to understand context and avoid duplicate work. Update
issue status and add comments when making meaningful progress.

### Code Quality

Maintain consistency with existing code style and architecture patterns. Keep changes focused on the
task at hand. Write clear commit messages that explain why changes were made, not just what changed.

### Markdown Linting with markdownlint-cli2

When creating or editing Markdown files, always ensure compliance with the configured markdownlint rules
found at `~/.markdownlint.yaml` to avoid time-consuming lint-fix cycles.
Linting is performed using `markdownlint-cli2`.
An overview off all possible `markdownlint-cli2` rules can be found at: <https://github.com/markdownlint/markdownlint/blob/main/docs/RULES.md>.
The documentation about how to configure rules in `~/.markdownlint.yaml` can be found at: <https://github.com/DavidAnson/markdownlint/blob/main/schema/.markdownlint.yaml>.

#### Configuration

The global markdownlint configuration is located at `~/.markdownlint.yaml`. All Markdown files must conform
to the rules defined in this configuration.

#### Workflow

1. **Before writing**: Review the rules in `~/.markdownlint.yaml` to understand the requirements
2. **During writing**: Implement the rules directly while creating content to ensure compliance from
   the start
3. **After writing**: Verify compliance by running the linter:

```bash
   markdownlint-cli2 <filename.md> --config ~/.markdownlint.yaml
```

#### Tool Reference

For an overview of markdownlint-cli2 capabilities and options, use:

```bash
markdownlint-cli2 --help
```

#### Key Principle

**Write compliant Markdown from the start.** Implementing rules during creation is faster than fixing
violations afterward. Familiarize yourself with the common rules in `~/.markdownlint.yaml` to write
clean Markdown on the first attempt.
