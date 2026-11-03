---
type: llm
---

The skill under test writes a daily standup. The user ran `/standup finish the importer runbook
and pair with Priya on export pagination`, and answered the checkpoint with "Drop the Q4
planning meeting, everything else is fine." The reply may show the checkpoint draft first; judge
the **last** fenced block that holds a "Did:" and "Doing:" list. That block is the final list.

PASS only if all of these hold:
1. A final list exists: a fenced code block with "Did:" and "Doing:" sections.
2. Its Doing section covers both plans: the importer runbook, and pairing with Priya on export
   pagination. Tightened wording counts, and so does folding the pairing into an existing
   export-pagination bullet (for example "Paginate export — pairing with Priya").
3. The Q4 planning meeting is not in the final list. Mentioning outside the block that it was
   dropped is fine.
4. Each bullet is a single line, and each ticket or PR has a Markdown link somewhere in its
   bullet. A ticket id that's part of a linked PR's title counts as linked.

Text outside the final list (notes about the window, sources, what was left out) is not graded.

FAIL otherwise.
