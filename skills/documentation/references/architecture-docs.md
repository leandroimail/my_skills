# Architecture Docs Path

Use this path when documenting system structure, boundaries, components, data
flow, integration points, or major technical decisions.

## Read First

- repository structure
- entrypoints and orchestration code
- domain modules and interfaces
- existing diagrams or architecture notes

## Recommended Sections

- context and goals
- system boundaries
- major components and responsibilities
- data flow or request flow
- integration points
- constraints and trade-offs
- key decisions

## Diagram Rules

- create diagrams only from verified relationships
- keep diagrams simple and aligned to the written explanation
- prefer omission over invented arrows

## Validation Points

- component boundaries match the codebase
- diagrams do not imply behavior the code does not support
- abstractions and names match real modules or services
