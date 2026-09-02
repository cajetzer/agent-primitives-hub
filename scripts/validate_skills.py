"""Validate the local Agent Skills collection using only the standard library."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening frontmatter delimiter")

    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("missing closing frontmatter delimiter") from error

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return [f"{skill_dir}: missing SKILL.md"]

    try:
        metadata = parse_frontmatter(skill_file)
    except ValueError as error:
        return [f"{skill_file}: {error}"]

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not NAME_PATTERN.fullmatch(name):
        errors.append(f"{skill_file}: invalid skill name {name!r}")
    if name != skill_dir.name:
        errors.append(
            f"{skill_file}: name {name!r} does not match directory {skill_dir.name!r}"
        )
    if not description:
        errors.append(f"{skill_file}: description is required")
    if "allowed-tools" in metadata and metadata["allowed-tools"].startswith("["):
        errors.append(f"{skill_file}: allowed-tools must be a string, not an array")
    return errors


def validate_collection(root: Path) -> list[str]:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return [f"{skills_root}: skills directory does not exist"]

    skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
    if not skill_dirs:
        return [f"{skills_root}: no skills found"]

    errors: list[str] = []
    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Skills repository root",
    )
    args = parser.parse_args()

    errors = validate_collection(args.root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Agent Skills validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
