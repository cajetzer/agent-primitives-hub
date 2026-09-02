# Agent Primitives Hub Demo

A customer-neutral reference repository for authoring, validating, releasing,
and distributing reusable Agent Skills.

## Skills

- `generate-design`: turns a bounded request into an HLD/LLD design.
- `implement-feature`: implements an approved, bounded change with tests.
- `review-code`: reports high-confidence correctness and security findings.

## Validate

```powershell
python .\scripts\validate_skills.py
python .\scripts\check_neutrality.py
python -m unittest discover -s .\tests
gh skill publish --dry-run
```

The `gh skill` command is a preview feature. Preview skill contents before
installing them, and pin approved installations to a release tag or commit SHA.

## Distribution

Use `gh skill install` for explicit personal or project installation. Use the
`sync-skills.yml` workflow to propose pinned project-skill updates to protected
consumer repositories through pull requests.

No workflow merges changes or deploys software.
