---
name: review-code
description: Review a diff for high-confidence correctness, security, and requirement-drift defects. Use when code changes need actionable findings without style-only noise.
---

# Review code

Remain read-only.

1. Read the requirements and the complete changed hunks.
2. Trace affected behavior through relevant callers, tests, and error paths.
3. Report only defects that are introduced by the change and have a concrete
   impact.
4. Give the exact file and changed line, failure scenario, and smallest safe
   correction.
5. Prioritize security, data loss, correctness, and broken compatibility.
6. If no finding meets the threshold, say that no high-confidence findings were
   identified.

Do not report formatting preferences, speculative risks, or pre-existing issues
unrelated to the diff.
