#!/usr/bin/env bash
# Destination in your repo: .claude/hooks/check-okf-version.sh
# No chmod needed: settings.json invokes this via `bash`.
#
# SessionStart hook: compares the OKF version this repo declares in docs/index.md
# against the latest spec version published on the OKF main branch. When they
# differ, it injects a note into Claude's context; the "OKF version policy"
# section in CLAUDE.md tells Claude what to do about it.
# Fails silent (exit 0, no output) when offline or if the spec layout changes.

SPEC_URL="https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md"
ROOT="${CLAUDE_PROJECT_DIR:-.}"

latest=$(curl -fsSL --max-time 5 "$SPEC_URL" 2>/dev/null \
  | grep -m1 -oE 'Version [0-9]+\.[0-9]+' | grep -oE '[0-9]+\.[0-9]+')
declared=$(grep -m1 -oE 'okf_version:[[:space:]]*"?[0-9]+\.[0-9]+"?' "$ROOT/docs/index.md" 2>/dev/null \
  | grep -oE '[0-9]+\.[0-9]+')

[ -z "$latest" ] && exit 0

if [ "$latest" != "$declared" ]; then
  cat <<EOF
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "OKF version check: the latest OKF spec version on the official main branch is $latest. This repo's docs/index.md declares okf_version ${declared:-(none)}. The OKF version policy in CLAUDE.md applies."}}
EOF
fi

exit 0
