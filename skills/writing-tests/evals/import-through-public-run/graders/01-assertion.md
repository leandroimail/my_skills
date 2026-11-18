---
type: llm
focus: trace
weight: 1
---

Every test exercises the behavior through `OrderSync.run`; no test calls the private `_normalize` method directly (including through casts or name access)
