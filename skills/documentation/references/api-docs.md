# API Docs Path

Use this path when documenting HTTP, RPC, SDK, or service interfaces.

## Read First

- route definitions and handlers
- request and response schemas
- auth or permission logic
- integration or contract tests
- existing API specs such as OpenAPI if present

## Required Coverage

- endpoint or method purpose
- authentication and authorization
- inputs and parameters
- request and response schemas
- errors and status codes
- pagination, idempotency, and rate limits when relevant
- concrete request and response examples

## Validation Points

- paths, methods, and operation names exist
- examples match real schema fields
- error codes are supported by implementation or tests
- auth requirements are not guessed
- omitted behavior is intentional, not overlooked
