# Fix GitHub Issue with TDD (Context-Optimized)

Analyze and implement a fix for GitHub issue: $ARGUMENTS

> **IMPORTANT**: This workflow uses subagent delegation to keep the main context window lean.
> Delegate research and verification tasks; only bring summaries back to main context.

## Phase 1: Understand the Issue

**Delegate to a subagent for issue research:**

Use the Explore subagent (or issue-researcher if available) to:
1. Run `gh issue view $ARGUMENTS` and read full issue details
2. Check for linked PRs, related issues, or discussion comments
3. Identify acceptance criteria from the issue description

Return ONLY a concise summary containing:
- Issue title and core problem statement
- Acceptance criteria (bullet points)
- Any blockers or dependencies mentioned

If acceptance criteria are unclear, list what you understand and ASK for confirmation before proceeding.

## Phase 2: Create Working Branch

1. Ensure you're on the latest main/master branch: `git fetch origin && git checkout main && git pull`
2. Create a feature branch: `git checkout -b fix/issue-$ARGUMENTS`
3. Confirm the branch was created successfully

## Phase 3: Research and Plan

**Delegate codebase exploration to a subagent:**

Use the Explore subagent with thoroughness level "medium" or "very thorough" to:
1. Search the codebase for files relevant to this issue
2. Identify existing test patterns and testing frameworks used
3. Find similar implementations or patterns to follow

Return ONLY:
- List of files to modify (with brief reason)
- New files to create (if any)
- Test file locations and patterns observed
- Key patterns or conventions to follow

**Then create the implementation plan:**
Based on the subagent's findings, create a written plan with:
- Files to modify and why
- Test cases to write (based on acceptance criteria)
- Implementation approach

**STOP and present this plan. Wait for approval before proceeding.**

## Phase 4: Write Failing Tests (TDD Red Phase)

This is TEST-DRIVEN DEVELOPMENT. Write tests FIRST.

1. Based on the acceptance criteria, write test cases that:
   - Cover the expected behavior described in the issue
   - Include edge cases
   - Follow existing test patterns discovered in Phase 3
2. DO NOT create mock implementations or stub the functionality
3. Run the tests and CONFIRM they fail with the expected failure reason
4. If tests pass unexpectedly, the issue may already be fixed or tests are incorrect

Commit the tests:
```bash
git add -A
git commit -m "test: add failing tests for issue #$ARGUMENTS"
```

## Phase 5: Implement the Fix (TDD Green Phase)

1. Write the minimum code necessary to make tests pass
2. DO NOT modify the tests during this phase
3. Run tests after each significant change
4. Continue iterating until ALL tests pass

Commit the implementation:
```bash
git add -A
git commit -m "fix: implement solution for issue #$ARGUMENTS"
```

## Phase 6: Refactor (TDD Refactor Phase)

1. Review the implementation for code quality, readability, and standards adherence
2. Refactor if needed while keeping tests green
3. Run the full test suite to ensure no regressions

If changes were made:
```bash
git add -A
git commit -m "refactor: clean up implementation for issue #$ARGUMENTS"
```

## Phase 7: Verification

**Delegate verification to a subagent:**

Use the Explore subagent (or test-runner if available) to:
1. Run the project's lint command
2. Run the project's type check command  
3. Run the full test suite
4. Report any failures

Only bring failure details into main context if issues need fixing.

## Phase 8: Create Pull Request

1. Push the branch: `git push -u origin fix/issue-$ARGUMENTS`
2. Create a PR using `gh pr create` with:
   - Title: `fix: [brief description] (closes #$ARGUMENTS)`
   - Body that includes:
     - Summary of changes
     - How it was tested
     - Reference to the issue: `Closes #$ARGUMENTS`

## Rules

**Context Management:**
- ALWAYS delegate research tasks to subagents
- Only bring concise summaries back to main context
- Use Explore subagent for read-only codebase analysis
- If custom subagents (issue-researcher, test-runner) exist, prefer those

**TDD Discipline:**
- NEVER skip the test-first approach
- NEVER modify tests to make them pass (fix the implementation instead)
- ALWAYS wait for plan approval before writing code

**Workflow:**
- If you encounter blockers or ambiguities, STOP and ask for clarification
- Keep commits atomic and well-described
