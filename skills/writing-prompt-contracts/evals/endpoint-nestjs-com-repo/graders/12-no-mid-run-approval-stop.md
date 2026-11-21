---
type: llm
focus: trace
weight: 1
---

The contract never makes the executing agent stop mid-run to wait for the user's approval (the user said they could not answer): non-blocking open items carry a default that the agent uses and reports, and any blocking item has a defined stopping point with a 'not done' report.
