# Optional Quality Gates — CRAP and Structural Duplication (TypeScript/JavaScript)

Advisory diagnostics from [crapper](https://github.com/unclebob/crapper) and
[dryer](https://github.com/unclebob/dryer). Use them to find **candidates** for
review. A score is never a finding by itself.

## Table of Contents

- [When to use](#when-to-use)
- [Installing the tools](#installing-the-tools)
- [Scope rules](#scope-rules)
- [CRAP](#crap)
- [Duplication](#duplication)
- [Severity mapping](#severity-mapping)
- [Environment caveats](#environment-caveats)
- [Fallback without the tools](#fallback-without-the-tools)

---

## When to use

- The change adds or edits functions with branching logic, or adds code that looks like existing code.
- Check each tool on its own: `python -m pip show crapper`, `python -m pip show dryer` (the interpreter that runs `python -m crapper`). A missing tool skips only that tool; use manual review or a labeled estimate for it (see [Fallback](#fallback-without-the-tools)).
- Never block a review on these tools. Missing or failing tools are **not** a Stage 2 Blocker.
- Install: see [Installing the tools](#installing-the-tools). On 2026-11-17 `pip index versions` found no PyPI distribution named `crapper` or `dryer`; versions seen: 0.1.0.

## Installing the tools

Run the script from this skill's `scripts/` folder. It needs `git` and Python 3.11+, clones into `~/.claude/tools/ub-mode`, pins the tested commits (crapper `c757ec7`, dryer `66ff6d2`), and runs `pip install -e`. Do not move that folder afterwards. Pass `--latest` / `-Latest` to skip the pinning.

| OS | Command |
|----|---------|
| Linux, macOS | `bash scripts/install-quality-tools.sh` |
| Windows | `powershell -File scripts/install-quality-tools.ps1` |

Mutation testing does not need these scripts: the mutation gate here uses StrykerJS (see the mutation section of SKILL.md). `--with-mutator` / `-WithMutator` also installs unclebob's mutator, which is optional and used by no step in these skills.

## Scope rules

`--changed` reads `git status` (working tree), **not** the PR diff. In a clean
checkout with committed changes it prints "No source files to analyze." and
exits 0. That is not a good score; it means nothing was measured.

```bash
# Files changed by the PR (replace BASE with the merge base)
git diff --name-only BASE...HEAD -- '*.ts' '*.tsx' '*.mts' '*.cts' '*.js' '*.jsx' '*.mjs' '*.cjs'
```

- **crapper** reads `.ts .tsx .js .jsx .mjs .cjs` and scores every function in the files you pass. Keep the functions the PR touched, plus any untouched function you can show is the cause of a finding.
- **dryer** compares only the files you pass against each other. Pass the changed files **plus** the modules likely to hold similar code (search for a distinctive identifier or call from the new code), then keep pairs where at least one side is in the diff.
- **dryer reads only `.ts`, `.tsx`, `.mts` and `.cts`.** It silently ignores `.js`, `.jsx`, `.mjs` and `.cjs`. For plain JavaScript report "duplication: metric unavailable"; never read an empty result as "no duplication".
- dryer skips forms under 4 lines or 20 syntax nodes. If a short function is the suspect, lower `--min-lines` and `--min-nodes`.

## CRAP

`CRAP = CC² × (1 − coverage)³ + CC` (coverage is a fraction, 0–1).

| Score | Reading |
|-------|---------|
| ≤ 5 | Low risk |
| > 5 to 30 | Worth a look |
| > 30 | Investigate first |

A high score means high complexity, low coverage, or both. Read the CC and
coverage columns to see which: CC 31 with 100% coverage still scores 31.
Reduce it by splitting the function, by testing it, or both.

ub-mode prefers `< 10`. Treat that as a team preference, not a gate: a function
with CC = 10 and 100% coverage scores exactly 10 and already meets the
`complexity ≤ 10` rule in this skill.

`--threshold N` makes crapper exit 2 when the worst score is above N. Do not
use it as a merge gate here; read the table.

```bash
# 1. LCOV from the project's own runner (default output: coverage/lcov.info)
npx vitest run --coverage --coverage.reporter=lcov   # Jest: npx jest --coverage --coverageReporters=lcov
# 2. CRAP from that report
python -m crapper --use-existing-coverage src/services/pricing.ts
```

When the report has branch records (`BRDA`) for a function, crapper scores by
branch coverage; otherwise it uses line hits. Say which applied.

crapper counts `&&`, `??`, `?.` and JSX `&&` as decisions, so its CC can
differ from ESLint's `complexity` rule. An inline Express route callback is
scored as its own entry (for example `GET /users`).

## Duplication

```bash
python -m dryer --threshold 0.82 src/services src/shared
```

Score is the Jaccard similarity of structural fingerprints (1.0 = same shape).
0.82 is dryer's own default; the ub-mode text says 0.8. Output is a
**candidate duplicate**. Open both functions and decide: same rule in two
places (extract) or same shape with different meaning (leave). Duplication can
be deliberate when two contracts must evolve independently. Callbacks nested
inside another function are not compared. TypeScript only (see Scope rules).

## Severity mapping

| Situation | Level |
|-----------|-------|
| Score only, not confirmed | 🟢 Suggestion (candidate) |
| Confirmed, and it carries a demonstrable risk in this PR (logic that must stay in sync, new branching with no test) | 🟡 Important |
| Confirmed similarity or complexity with no demonstrated risk | 🟢 Suggestion |
| Confirmed security, data loss, or broken behavior found while investigating | 🔴 Critical (by that finding, not by the score) |

## Environment caveats

- **Unreliable coverage makes CRAP unreliable, in either direction.** Missing or mismatched coverage scores a function as 0% and inflates CRAP. A stale report or one from another revision can look good and deflate it; crapper does not check the revision. Accept a CRAP number only when the coverage run succeeded, came from this revision after the last code change, and its paths match. Otherwise report **"CRAP: metric unavailable"** and conclude nothing about quality.
- A coverage failure does **not** affect dryer. Duplication needs only a valid corpus and parsing.
- `--use-existing-coverage` only reads files on disk. crapper searches `coverage/` and `target/coverage/` and merges every LCOV it finds, and repeated entries overwrite each other. Remove stale reports that you created before the run.
- Without `--use-existing-coverage`, crapper runs coverage itself: it deletes `target/coverage/typescript/` and may install `@vitest/coverage-v8` into `node_modules` (without editing `package.json`). Pass `--use-existing-coverage` to avoid that.
- On Windows, `python -m crapper --help` can crash with `UnicodeEncodeError` (cp1252 console); set `PYTHONUTF8=1`. Redirected analysis output worked in testing.
- On Windows, run `python -m crapper`; the wrapper script is POSIX shell.
- The first run downloads tree-sitter grammars from GitHub releases. Report the tools unavailable only if loading a grammar actually fails; a blocked network with grammars already cached still works.
- Both tools write `.metrics/` in the project root, and the coverage runner writes `coverage/`. Never delete pre-existing `.metrics/` or coverage directories (they can hold earlier history). Remove only files this run created, and tell the user if they are not git-ignored.
- Without `--threshold`, crapper exits 0 even for bad scores. Read the table.
- **Not validated on JS/TS in this environment** (only Python was run). Treat output as unverified until you spot-check one function by hand.

## Fallback without the tools

You may estimate CRAP with ESLint `complexity` (cyclomatic) plus per-function
coverage from the LCOV report. Label the result **"estimate"** and name the
complexity rule, the coverage unit (line or branch), and the scope. Do not use
`sonarjs/cognitive-complexity` as the CC in the formula; report it separately.
Do not compare an estimate with crapper output as if it were the same metric.
For duplication, read the changed code against its neighbors and say it was a
manual check.
