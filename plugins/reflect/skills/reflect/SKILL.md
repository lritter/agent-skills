---
name: reflect
description: Analyze conversation for learnings and update relevant skills. Use at end of session or when you want to capture a correction/preference.
disable-model-invocation: true
---

# Reflect: Learn from Conversation

Analyze the current conversation for corrections, preferences, and patterns, then update relevant skill files.

## When to Use

- End of a productive session where you made corrections
- After explicitly stating a preference ("always do X", "never do Y")
- When you say "remember this" or similar
- Anytime you want to capture learnings for future sessions

## Process

### Step 1: Scan for Signals

Analyze the full conversation looking for:

**Corrections** (High confidence)

- "No, use X instead"
- "Actually, always do Y"
- "Don't do that, do this"
- Repeated corrections of the same mistake

**Explicit Instructions** (High confidence)

- "Always...", "Never..."
- "Remember to...", "Remember this"
- "Add this to the skill"
- "From now on..."

**Preferences** (Medium confidence)

- "I prefer..."
- "Let's use X for this"
- Consistent choices when given options

**Successful Patterns** (Medium confidence)

- Approaches that worked well and were confirmed
- Patterns you praised or approved

**Observations** (Low confidence)

- Single instances of behavior
- Implicit preferences not explicitly confirmed
- Patterns that might be situational

### Step 2: Discover Available Skills

Load skills from both locations:

```bash
# Global skills
ls ~/.claude/skills/*/SKILL.md 2>/dev/null

# Project skills (if in a project)
ls .claude/skills/*/SKILL.md 2>/dev/null
```

Read each skill file to understand its purpose and structure.

### Step 3: Match Signals to Skills

For each signal identified:

1. Determine which skill it best applies to based on the skill's description and content
2. If no existing skill fits, suggest creating a new skill
3. Identify which section of the skill it belongs in (or suggest "Learned Preferences" section)

### Step 4: Present Findings

Output format:

```markdown
## Signals Detected

### High Confidence

- [Signal description and source quote]
- [Signal description and source quote]

### Medium Confidence

- [Signal description and context]

### Low Confidence

- [Observation and context]

---

## Proposed Changes

### Skill: [skill-name] ([global/project])

File: [path to skill file]

**Current section:** [section name or "New section: Learned Preferences"]

**Add:**

> [Exact text to add]

**Confidence:** [High/Medium/Low]
**Reason:** [Why this was identified]

---

### NEW SKILL SUGGESTED: [skill-name]

**Purpose:** [What this skill would cover]
**Would add:**

> [Content for the new skill]

**Confidence:** [level]
**Reason:** [Why a new skill is needed]
```

### Step 5: Get Approval

Use `AskUserQuestion` with options:

- **Accept all** - Apply all proposed changes
- **High confidence only** - Apply only high-confidence changes
- **Let me review each** - Step through one at a time
- **Skip** - Cancel without changes

If user wants to modify, accept natural language adjustments:

- "Change the wording on X to..."
- "Skip the one about Y"
- "Combine these two"

### Step 6: Apply Changes

For each approved change:

**Existing skills:**

1. Read the current skill file
2. Find the target section (or create "Learned Preferences" section at the end)
3. Append the new content with a blank line separator
4. Write the updated file

**New skills:**

1. Create directory: `~/.claude/skills/[skill-name]/`
2. Write SKILL.md with frontmatter and content:

```markdown
---
name: [skill-name]
description: [purpose]
---

# [Skill Name]

[Learned content]
```

### Step 7: Commit Changes

For each skill location that is a git repo:

```bash
cd [skill directory]
git add .
git commit -m "reflect: [brief description]

Learned from conversation:
- [signal 1]
- [signal 2]

Confidence: [level]"
```

Report results:

```markdown
## Summary

- **Updated:** [count] skills
- **Created:** [count] new skills
- **Skipped:** [count] (low confidence / user rejected)

### Commits

- `~/.claude/skills`: [commit hash] - [message]
- `.claude/skills`: [commit hash] - [message]
```

## Edge Cases

**No signals found:**

> No learnings identified in this conversation. Try `/reflect` after making corrections or stating preferences.

**Skill file has no clear sections:**
Create a new section at the end:

```markdown
## Learned Preferences

- [new content]
```

**Skills directory not a git repo:**

- Apply changes to files
- Warn: "Note: [path] is not a git repo. Changes were saved but not committed."

**Conflict with existing content:**

- If the skill already contains similar guidance, note it:
  > "Skill already contains guidance about X. Skipping to avoid duplication."

## Example Session

User corrects: "No, always use `AskUserQuestion` with multiple choice options when possible, not open-ended questions."

Later invokes `/reflect`:

```
## Signals Detected

### High Confidence
- Correction: "Always use AskUserQuestion with multiple choice options when possible"
  Source: User explicitly corrected open-ended question approach

## Proposed Changes

### Skill: brainstorming (global via superpowers plugin)
Note: This skill is from a plugin and cannot be modified.
Suggest: Create a local override or new skill for this preference.

### NEW SKILL SUGGESTED: asking-questions
Purpose: Guidelines for how to ask users questions
Would add:
> When using `AskUserQuestion`, prefer multiple choice options over open-ended
> questions when the possible answers are known or can be reasonably enumerated.

Confidence: High
Reason: Explicit correction from user
```
