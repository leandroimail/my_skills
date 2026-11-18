---
name: jupyter-notebook
description: >
  Creates, scaffolds, and edits Jupyter notebooks (.ipynb) for experiments,
  explorations, or tutorials. Use when the user mentions notebooks, .ipynb files,
  Jupyter, experiments, exploratory analysis, or tutorials — even if they don't
  explicitly ask for this skill. Prefer the bundled templates and the helper script
  new_notebook.py to generate clean starting notebooks.
---

# Jupyter Notebook Skill

Creates clean, reproducible Jupyter notebooks for two primary modes:

- Experiments and exploratory analysis
- Tutorials and teaching-oriented walkthroughs

Prefers the bundled templates and the helper script for consistent structure and fewer JSON mistakes.

## When To Use

- Create a new `.ipynb` notebook from scratch.
- Convert rough notes or scripts into a structured notebook.
- Refactor an existing notebook to be more reproducible and skimmable.
- Build experiments or tutorials that will be read or re-run by other people.

## When Not To Use

- Running or executing notebooks interactively (use JupyterLab directly).
- Managing Jupyter server configuration or kernels.
- Converting notebooks to other formats (use `jupyter nbconvert`).

## Inputs

- Notebook kind (`experiment` or `tutorial`), title, objective, and audience.
- For edits: the existing `.ipynb` file or the notes/scripts to convert.
- Output path (default `output/jupyter-notebook/<name>.ipynb`).

## Decision Tree

- If the request is exploratory, analytical, or hypothesis-driven, choose `experiment`.
- If the request is instructional, step-by-step, or audience-specific, choose `tutorial`.
- If editing an existing notebook, treat it as a refactor: preserve intent and improve structure.

## Method

### 1. Lock the intent

Identify the notebook kind: `experiment` or `tutorial`.
Capture the objective, audience, and what "done" looks like.

### 2. Scaffold from the template

Use the helper script to avoid hand-authoring raw notebook JSON. The script path is relative to this skill directory: `scripts/new_notebook.py`. Run from the skill directory, or prefix the path with it. Use `python` (or `uv run python` if the project uses uv).

```bash
python scripts/new_notebook.py \
  --kind experiment \
  --title "Compare prompt variants" \
  --out output/jupyter-notebook/compare-prompt-variants.ipynb
```

```bash
python scripts/new_notebook.py \
  --kind tutorial \
  --title "Intro to embeddings" \
  --out output/jupyter-notebook/intro-to-embeddings.ipynb
```

### 3. Fill the notebook with small, runnable steps

Keep each code cell focused on one step.
Add short markdown cells that explain the purpose and expected result.
Avoid large, noisy outputs when a short summary works.

### 4. Apply the right pattern

For experiments, follow [experiment-patterns.md](references/experiment-patterns.md).
For tutorials, follow [tutorial-patterns.md](references/tutorial-patterns.md).

### 5. Edit safely when working with existing notebooks

Preserve the notebook structure; avoid reordering cells unless it improves the top-to-bottom story.
Prefer targeted edits over full rewrites.
If you must edit raw JSON, review [notebook-structure.md](references/notebook-structure.md) first.

### 6. Validate the result

Run the notebook top-to-bottom when the environment allows.
If execution is not possible, say so explicitly and call out how to validate locally.
Use the final pass checklist in [quality-checklist.md](references/quality-checklist.md).

## Quality Checklist

Before delivering, confirm (full list in [quality-checklist.md](references/quality-checklist.md)):

- The notebook runs top-to-bottom, or the inability to run it is stated with local validation steps.
- Each code cell does one step, with a short markdown cell explaining purpose and expected result.
- Cell order tells a top-to-bottom story and outputs are small.

## Outputs

A valid `.ipynb` file at the agreed path, plus a short note on the notebook kind, how it was validated, and anything not verified.

## Templates and Helper Script

- Templates: [assets/experiment-template.ipynb](assets/experiment-template.ipynb) and [assets/tutorial-template.ipynb](assets/tutorial-template.ipynb).
- The helper script (`scripts/new_notebook.py`) loads a template, updates the title cell, and writes a notebook. Uses only the Python standard library — no extra dependencies.

## Output Conventions

- Use `tmp/jupyter-notebook/` for intermediate files; delete when done.
- Write final artifacts under `output/jupyter-notebook/` when working in this repo.
- Use stable, descriptive filenames (for example, `ablation-temperature.ipynb`).

## Dependencies

Optional Python packages for local notebook execution:

```bash
pip install jupyterlab ipykernel
# or, with uv: uv pip install jupyterlab ipykernel
```

## Reference Map

- [references/experiment-patterns.md](references/experiment-patterns.md): experiment structure and heuristics.
- [references/tutorial-patterns.md](references/tutorial-patterns.md): tutorial structure and teaching flow.
- [references/notebook-structure.md](references/notebook-structure.md): notebook JSON shape and safe editing rules.
- [references/quality-checklist.md](references/quality-checklist.md): final validation checklist.
