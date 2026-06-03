# Claude Config

Personal Claude Code configuration: user instructions and custom skills.

## Repository Contents

### Plugins

Plugins extend Claude Code with commands, agents, skills, and hooks.

**Recommended for frontend projects:**

```bash
/plugin marketplace add anthropics/claude-code
/plugin install frontend-design@claude-code
```

The frontend-design plugin auto-invokes for UI work, generating production-grade interfaces
with bold design choices instead of generic AI aesthetics.

### GitHub Integration

Claude Code integrates with GitHub Actions for automated PR reviews and issue analysis.

**Setup:**

```bash
/install-github-app
```

Installs the Claude GitHub app, configures repository secrets (`ANTHROPIC_API_KEY`), and sets
up GitHub Actions workflows.

**Review flow:**

Mention `@claude` in PRs or issues with requests like "review my code changes" or "check for
security issues". Claude respects your repository's `CLAUDE.md` guidelines and existing code
patterns for tailored reviews.

### User Memory

The `user_memory/CLAUDE.md` file contains user-level instructions that apply across all projects.
Copy to `~/.claude/CLAUDE.md` for global application.

**Key directives:**

- Conciseness over grammar in all interactions
- Clarify before implementing (never assume)
- Test-driven development (red-green-refactor)
- GitHub issue integration
- Markdown linting with rumdl

### Skills

Skills extend Claude Code with structured workflows. Each skill contains frontmatter metadata
and step-by-step instructions.

#### make-note (v1.2)

Creates Obsidian notes with intelligent tag suggestions from existing vault patterns.

**Trigger:** "create a note", "make a note", "save to Obsidian"

#### verbalized-sampling (v1.0)

Prompt engineering technique to overcome LLM mode collapse by generating multiple responses
with probability distributions.

**Trigger:** "use verbalized sampling", "show multiple responses with probabilities"

## AWS CLI over AWS MCP

Rationale for using the AWS CLI directly from Claude Code instead of the AWS
API MCP server.

### Decision

Use the AWS CLI, bound to an IAM Identity Center SSO profile with the
`ReadOnlyAccess` permission set. Do not install the AWS API MCP server.

### Why

#### Token efficiency

MCP tool definitions are injected into the context window at session start
and persist for the full session. The `aws-api-mcp-server` schema consumes
several thousand tokens before the first prompt is sent. Stacking multiple
AWS MCP servers (cost-explorer, cloudwatch, cfn) compounds this.

The CLI costs zero upfront tokens. Claude already knows the syntax from
training and invokes it through the Bash tool.

#### Security surface

The MCP server is additional code running inside the agent's trust boundary,
with its own release cadence and supply chain. The CLI is a signed AWS-vendor
binary already present on the system.

Both paths use the same IAM credentials underneath, so the effective AWS
permissions are identical. The CLI simply has fewer moving parts between the
agent and the API.

Read-only is enforced at the IAM layer via the `ReadOnlyAccess` permission
set, not at the tool layer. This holds regardless of which client the agent
uses.

#### Functional parity

For the read-only, describe/list/get workload that Claude Code performs
against AWS (inventory, cost signals, resource configuration, log and metric
reads), the CLI and the generic AWS API MCP server expose the same
operations. The MCP server offers no capability the CLI lacks.

#### Speed

Both ultimately hit the same AWS API endpoints. Wall-clock time is dominated
by AWS latency; neither transport is meaningfully faster.

### When a specialized MCP server is justified

A purpose-built MCP server (for example `cost-explorer-mcp` or
`cloudwatch-mcp`) earns its context cost when it replaces a multi-call CLI
pattern with a single semantic operation, for example a grouped cost pivot
with forecasting that would otherwise require five or six chained `aws ce`
calls and JSON parsing.

Evaluate these case by case. The generic `aws-api-mcp-server` is not in
this category and is not used.

### Authentication

Authentication happens outside the agent session via `aws sso login`. The
agent never initiates login, never handles credentials, and never refreshes
tokens. On token expiry the agent pauses and the user re-authenticates in a
separate terminal.

### Enforcement

The user-level `CLAUDE.md` carries the operational policy: required profile
shape, allowed verbs, forbidden verbs, and the identity check run once per
session.

## Repository Structure

```text
claude-config/
├── CLAUDE.md              # Repo-level Claude instructions
├── README.md              # This file
├── .mise.toml             # mise tools (hk, pkl, rumdl, trufflehog, jq) + tasks
├── hk.pkl                 # hk git-hook config (pre-commit, check, fix)
├── .rumdl.toml            # rumdl config (markdown line-length 100)
├── generic_settings.json  # Shared Claude settings merged on sync
├── hooks/
│   └── block-commands.sh  # PreToolUse Bash guard
├── user_memory/
│   └── CLAUDE.md          # User-level instructions (copy to ~/.claude/)
└── skills/
    └── [skill-name]/
        ├── SKILL.md       # Skill definition
        └── references/    # Optional supporting docs
```

## Development

Tooling and git hooks are managed with [mise](https://github.com/jdx/mise) (tool versions + task
runner) and [hk](https://github.com/jdx/hk) (git hook runner).

**Setup:**

```bash
brew install mise        # one-time, if not already installed
mise run bootstrap       # mise install (tools) + hk install (git hooks)
```

**Tasks:**

```bash
mise tasks               # list available tasks
mise run sync            # sync hook + settings + user CLAUDE.md into ~/.claude and ~/.claude-dpg
```

**Checks:**

`pre-commit` runs automatically on `git commit`: [rumdl](https://github.com/jdx/rumdl) lints and
auto-fixes Markdown, and trufflehog scans staged files for secrets. Run them manually with:

```bash
hk check                 # report issues
hk fix                   # apply fixes
```

On Git 2.54+ hk stores hooks as git config, not scripts in `.git/hooks/`. Verify with
`git config --get-regexp '^hook\.'` (an empty `.git/hooks/` is expected).

## License

MIT
