"""Reject configured sensitive terms without echoing their values."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}


def tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [root / line for line in result.stdout.splitlines() if line]


def load_terms(args: argparse.Namespace) -> list[str]:
    terms = [term.strip() for term in args.term if term.strip()]
    if args.terms_file:
        terms.extend(
            line.strip()
            for line in args.terms_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    terms.extend(
        term.strip()
        for term in os.environ.get("NEUTRALITY_TERMS", "").split(",")
        if term.strip()
    )
    return list(dict.fromkeys(term.casefold() for term in terms))


def scan(root: Path, terms: list[str]) -> list[tuple[Path, int, int]]:
    matches: list[tuple[Path, int, int]] = []
    for path in tracked_files(root):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            folded = line.casefold()
            for rule_number, term in enumerate(terms, start=1):
                if term in folded:
                    matches.append((path.relative_to(root), line_number, rule_number))
    return matches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--term", action="append", default=[])
    parser.add_argument("--terms-file", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    terms = load_terms(args)
    matches = scan(root, terms)
    if matches:
        for path, line, rule in matches:
            print(f"{path}:{line}: matched neutrality rule {rule}", file=sys.stderr)
        return 1

    print(f"Neutrality scan passed with {len(terms)} configured rules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
