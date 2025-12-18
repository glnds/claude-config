# Fix PR Review Comment

---
description: Fix the latest (or specified) PR review comment on current branch
argument-hint: [comment_id] [--resolve] [--skip-tests] [--include-outdated]
model: claude-sonnet-4-20250514
allowed-tools: Bash(gh:*), Bash(git:*), Read, Write, Edit
---

Fix a PR review comment. By default, picks the latest unresolved, non-outdated comment on the current branch's PR.

## Arguments
- `comment_id` (optional): Specific comment ID or URL. If omitted, uses latest unresolved comment.
- `--resolve`: Also resolve the thread after fixing
- `--skip-tests`: Skip test verification (use sparingly)
- `--include-outdated`: Include outdated comments (normally skipped)

## Step 1: Context Detection

```bash
# Get current branch name and verify not on main/master
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "Error: Cannot run from main/master branch. Checkout a feature branch first."
  exit 1
fi

# Get PR info from current branch
gh pr view --json number,headRefName,url,state,baseRefName
```

Extract owner/repo from the URL or use:
```bash
gh repo view --json owner,name
```

**Validations:**
- If no PR exists for this branch, stop and inform the user
- If PR is already merged/closed, stop and inform the user

## Step 2: Get Target Comment

If `$ARGUMENTS` contains a comment ID or URL, extract and use that (skip outdated filtering for explicit targets).

Otherwise, fetch the latest unresolved, non-outdated comment:

```bash
# Extract values from Step 1 output
OWNER=$(gh repo view --json owner -q .owner.login)
REPO=$(gh repo view --json name -q .name)
NUMBER=$(gh pr view --json number -q .number)

# Get all review threads with outdated status
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

**Filtering logic:**
1. Filter for `isResolved: false`
2. Unless `--include-outdated` is specified, also filter for `isOutdated: false` (thread level) AND `outdated: false` (comment level)
3. Sort remaining by `createdAt` descending
4. Take the first one

**If no actionable comments exist:**
- If there ARE unresolved but outdated comments, report: "Found X unresolved comments but all are outdated (code has changed). Use --include-outdated to process them, or they may auto-resolve on next push."
- If truly none, report: "No unresolved review comments found" and stop

## Step 3: Analyze the Comment

Read the comment body and referenced code location.

**If targeting a specific comment that is marked `outdated: true`:**
- Check the current state of the file at the referenced path
- Determine if the concern is still valid despite code changes
- If the issue no longer exists, reply: "This has been addressed by subsequent changes to the code" and resolve if `--resolve` specified, then stop

**Evaluation checklist:**
1. Is this a valid concern or false positive?
2. Does the referenced code still exist at the specified path/line?
3. Does the suggestion align with project conventions?
4. Would implementing it break existing functionality?
5. Is this a duplicate of another comment already addressed?

**If the comment is invalid or no longer applicable:**
- Reply explaining why (e.g., "This code was refactored in commit abc123" or "This is a false positive because...")
- If `--resolve` specified, resolve the thread
- Stop here

## Step 4: Check Current State

Before making changes, verify the issue isn't already fixed:

```bash
# Check if the specific issue mentioned is already addressed
git log --oneline -10
git diff origin/main -- <file_path>
```

**If already fixed:**
- Find the commit that fixed it
- Reply: "Already addressed in commit {sha}"
- If `--resolve` specified, resolve the thread
- Stop here

## Step 5: Implement the Fix

- Read the relevant file(s)
- Make the necessary code changes
- Keep changes minimal and focused on the comment

## Step 6: Verify the Fix

Unless `--skip-tests` is specified:

```bash
# Detect and run appropriate test/lint commands
# Common patterns - adapt to project:
npm test 2>&1 || yarn test 2>&1 || pnpm test 2>&1
npm run lint 2>&1 || yarn lint 2>&1
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
git commit -m "fix: address review comment on <file>

<brief description of what was fixed>

Addresses: <comment_url>"
git push
```

**If push fails:**
- Check for upstream changes: `git fetch && git status`
- If behind, pull and retry
- If branch protection blocks push, report the error

## Step 8: Reply to Comment

```bash
gh api -X POST repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies \
    -f body="Fixed in commit {commit_sha}.

{brief description of the fix}"
```

## Step 9: Resolve Thread (if --resolve specified)

Only if `--resolve` is in `$ARGUMENTS`:

```bash
# Get thread ID for this comment
THREAD_ID=$(gh api graphql -f query='...' | jq -r '...')

# Resolve it
gh api graphql -f query='
mutation {
  resolveReviewThread(input: {threadId: "'$THREAD_ID'"}) {
    thread { isResolved }
  }
}'
```

## Summary Output

Report:
- Comment addressed: {comment_url}
- Author: {comment_author}
- File changed: {path}:{line}
- Commit: {sha}
- Tests: passed/skipped
- Thread resolved: yes/no

If there are remaining unresolved comments:
- Remaining actionable comments: X
- Remaining outdated comments: Y (use --include-outdated or they may auto-clear)

## Notes

- GitHub marks comments as "outdated" when the referenced code changes, even if the underlying issue isn't fixed
- The Claude GitHub bot creates new comments on each push, so older comments on the same issue become outdated
- Focus on the latest comment to avoid duplicate work
- Use `--include-outdated` only if you specifically need to address a stale comment
