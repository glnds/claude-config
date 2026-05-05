#!/bin/bash
# Block commands that should only be run by humans, not AI agents.
#
# Philosophy: some commands encode workflow assumptions (correct env,
# correct profile, intent confirmation) that should not be made on a
# user's behalf. Hooks fire even in bypass mode; exit code 2 stops
# the tool call before permission rules are evaluated.
#
# Configuration: edit the variables below or override via environment.

# --- Configuration -----------------------------------------------------------

# Block all `make` invocations. Set to "false" to disable.
BLOCK_MAKE="${CLAUDE_BLOCK_MAKE:-true}"

# Comma-separated list of substrings. Any AWS profile name (or, more
# broadly, any aws CLI command) containing one of these substrings
# (case-insensitive) is blocked.
# Example: "admin,root,prod"
BLOCKED_PROFILE_SUBSTRINGS="${CLAUDE_BLOCKED_PROFILE_SUBSTRINGS:-admin}"

# -----------------------------------------------------------------------------

input=$(cat)
command=$(echo "$input" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"command"[[:space:]]*:[[:space:]]*"\(.*\)"/\1/')

# --- Check 1: make -----------------------------------------------------------

if [ "$BLOCK_MAKE" = "true" ]; then
    if echo "$command" | grep -qE '(^|[;&|`$(])[[:space:]]*(env[[:space:]]+[^;&|]*)?([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]+[[:space:]]+)*g?make($|[[:space:]]|;|&|\|)'; then
        cat >&2 <<'EOF'
Blocked: `make` invocations are not permitted.

Makefiles in this repository are written for humans, not AI agents. They
encode workflow assumptions (active AWS profile, environment, confirmation
prompts) that should not be made on the user's behalf.

Do NOT work around this block by reading the Makefile and running its
recipe commands manually — that defeats the purpose of the block. Ask the
user to run the target themselves (e.g. `! make <target>` in the prompt
so output lands in the conversation).
EOF
        exit 2
    fi
fi

# --- Check 2: AWS profiles containing blocked substrings ---------------------
# Precise match on --profile / AWS_PROFILE / AWS_DEFAULT_PROFILE references.
# Produces a focused error message for the common case.

if [ -n "$BLOCKED_PROFILE_SUBSTRINGS" ]; then
    # Extract every AWS profile name referenced in the command, in any form:
    #   --profile <name>     --profile=<name>
    #   AWS_PROFILE=<name>   AWS_DEFAULT_PROFILE=<name>
    # Profile names per AWS spec: letters, digits, hyphen, underscore, dot, @.
    profiles_used=$(echo "$command" | grep -oE '(--profile[=	 ]+|AWS_PROFILE=|AWS_DEFAULT_PROFILE=)[A-Za-z0-9_.@-]+' \
                                    | sed -E 's/(--profile[=	 ]+|AWS_PROFILE=|AWS_DEFAULT_PROFILE=)//')

    if [ -n "$profiles_used" ]; then
        IFS=',' read -ra substrings <<< "$BLOCKED_PROFILE_SUBSTRINGS"

        # Iterate every (profile, substring) pair, case-insensitive
        while IFS= read -r profile; do
            [ -z "$profile" ] && continue
            profile_lower=$(echo "$profile" | tr '[:upper:]' '[:lower:]')

            for substring in "${substrings[@]}"; do
                substring=$(echo "$substring" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                [ -z "$substring" ] && continue
                substring_lower=$(echo "$substring" | tr '[:upper:]' '[:lower:]')

                case "$profile_lower" in
                    *"$substring_lower"*)
                        cat >&2 <<EOF
Blocked: the AWS profile "${profile}" matches the restricted pattern
"${substring}" and cannot be used by Claude Code.

Profiles containing this substring are reserved for human operators because
they typically carry elevated privileges that require human judgment,
confirmation, and accountability. If the action you are attempting requires
this profile, stop and ask the user to perform it themselves.

For other AWS work, use a profile with appropriately scoped permissions.
EOF
                        exit 2
                        ;;
                esac
            done
        done <<< "$profiles_used"
    fi
fi

# --- Check 3: any aws CLI command mentioning a blocked substring -------------
# Catches profile/role/ARN/policy/etc. references the structured check above
# misses. Broad on purpose — false positives fail safely (human takes over).

if [ -n "$BLOCKED_PROFILE_SUBSTRINGS" ]; then
    # Detect whether the command invokes the aws CLI at all.
    # Matches `aws ` at start of command, after env-var prefix, or after
    # a shell separator (; && || | etc.). Avoids matching "paws" or "saws".
    if echo "$command" | grep -qE '(^|[;&|`$(])[[:space:]]*(env[[:space:]]+[^;&|]*)?([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]+[[:space:]]+)*aws([[:space:]]|$)'; then

        command_lower=$(echo "$command" | tr '[:upper:]' '[:lower:]')
        IFS=',' read -ra substrings <<< "$BLOCKED_PROFILE_SUBSTRINGS"

        for substring in "${substrings[@]}"; do
            substring=$(echo "$substring" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            [ -z "$substring" ] && continue
            substring_lower=$(echo "$substring" | tr '[:upper:]' '[:lower:]')

            case "$command_lower" in
                *"$substring_lower"*)
                    cat >&2 <<EOF
Blocked: this aws CLI command references the restricted pattern
"${substring}" and cannot be run by Claude Code.

This catches profile names, role ARNs, IAM resources, and other admin-
flavored references. If you genuinely need to run this command, ask the
user to run it themselves so a human can confirm the intent.
EOF
                    exit 2
                    ;;
            esac
        done
    fi
fi

exit 0
