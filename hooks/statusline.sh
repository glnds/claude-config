#!/bin/bash
# Claude Code statusline: ccusage renders the stats, cship renders the context bar.
#
# Both tools consume the same session JSON on stdin, but settings.json allows
# only one statusLine command -- hence this wrapper. stdin is single-use, so it
# is read once and replayed into each binary.
#
# Failures degrade rather than abort: a non-zero exit from either tool would
# otherwise blank the entire statusline. Whatever half succeeded still renders.

set -uo pipefail

input=$(cat)

stats=$(printf '%s' "$input" | ccusage statusline \
    --context-low-threshold 20 --context-medium-threshold 60 2>/dev/null) || stats=""
bar=$(printf '%s' "$input" | cship 2>/dev/null) || bar=""

if [ -n "$stats" ] && [ -n "$bar" ]; then
    printf '%s | %s\n' "$stats" "$bar"
else
    printf '%s%s\n' "$stats" "$bar"
fi
