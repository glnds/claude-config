# Create GitHub Issue with TDD Plan

Create a well-defined GitHub issue for: $ARGUMENTS

> **Goal**: Gather clear requirements upfront to avoid assumptions during implementation.
> Every issue includes a TDD implementation plan.

## Step 1: Clarify the Request

Before creating anything, ask the user these questions (skip any already answered in $ARGUMENTS):

**Functional Requirements:**
1. What is the expected behavior? (What should happen?)
2. What triggers this behavior? (User action, API call, scheduled task?)
3. What are the inputs and expected outputs?

**Scope & Boundaries:**
4. What is explicitly OUT of scope?
5. Are there edge cases to handle? (empty inputs, errors, limits)

**Context:**
6. Is this a new feature, bug fix, or improvement?
7. Are there existing patterns in the codebase to follow?

**Acceptance Criteria:**
8. How do we know this is "done"? (Be specific)

Wait for answers before proceeding.

## Step 2: Summarize Understanding

Present a summary to confirm understanding:

```
## My Understanding

**Problem/Feature**: [one sentence]

**Expected Behavior**:
- When [trigger], then [outcome]
- [additional behaviors]

**Out of Scope**:
- [explicit exclusions]

**Edge Cases**:
- [edge case 1]: [expected handling]
- [edge case 2]: [expected handling]
```

Ask: "Is this correct? Anything to add or change?"

Wait for confirmation.

## Step 3: Create the Issue

Use `gh issue create` with this structure:

```markdown
## Problem Statement
[Clear description of what needs to be solved]

## Expected Behavior
- When [trigger], then [outcome]
- [additional behaviors]

## Acceptance Criteria
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

## Out of Scope
- [What this issue will NOT address]

## Edge Cases
| Scenario | Expected Behavior |
|----------|-------------------|
| [edge case] | [handling] |

## Implementation Plan (TDD)

### Phase 1: Red (Write Failing Tests)
Tests to create based on acceptance criteria:
- [ ] Test: [criterion 1 as test]
- [ ] Test: [criterion 2 as test]
- [ ] Test: [edge case 1]
- [ ] Test: [edge case 2]

### Phase 2: Green (Implement)
- Implement minimum code to pass tests
- Do not modify tests during this phase

### Phase 3: Refactor
- Clean up implementation
- Ensure all tests still pass

## Notes
[Any additional context, links, or references]
```

## Rules

- NEVER create the issue without user confirmation on the summary
- NEVER skip the TDD implementation plan section
- ALWAYS include testable acceptance criteria (not vague statements)
- ALWAYS ask about edge cases explicitly
- If user gives vague requirements, ask follow-up questions
