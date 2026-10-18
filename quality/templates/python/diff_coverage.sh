#!/usr/bin/env bash
set -euo pipefail
BASE="$1"
mkdir -p .quality/out
uv run pytest -q --cov --cov-branch --cov-report=xml:.quality/out/coverage.xml
uv run diff-cover .quality/out/coverage.xml --compare-branch="$BASE" --include-untracked --fail-under=90
