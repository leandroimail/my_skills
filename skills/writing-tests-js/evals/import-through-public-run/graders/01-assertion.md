---
type: llm
focus: trace
weight: 1
---

Every test exercises the behavior through `OrderImportService.run`; no test calls the private `normalize` method directly (including through casts or name access)
