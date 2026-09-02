---
name: generate-design
description: Create a reviewable high-level and low-level design for a bounded software change. Use when a feature needs architecture, interfaces, risks, and acceptance criteria before implementation.
---

# Generate design

## Inputs

- The requested outcome and explicit non-goals.
- Relevant repository structure, instructions, and existing architecture.
- Known runtime, security, compatibility, and validation constraints.

If a required decision is missing, identify it as an open question rather than
inventing an answer.

## Process

1. Inspect only the repository areas needed to understand the change.
2. Separate source-backed facts from assumptions.
3. Describe the smallest coherent architecture that satisfies the request.
4. Define interfaces, data flow, error behavior, and security boundaries.
5. Map each requirement to a validation method.
6. Identify risks, alternatives, unresolved decisions, and rollback behavior.

## Output

Use the template in `references/design-template.md`. Keep the HLD focused on
components and interactions. Keep the LLD focused on concrete files, functions,
data shapes, and test cases.

Do not modify production code unless the user separately asks for
implementation.
