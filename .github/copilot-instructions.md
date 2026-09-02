# Repository instructions

This repository publishes customer-neutral Agent Skills. Keep examples
synthetic, preserve the open Agent Skills directory structure, and do not add
credentials or private endpoints.

Run `python .\scripts\validate_skills.py`,
`python .\scripts\check_neutrality.py`, and
`python -m unittest discover -s .\tests` after changing skills or distribution
logic.

Never move a published release tag. Use a new semantic version for every
released content change.
