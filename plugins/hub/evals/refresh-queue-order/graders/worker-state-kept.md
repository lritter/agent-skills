---
type: regex
# Workers own their state: refresh leaves the rollout's after-merge state and steps alone.
pattern: 'state: after-merge\s*\n[\s\S]*after_merge: \[prod promote\]'
target: { source: file, path: .local/ai/hub/sessions/sth-102-alpha-rollout.md }
---
