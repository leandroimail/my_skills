# Project-Wide Docs Path

Use this path when the request spans a repository rather than one single
document.

## Read First

- top-level repository structure
- existing `README.md`
- major source directories
- test layout
- existing `docs/` content
- architecture or design notes if they exist

## Preferred Output Shape

For broad work, prefer a hub and split structure:

- `README.md` as a concise entry point
- `docs/technical/` or equivalent for detailed technical reference
- `docs/tutorial/` or equivalent for guided usage
- additional focused files per abstraction or workflow when necessary

## Working Rules

- identify the 5 to 15 most important abstractions or workflows
- split broad documentation by reader need, not by arbitrary length
- move duplicated long-form material out of `README.md`
- link aggressively instead of copying paragraphs

## Validation Points

- the hub structure is navigable
- each document has a clear job
- duplicated content is reduced
- the top-level README stays concise
