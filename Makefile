.PHONY: help sync

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

sync: ## Sync hook, settings, and user CLAUDE.md into ~/.claude and ~/.claude-dpg
	@command -v jq >/dev/null 2>&1 || { echo "jq required but not installed" >&2; exit 1; }
	@for DIR in "$(HOME)/.claude" "$(HOME)/.claude-dpg"; do \
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
		fi; \
		cp user_memory/CLAUDE.md "$$DIR/CLAUDE.md"; \
		echo "Installed user CLAUDE.md -> $$DIR/CLAUDE.md"; \
	done
