# my_skills

My development skills for AI coding agents. Every skill follows the
[Agent Skills specification](https://agentskills.io) and installs with the
[`skills` CLI](https://github.com/vercel-labs/skills) (`npx skills`).

## Install

```bash
# List the skills in this repository (installs nothing)
npx skills add leandroimail/my_skills --list

# Install one or more skills globally for Claude Code
npx skills add leandroimail/my_skills -g -a claude-code --skill caveman --skill grill-me

# Install every skill globally for Claude Code
npx skills add leandroimail/my_skills -g -a claude-code --skill '*'
```

Without `-g`, skills install into the current project. Without `-a`, the CLI
asks which agents to install for. Set `DISABLE_TELEMETRY=1` to turn off the
CLI's anonymous telemetry.

## Skills

| Skill | Purpose |
|---|---|
| `code-review` | PR-level review for Python, SQL and data pipelines |
| `code-review-js` | PR-level review for TypeScript/JavaScript, React, NestJS |
| `receiving-code-review` | Inline self-review after each change (Python) |
| `receiving-code-review-js` | Inline self-review after each change (TS/JS) |
| `writing-tests` | pytest suites, fixtures, mocks, mutmut |
| `writing-tests-js` | Jest/Vitest suites, MSW, Testing Library, StrykerJS |
| `programming-guidelines` | Guardrails against common LLM coding mistakes |
| `generating-commit-messages` | Conventional Commits messages |
| `creating-pull-requests` | Stacked, reviewable PR workflow |
| `task-planning-execution` | Spec-driven planning with a durable `.plan/` |
| `frontend-design` | Intentional visual design for UI work |
| `jupyter-notebook` | Notebook scaffolding and editing |
| `playwright-cli` | Browser automation and Playwright tests from the terminal |
| `graphify` | Knowledge graph of a codebase or corpus |
| `escrita` | Routes writing requests to the right writing skill |
| `escrita-tecnica-controlada` | Unambiguous technical text in pt-BR and English |
| `humanizer` | Removes AI tells from prose |
| `documentation` | Diataxis-aware technical documentation |
| `caveman` | Ultra-compressed response mode |
| `creating-skills` | Creates and validates Agent Skills |
| `multi-ide-artifacts` | Converts AI artifacts across IDEs |
| `grill-me` | Interviews the user to pressure-test an idea or decision |

## Third-party skills

`humanizer` (MIT), `frontend-design` (Apache-2.0) and `jupyter-notebook`
(Apache-2.0) started from upstream projects; their license files stay inside
each skill folder. `graphify`, `caveman` and `playwright-cli` also started from
upstream projects.
