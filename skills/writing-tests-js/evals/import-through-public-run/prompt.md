---
tags: [skill-creator]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We have no tests for the order import in order-import.service.ts and it worries me, it writes to the database. Can you write the tests for it? We use Jest with ts-jest.

Input files: order-import.service.ts
