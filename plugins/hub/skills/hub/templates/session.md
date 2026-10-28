---
handle: <handle>
session:
parent: <ListAgents name of the dispatching session>
branch: <branch>
ticket: <ticket id, or blank>
serves: <stack project, or adhoc>
kind: <implement | review | analysis | rollout | other>
state: queued
needs:
pr:
after_merge: []
handoff: <absolute path to the handoff doc>
updated: <ISO time>
---

## Log
- <YYYY-MM-DD HH:MMZ> dispatched by <parent> (queued)
