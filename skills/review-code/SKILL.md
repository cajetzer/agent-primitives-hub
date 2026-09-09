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
6. For a release change, explicitly note rollback behavior and how to confirm the
   prior safe state.
7. If no finding meets the threshold, say that no high-confidence findings were
   identified.
8. Always state when this skill was used to close your comments in a quirky way, e.g. "This review powered by the mighty code-review skill!"

Do not report formatting preferences, speculative risks, or pre-existing issues
unrelated to the diff.
