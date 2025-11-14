# Claude Skills

Custom skills that extend Claude Code's functionality through structured workflows and integrations.

## What are Skills?

Skills are capabilities defined in markdown files that Claude Code can invoke
to perform specialized tasks. Each skill contains:

- **Frontmatter metadata**: Name, description, version, license
- **Workflow instructions**: Step-by-step execution logic
- **Integration patterns**: MCP server tools, user interactions

## Available Skills

### make-note

**Version:** 1.1
**License:** MIT

Creates structured notes in Obsidian with intelligent tag suggestions based on
existing vault patterns.

**Invocation:** Ask Claude to "create a note", "make a note", or "save content
to Obsidian"

**Key Features:**

- Analyzes existing vault to identify common tag patterns
- Suggests 3-5 relevant tags based on note content
- Waits for user confirmation before creating note
- Creates notes in Resources folder with proper frontmatter
- Supports hierarchical tags (e.g., `ai/code-agent`, `dpg/strategy`)

**Workflow:**

1. Scans vault using `mcp-obsidian` server to get tag frequencies
2. Suggests relevant tags matching note content (3+ occurrences prioritized)
3. Presents options as numbered list for easy selection
4. Creates note with confirmed tags in Resources folder
5. Reports filepath and applied tags

**Output Format:**

```yaml
---
tags:
- tag1
- tag2
created: DD-MM-YYYY HH:MM
---

# [[Note Title]]

Content here...

## References
- [Link](URL)

## Related Notes
- [[Related Note]]
```

**Tag Conventions:**

- Lowercase with hyphens for multi-word tags
- Hierarchical structure using `/` (e.g., `cloud/aws`)
- 3-5 tags per note (general + specific)

## Repository Structure

```text
claude-skills/
├── README.md
├── CLAUDE.md              # Guidance for Claude Code
├── LICENSE
└── [skill-name]/
    └── SKILL.md          # Skill definition
```

## Creating Skills

Each skill requires:

1. Directory named after skill (lowercase, hyphenated)
2. `SKILL.md` with YAML frontmatter and workflow
3. Clear trigger phrases in description
4. User confirmation points for actions
5. MCP tool integration (if external systems involved)

See [CLAUDE.md](CLAUDE.md) for detailed guidelines.

## License

MIT
