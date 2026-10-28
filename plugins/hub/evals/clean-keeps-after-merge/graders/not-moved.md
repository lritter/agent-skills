---
type: regex
# Nothing is archived before the user confirms: the candidate's file is still in sessions/.
# (A regex on the file, since file_exists didn't resolve under .local/ in this harness.)
pattern: 'handle: sth-103-alpha-done'
target: { source: file, path: .local/ai/hub/sessions/sth-103-alpha-done.md }
---
