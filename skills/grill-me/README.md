# grill-me

An interview and ideation skill for AI coding assistants that support the [open agent skills](https://github.com/vercel-labs/skills) format.

`/grill-me` expands your understanding of what you want. It reads the existing documentation and code first, then asks only what those sources cannot answer. It works in two modes: a relentless interview about a plan or decision, and a brainstorm that generates and filters directions for an open problem.

## Usage

```
/grill-me <plan, decision, or problem>
```

Or by phrase: "grill me on…", "interview me about…", "pressure-test this…", "help me think through…", "brainstorm…", "me entreviste…".

## What it does

- **Reads before it asks.** Code, README, docs, ADRs, glossary, earlier `.grill/` logs. What a source answers is stated with the source, not asked. Before each new question it checks the sources for that specific gap.
- **Separates facts from decisions.** Facts are the agent's job. Intent, risk, assumptions, and hard-to-reverse choices are always put to you. Reversible choices with an obvious default are stated out loud as the agent's call, so you can reject them.
- **Interview mode.** Models the problem as a design tree and asks the whole frontier in numbered rounds, each decision with a recommended answer. Drills into vague answers before moving on.
- **Ideation mode.** Establishes the why, generates a wide unfiltered list, filters it against your constraints, and presents the surviving directions with trade-offs and a recommendation. Switches to interview mode once you pick one.
- **Offers a throwaway prototype** when a doubt can be judged only by seeing or exercising something. It builds one only with your consent.
- **Runs one final check** before closing: a reader with no access to the conversation reports what a builder would still have to guess.
- **Writes a log** to `<cwd>/.grill/<slug>.md` from the first decision and updates it every round. It never commits.
- **Stops when you say so.** "Enough, just do it" ends the questions.

See [SKILL.md](SKILL.md) for the full instructions.

## Files

```
grill-me/
  SKILL.md
  references/
    lenses.md       question lenses
    log-format.md   log template and rules
```

## Install

Copy the whole `grill-me/` folder, including `references/`.

| Agent | Location |
|---|---|
| Claude Code (global) | `~/.claude/skills/grill-me/` |
| Claude Code (project) | `<project>/.claude/skills/grill-me/` |
| Cursor | `<project>/.cursor/skills/grill-me/` |
| Codex | `<project>/.codex/skills/grill-me/` |

## Origin

This version started from `satya-janghu/agent-skills/skills/grill-me` and no longer matches it. Installing from that repository gives you the older skill, not this one.

It combines ideas from Matt Pocock's `grilling`, `domain-modeling`, and `prototype` skills (<https://github.com/mattpocock/skills>) and from `brainstorming` in <https://github.com/obra/superpowers>.
