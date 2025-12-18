# Fix PR Review Comment

---
description: Fix issues from Claude bot code review comments on current branch's PR
argument-hint: [issue_number] [--all] [--skip-tests]
model: claude-sonnet-4-20250514
allowed-tools: Bash(gh:*), Bash(git:*), Read, Write, Edit
---

Fix issues identified in Claude bot code review comments. By default, fixes the highest severity unaddressed issue from the latest review.

## Arguments

- `issue_number` (optional): Specific issue number (1, 2, 3...) from the review to fix. If omitted, picks highest severity.
- `--all`: Fix all issues in sequence
- `--skip-tests`: Skip test verification (use sparingly)

## Step 1: Context Detection

```bash
# Get current branch name and verify not on main/master
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "Error: Cannot run from main/master branch. Checkout a feature branch first."
  exit 1
fi

# Get PR info from current branch
gh pr view --json number,headRefName,url,state
```

Extract owner/repo:

```bash
OWNER=$(gh repo view --json owner -q .owner.login)
REPO=$(gh repo view --json name -q .name)
NUMBER=$(gh pr view --json number -q .number)
```

**Validations:**

- If no PR exists for this branch, stop and inform the user
- If PR is already merged/closed, stop and inform the user

## Step 2: Find Claude Review Comment

Fetch PR issue comments and find the latest Claude code review:

```bash
# Get all issue comments on the PR
gh api repos/$OWNER/$REPO/issues/$NUMBER/comments --jq '.[] | {id, body, created_at, html_url}'
```

**Identify Claude review comments by pattern:**

- Body starts with `## Code Review - PR #`
- Contains `### 🔍 **Potential Issues**` section
- Contains severity markers: `(CRITICAL)`, `(MEDIUM)`, `(LOW)`

**Select the most recent review comment.**

If no Claude review found, report: "No Claude code review comments found on this PR" and stop.

## Step 3: Parse Review Issues

Extract issues from the `### 🔍 **Potential Issues**` section.

Each issue has this structure:

```markdown
#### 1. **Issue Title (SEVERITY)**
**Location:** `file.js:line-range`, `other-file.js:line`

\`\`\`javascript
// problematic code snippet
\`\`\`

**Problem:** Description of the issue

**Recommendation:** Suggested fix with code example
```

Parse into structured list:

- Issue number (1, 2, 3...)
- Title
- Severity (CRITICAL, MEDIUM, LOW)
- Location(s) - file paths and line numbers
- Problem description
- Recommendation/fix suggestion

**Priority order:** CRITICAL > MEDIUM > LOW

If `$ARGUMENTS` contains a specific issue number, select that issue.
Otherwise, select the highest severity unaddressed issue.

## Step 4: Check if Already Fixed

Before making changes, verify the issue isn't already addressed:

```bash
# Check recent commits for related changes
git log --oneline -10
git diff origin/main -- <file_path>
```

Read the file(s) at the specified location(s) and check if the recommendation is already implemented.

**If already fixed:**

- Note which commit fixed it
- Move to next issue (or stop if no more issues)

## Step 5: Implement the Fix

1. Read the relevant file(s) at the specified locations
2. Understand the problem and recommendation
3. Implement the fix following the recommendation
4. Keep changes minimal and focused

**For common patterns:**

- Memory leak (duplicate listeners): Add idempotency guard
- Missing cleanup: Add cleanup function or flag
- Test issues: Update test file accordingly

## Step 6: Verify the Fix

Unless `--skip-tests` is specified:

```bash
# Detect and run appropriate test/lint commands based on project
npm test 2>&1 || yarn test 2>&1 || pnpm test 2>&1
python -m pytest 2>&1
go test ./... 2>&1
```

**If tests fail:**

- Attempt to fix test failures
- If unable to fix, revert changes and report: "Fix causes test failures, manual intervention needed"
- Do NOT commit broken code

## Step 7: Commit and Push

```bash
git add -A
git commit -m "fix: <issue title from review>

<brief description of what was fixed>

Addresses review issue #<N> (<SEVERITY>)
Review: <comment_url>"
git push
```

**If push fails:**

- Check for upstream changes: `git fetch && git status`
- If behind, pull and retry

## Step 8: Reply to Review Comment

```bash
gh api repos/$OWNER/$REPO/issues/$NUMBER/comments \
    -f body="Fixed issue #<N> (**<Title>**) in commit <sha>.

**Changes:**
- <bullet points of changes made>

Remaining issues: <count> (<severities>)"
```

## Step 9: Continue or Complete

If `--all` is specified and more issues remain:

- Return to Step 4 with the next highest severity issue
- Continue until all issues are addressed

Otherwise, report completion:

```
Fixed: Issue #<N> - <Title> (<SEVERITY>)
Commit: <sha>
Tests: passed/skipped

Remaining issues from review:
- #2: <Title> (MEDIUM)
- #3: <Title> (LOW)

Run again to fix next issue, or use --all to fix all.
```

## Notes

- Claude bot posts code reviews as PR comments, not inline review threads
- Reviews follow a structured format with numbered issues and severity levels
- Focus on CRITICAL issues first as they may block merging
- The `--all` flag processes issues in severity order, not numerical order
