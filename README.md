# agent-skills

Personal [Claude Code](https://claude.com/claude-code) skills, published as a plugin marketplace.

## Install

```bash
/plugin marketplace add lritter/agent-skills
/plugin install plan-my-day@lritter-agent-skills
```

Install only what you want — each plugin is independent.

## Plugins

| Plugin | What it does |
| --- | --- |
| `handoff` | Write a handoff document capturing session state, then apply it — return the contents, dispatch a subagent, or start a fresh session. Two skills that pair: `create-handoff` writes, `perform-handoff` executes. |
| `plan-my-day` | Morning planning routine. Reads calendar, PRs, tickets, email, and Apple Reminders, checks standing priorities against the week so far, and produces one clear agenda for today. Ships a second skill, `gym-schedule`, for looking up class times at a Virtuagym-hosted gym. |
| `reflect` | Analyze the conversation for learnings and update the relevant skills. |

## Layout

```
.claude-plugin/marketplace.json    the marketplace manifest
plugins/<name>/
├── .claude-plugin/plugin.json     the plugin manifest
└── skills/<skill-name>/SKILL.md   one directory per skill
```

A plugin can hold more than one skill — `handoff` holds two.

## Configuration and personal data

Skills here contain **no account-specific values**. Anything tied to a particular
calendar, workspace, or tracker lives in a local config file outside this repo,
and the skill reads it at runtime.

`plan-my-day` is the one with real setup: copy
`plugins/plan-my-day/skills/plan-my-day/reference/config.template.md` to
`~/.local/ai/agenda/config.md` and fill it in. It also needs
[`reminders-cli`](https://github.com/keith/reminders-cli) for Apple Reminders
(`brew install keith/formulae/reminders-cli`) — AppleScript works but is roughly
60x slower.

`gym-schedule` needs no setup to use directly — pass `--site` and `--club` on the
command line. Adding a **Schedule sources** block to `config.md` is what lets
`plan-my-day` anchor exercise blocks to real class times.

If you add a skill here, keep that boundary: ids, emails, calendar addresses, and
family details go in config, not in the SKILL.md.

## License

MIT
