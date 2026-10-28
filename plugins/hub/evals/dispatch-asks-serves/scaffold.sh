#!/usr/bin/env bash
# A repo with a hub: two stack projects (Alpha above Beta), two ad hoc items, six sessions.
# Every hub case carries a copy of this body.
set -euo pipefail
g() { git -c user.name=eval -c user.email=eval@example.com -c commit.gpgsign=false "$@"; }
git init -q -b main
echo "# demo" > README.md
g add README.md && g commit -qm init
H=.local/ai/hub
mkdir -p "$H/sessions/_done"

cat > "$H/stack.md" <<'EOF'
# Stack

hub_session: old-hub-11
claimed: 2026-10-27T09:00Z

## 1. Alpha
umbrella: STH-100
hub:
Next: STH-105, STH-106
Blocked:
Risk: prod promote takes 30 min

## 2. Beta
umbrella: STH-200
hub:
Next: STH-203
Blocked: waiting on design
Risk:

## History
- 2026-10-27 push Alpha at 1
- 2026-10-27 push Beta at 2
EOF

cat > "$H/adhoc.md" <<'EOF'
# Ad hoc

- decision: merge #12
  where: https://github.com/example/demo/pull/12
  unblocks: STH-203
  serves: Beta
  since: 2026-10-20
- decision: close STH-300
  where: STH-300
  unblocks:
  serves:
  since: 2026-10-25
EOF

session() { # handle serves kind state needs after_merge updated pr parent
  cat > "$H/sessions/$1.md" <<EOF
---
handle: $1
session: $1-ab
parent: ${9:-old-hub-11}
branch: $1
ticket: STH-$(echo "$1" | cut -d- -f2)
serves: $2
kind: $3
state: $4
needs: $5
pr: $8
after_merge: $6
handoff: /tmp/handoff-$1.md
updated: $7
---

## Log
- 2026-10-27 dispatched by old-hub-11 (queued)
EOF
}
session sth-101-alpha-api    Alpha implement needs-user "sign off on the plan" "[]" 2026-10-27T10:00Z ""
session sth-201-beta-ui      Beta  implement needs-user "rule on review findings" "[]" 2026-10-26T15:00Z "https://github.com/example/demo/pull/14"
session sth-102-alpha-rollout Alpha rollout after-merge "" "[prod promote]" 2026-10-27T12:00Z "https://github.com/example/demo/pull/9"
session sth-103-alpha-done   Alpha implement done "" "[]" 2026-10-26T08:00Z "https://github.com/example/demo/pull/8"
session sth-202-beta-cleanup Beta  implement done "" "[run the backfill tool in prod]" 2026-10-25T08:00Z "https://github.com/example/demo/pull/7"
session sth-104-alpha-review Alpha review running "" "[]" 2026-10-27T11:00Z "" sth-101-alpha-api-ab
