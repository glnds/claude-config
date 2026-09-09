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

## Permissions and auto mode

`generic_settings.json` runs Claude Code in auto mode (`permissions.defaultMode: "auto"`), which
routes each tool call through a classifier after the deterministic permissions system has had its
say. Three layers, each catching what the others cannot:

| Layer | What it is | What it catches |
|---|---|---|
| `permissions.deny` | Deterministic rules, evaluated first | `make`/`gmake`, and `Read()` on credential paths (`~/.aws/credentials`, `~/.ssh`, `~/.gnupg`, `~/.kube`, `.env`) |
| `hooks/block-commands.sh` | `PreToolUse` Bash hook, exit 2 blocks | `admin` AWS profiles via `--profile`, `--profile=`, `AWS_PROFILE=`, `AWS_DEFAULT_PROFILE=`; `make` behind env prefixes and shell separators. Fires even under `bypassPermissions`. |
| `autoMode` | Natural-language classifier rules | The fuzzy, intent-level cases the other two cannot enumerate — any mutating AWS operation, any elevated identity, workstation applies |

None of these is an enforcement boundary. The classifier is reasoning-blind by design: it sees user
messages and tool calls, never command output, so it cannot know a profile is privileged from a fact
that arrived via stdout, and nothing here stops a boto3 script or a renamed wrapper. Read-only is
enforced at the IAM layer, as described above; these layers reduce accidental misexecution and give
fast feedback.

### The `autoMode` block

Four array keys, all prose — the classifier reads them as natural-language rules, not as regex or
tool patterns. One asymmetry decides how to edit them:

- **`environment`** replaces all 21 built-in slots and must **not** contain `"$defaults"`. Keep the
  exact `**Slot name**: value` shape, and leave a slot at its shipped default text rather than
  guessing a value.
- **`allow`**, **`soft_deny`**, **`hard_deny`** are additive and must start with the literal entry
  `"$defaults"`. Omitting it discards every built-in rule in that section.

`hard_deny` entries block unconditionally; `soft_deny` entries can be cleared by explicit user
intent or by an `allow` entry. This repo sets two hard blocks and adds nothing to the other three
sections:

- **AWS Mutation & IaC Apply** — no AWS state change and no `terraform`/`cdk`/`sam`/`pulumi` apply
  from this machine, by any route. Read-only calls and read-only IaC (`plan`, `diff`, `synth`,
  `cfn-lint`) are explicitly carved out, including the Terraform backend's own state-lock writes.
- **Elevated AWS Identity** — no `admin` or otherwise privileged profile, no credential-env
  override, no `aws sso login`, no `assume-role` into another role.

Both are hard rather than soft because `CLAUDE.md` states them without exception, and because a hard
rule is evaluated first — a soft rule saying the same thing would be dead code behind it. Keep the
prose tight: these are read by a classifier on every tool call.

The classifier reads `autoMode` from user settings, managed settings and `--settings` only — never
from a project's `.claude/settings.json`, so a checked-in repo cannot inject its own allow rules.
That is why this block ships through `mise run sync` into `~/.claude/settings.json`.

Inspect it with:

```bash
claude auto-mode defaults    # the 21 built-in environment slots and every built-in rule
claude auto-mode config      # the effective merged config
claude auto-mode critique    # AI review of the custom rules
```

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
