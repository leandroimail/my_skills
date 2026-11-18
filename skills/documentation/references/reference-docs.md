# Reference Docs Path

Use this path when documenting commands, parameters, fields, schemas,
interfaces, configuration options, or return values.

## Read First

- source definitions in code
- config schemas and defaults
- CLI help output
- tests that define accepted behavior

## Writing Rules

- optimize for exactness and scanability
- document names, types, defaults, allowed values, errors, and constraints
- prefer tables or short repeated patterns when helpful
- avoid tutorial-style storytelling

## Recommended Sections

- item name
- purpose
- signature, fields, or flags
- defaults and constraints
- examples
- related errors or edge cases

## Validation Points

- every field, flag, or parameter exists
- defaults match the implementation
- allowed values come from real code or schema
- examples use valid names and shapes
