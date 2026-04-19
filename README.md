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

### Project Memory

Tools that give AI coding agents persistent memory about your project:

- [Beads](https://github.com/steveyegge/beads): Git-backed distributed issue tracker for AI
  agents. Maintains task dependencies and work state across sessions.

### User Memory

The `user_memory/CLAUDE.md` file contains user-level instructions that apply across all projects.
Copy to `~/.claude/CLAUDE.md` for global application.

**Key directives:**

- Conciseness over grammar in all interactions
- Clarify before implementing (never assume)
- Test-driven development (red-green-refactor)
- GitHub issue integration
- Markdown linting with markdownlint-cli2

### Skills

Skills extend Claude Code with structured workflows. Each skill contains frontmatter metadata
and step-by-step instructions.

#### make-note (v1.2)

Creates Obsidian notes with intelligent tag suggestions from existing vault patterns.

**Trigger:** "create a note", "make a note", "save to Obsidian"

#### sparring (v1.0)

Critical thinking partner for technical concepts. Researches Obsidian notes for context,
identifies gaps and assumptions, provides constructive challenge.

**Trigger:** "let's spar on...", "challenge my thinking on..."

#### text-enhancer (v1.0)

Enhances professional/technical text with grammar, clarity, and factual verification while
preserving authentic style.

**Trigger:** "enhance [text]", "polish [text]"

#### verbalized-sampling (v1.0)

Prompt engineering technique to overcome LLM mode collapse by generating multiple responses
with probability distributions.

**Trigger:** "use verbalized sampling", "show multiple responses with probabilities"

#### zellij-config (v1.3)

Zellij terminal multiplexer configuration: layouts, themes, keybindings, plugins.
Config location: `~/dotfiles/.config/zellij/`

**Trigger:** "configure zellij", "create a zellij layout"

## Repository Structure

```text
claude-config/
├── CLAUDE.md              # Repo-level Claude instructions
├── README.md              # This file
├── user_memory/
│   └── CLAUDE.md          # User-level instructions (copy to ~/.claude/)
└── skills/
    └── [skill-name]/
        ├── SKILL.md       # Skill definition
        └── references/    # Optional supporting docs
```

## License

MIT
