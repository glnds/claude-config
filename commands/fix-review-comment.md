# Fix PR Review Comment

---
description: Fix issues from Claude Code Action reviews (inline threads and PR comments)
argument-hint: [issue_number] [--all] [--skip-tests] [--inline] [--comments]
model: claude-sonnet-4-20250514
allowed-tools: Bash(gh:*), Bash(git:*), Read, Write, Edit
---

Fix issues identified in Claude Code Action reviews. Checks both inline review threads and PR issue comments. By default, fixes the highest severity unaddressed issue.

## Arguments

- `issue_number` (optional): Specific issue number to fix. If omitted, picks highest severity.
- `--all`: Fix all issues in sequence
- `--skip-tests`: Skip test verification (use sparingly)
- `--inline`: Only check inline review threads
- `--comments`: Only check PR issue comments

## Output Behavior

- Do NOT output intermediate status messages during data gathering
- Only report findings after all sources have been checked and merged
- Treat empty results from any single source as normal (check all sources before reporting)
- If no actionable issues are found across ALL sources, then report "No unresolved review issues found"

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

## Step 2: Find Review Feedback

Check both inline review threads AND PR issue comments (unless filtered by flags).

### 2a. Check Inline Review Threads (GraphQL)

Skip if `--comments` flag is specified.

```bash
gh api graphql -f query='
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          comments(first: 10) {
            nodes {
              databaseId
              body
              path
              line
              outdated
              createdAt
              author { login }
              url
            }
          }
        }
      }
    }
  }
}' -F owner="$OWNER" -F repo="$REPO" -F number="$NUMBER"
```

**Filter inline threads:**

1. `isResolved: false` - only unresolved
2. `isOutdated: false` - skip outdated (code changed)
3. Extract actionable issues from comment body

### 2b. Check PR Issue Comments (REST)

Skip if `--inline` flag is specified.

```bash
gh api repos/$OWNER/$REPO/issues/$NUMBER/comments
```

**Identify Claude review comments by patterns:**

- Contains `## Code Review` or `Code Review -`
- Contains severity markers: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
- Contains actionable markers: `**Problem:**`, `**Recommendation:**`, `**Location:**`
- Contains unchecked checklist items: `- [ ]`

**Select the most recent matching review comment.**

### 2c. Merge and Prioritize

**After checking ALL sources in 2a and 2b**, consolidate findings:

1. Collect all issues from both sources
2. For inline threads: each unresolved thread = 1 issue
3. For PR comments: parse structured issues from `### 🔍 **Potential Issues**` or similar sections
4. Assign severity from markers (default to MEDIUM if not specified)
5. Sort by severity: `CRITICAL > HIGH > MEDIUM > LOW`
6. Select target based on `$ARGUMENTS` or highest severity

**If no actionable issues found across all sources:**

- Report: "No unresolved review issues found on this PR" and stop

## Step 3: Parse Target Issue

**For inline review threads:**

- File path and line from thread metadata
- Issue description from comment body
- Look for severity markers in body

**For PR comment issues:**

Each issue typically has:

```markdown
#### N. **Issue Title (SEVERITY)**
**Location:** `file.js:line-range`

**Problem:** Description

**Recommendation:** Suggested fix
```

Or checklist format:

```markdown
- [ ] Issue description (file.js:line)
```

Extract:

- Title/description
- Severity (CRITICAL, HIGH, MEDIUM, LOW)
- Location(s) - file paths and line numbers
- Problem description
- Recommendation/fix suggestion

## Step 4: Check if Already Fixed

Before making changes, verify the issue isn't already addressed:

```bash
git log --oneline -10
git diff origin/main -- <file_path>
```

Read the file(s) at specified location(s) and check if the recommendation is already implemented.

**If already fixed:**

- Note which commit fixed it
- For inline threads: consider resolving if `--resolve` would be added
- Move to next issue (or stop if no more)

## Step 5: Implement the Fix

1. Read the relevant file(s) at the specified locations
2. Understand the problem and recommendation
3. Implement the fix following the recommendation
4. Keep changes minimal and focused

**Common fix patterns:**

- Memory leak (duplicate listeners): Add idempotency guard
- Missing cleanup: Add cleanup function or flag
- Security issue: Apply recommended sanitization
- Test issues: Update test file accordingly

## Step 6: Verify the Fix

Unless `--skip-tests` is specified:

```bash
# Detect and run appropriate test/lint commands
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

## Step 8: Reply to Review

**For inline threads:**

```bash
gh api graphql -f query='
mutation($threadId: ID!, $body: String!) {
  addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
    comment { url }
  }
}' -F threadId="$THREAD_ID" -F body="Fixed in commit <sha>."
```

**For PR comment issues:**

```bash
gh api repos/$OWNER/$REPO/issues/$NUMBER/comments \
    -f body="Fixed issue #<N> (**<Title>**) in commit <sha>.

**Changes:**
- <bullet points of changes made>

Remaining issues: <count>"
```

## Step 9: Continue or Complete

If `--all` is specified and more issues remain:

- Return to Step 4 with the next highest severity issue
- Continue until all issues are addressed

Otherwise, report completion:

```
Fixed: Issue #<N> - <Title> (<SEVERITY>)
Source: inline thread / PR comment
Commit: <sha>
Tests: passed/skipped

Remaining issues:
- #2: <Title> (HIGH) [inline]
- #3: <Title> (MEDIUM) [comment]

Run again to fix next issue, or use --all to fix all.
```

## Notes

- Claude Code Action posts reviews via two methods:
  - **Inline review threads**: Code-specific comments at exact lines (GraphQL `reviewThreads`)
  - **PR issue comments**: General feedback, summaries, checklists (REST `/issues/{pr}/comments`)
- This command checks both sources and merges findings
- Reviews may follow different formats depending on prompt configuration
- Severity levels: `CRITICAL > HIGH > MEDIUM > LOW`
- Use `--inline` or `--comments` to filter to one source
- Inline threads have precise file/line info; PR comments may need parsing
