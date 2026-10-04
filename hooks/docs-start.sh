#!/bin/bash
# SessionStart: tell Claude to read the project docs first.
files=""
for f in README.md AGENTS.md CLAUDE.md; do [ -f "$f" ] && files="$files $f"; done
[ -d docs ] && files="$files docs/"
[ -z "$files" ] && exit 0
jq -n --arg f "$files" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:("Before any work, read project docs:" + $f)}}'
