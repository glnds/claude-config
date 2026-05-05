.PHONY: help install install-settings

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Copy user CLAUDE.md to ~/.claude/
	cp user_memory/CLAUDE.md ~/.claude/CLAUDE.md

install-settings: ## Install hook + merge generic_settings.json into <dir>/settings.json (default ~/.claude). Usage: make install-settings [<dir>]
	@command -v jq >/dev/null 2>&1 || { echo "jq required but not installed" >&2; exit 1; }
	@DIR="$(filter-out $@,$(MAKECMDGOALS))"; \
	DIR="$${DIR:-$(HOME)/.claude}"; \
	mkdir -p "$$DIR/hooks"; \
	cp hooks/block-commands.sh "$$DIR/hooks/block-commands.sh"; \
	chmod +x "$$DIR/hooks/block-commands.sh"; \
	echo "Installed hook -> $$DIR/hooks/block-commands.sh"; \
	SETTINGS="$$DIR/settings.json"; \
	if [ -f "$$SETTINGS" ]; then \
		jq -s '.[0] + .[1]' "$$SETTINGS" generic_settings.json > "$$SETTINGS.tmp" && mv "$$SETTINGS.tmp" "$$SETTINGS"; \
		echo "Merged generic_settings.json -> $$SETTINGS"; \
	else \
		cp generic_settings.json "$$SETTINGS"; \
		echo "Created $$SETTINGS from generic_settings.json"; \
	fi

# Catch-all so positional args (e.g. paths) passed to install-settings
# don't fail as unknown make targets.
%:
	@:
