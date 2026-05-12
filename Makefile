.PHONY: help install install-settings sync

# Default target directory for install-settings. Override with `make install-settings DIR=~/.claude-dpg`.
DIR ?= $(HOME)/.claude

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Copy user CLAUDE.md to ~/.claude/
	cp user_memory/CLAUDE.md ~/.claude/CLAUDE.md

install-settings: ## Install hook + merge generic_settings.json into $(DIR)/settings.json. Override DIR=<path>.
	@command -v jq >/dev/null 2>&1 || { echo "jq required but not installed" >&2; exit 1; }
	@mkdir -p "$(DIR)/hooks"
	@cp hooks/block-commands.sh "$(DIR)/hooks/block-commands.sh"
	@chmod +x "$(DIR)/hooks/block-commands.sh"
	@echo "Installed hook -> $(DIR)/hooks/block-commands.sh"
	@SETTINGS="$(DIR)/settings.json"; \
	if [ -f "$$SETTINGS" ]; then \
		jq -s '.[0] + .[1]' "$$SETTINGS" generic_settings.json > "$$SETTINGS.tmp" && mv "$$SETTINGS.tmp" "$$SETTINGS"; \
		echo "Merged generic_settings.json -> $$SETTINGS"; \
	else \
		cp generic_settings.json "$$SETTINGS"; \
		echo "Created $$SETTINGS from generic_settings.json"; \
	fi

sync: ## Install settings to both ~/.claude and ~/.claude-dpg
	@$(MAKE) --no-print-directory install-settings DIR=$(HOME)/.claude
	@$(MAKE) --no-print-directory install-settings DIR=$(HOME)/.claude-dpg
