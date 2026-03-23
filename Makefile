.PHONY: help install

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Copy user CLAUDE.md to ~/.claude/
	cp user_memory/CLAUDE.md ~/.claude/CLAUDE.md
