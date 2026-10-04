#!/bin/bash
# Stop: if files changed but no docs did, block once to update docs.
in=$(cat)
[ "$(jq -r '.stop_hook_active // false' <<<"$in")" = "true" ] && exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
changed=$(git status --porcelain | awk '{print $NF}')
[ -z "$changed" ] && exit 0
grep -qiE '(^|/)(README|AGENTS|CLAUDE)\.md$|(^|/)docs/|\.md$' <<<"$changed" && exit 0
jq -n '{decision:"block",reason:"Files changed, no docs touched. Update README/AGENTS.md/docs if affected; else reply \"docs unaffected\"."}'
