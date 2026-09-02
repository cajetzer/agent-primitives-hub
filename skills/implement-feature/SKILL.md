---
name: implement-feature
description: Implement a bounded, approved software change with focused tests and validation. Use after requirements or a design identify the intended behavior and repository constraints.
---

# Implement feature

1. Read the approved requirements and repository instructions.
2. Inspect existing patterns and reuse them instead of introducing parallel
   abstractions.
3. Make the smallest coherent change that fully satisfies the behavior.
4. Add or update deterministic tests for success, boundary, and failure cases.
5. Run the smallest relevant validation first, then the repository-required
   checks.
6. Report changed behavior, validation results, and any remaining limitation.

Preserve unrelated changes. Do not suppress errors, weaken tests, commit
credentials, merge pull requests, or deploy software.
