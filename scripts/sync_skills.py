"""Install pinned skills into a consumer repository with drift protection."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCK_NAME = ".agent-skills-lock.json"


def content_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
        relative = file_path.relative_to(path).as_posix().encode()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        content = file_path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def git_value(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def load_lock(target: Path) -> dict[str, object]:
    lock_path = target / LOCK_NAME
    if not lock_path.exists():
        return {}
    return json.loads(lock_path.read_text(encoding="utf-8"))


def verify_existing_install(
    target: Path, lock: dict[str, object], repair_drift: bool
) -> None:
    locked_skills = lock.get("skills", {})
    if not isinstance(locked_skills, dict):
        raise ValueError("lock file skills value must be an object")

    for name, value in locked_skills.items():
        if not isinstance(value, dict):
            raise ValueError(f"lock entry for {name} must be an object")
        destination = target / str(value.get("path", ""))
        expected = value.get("contentSha256")
        if destination.is_dir() and expected and content_hash(destination) != expected:
            if not repair_drift:
                raise ValueError(
                    f"local drift detected for {name}; use --repair-drift to replace it"
                )


def synchronize(args: argparse.Namespace) -> None:
    source = args.source.resolve()
    target = args.target.resolve()
    lock = load_lock(target)
    verify_existing_install(target, lock, args.repair_drift)

    head_sha = git_value(source, "rev-parse", "HEAD")
    commit_sha = args.commit_sha or head_sha
    if not re.fullmatch(r"[0-9a-f]{40}", commit_sha):
        raise ValueError("commit SHA must be 40 lowercase hexadecimal characters")
    if commit_sha != head_sha:
        raise ValueError("commit SHA does not match the checked-out source")

    locked_skills = lock.get("skills", {})
    if isinstance(locked_skills, dict):
        for old_name, old_value in locked_skills.items():
            if old_name in args.skills or not isinstance(old_value, dict):
                continue
            old_destination = target / str(old_value.get("path", ""))
            if old_destination.is_dir():
                shutil.rmtree(old_destination)

    lock_skills: dict[str, dict[str, str]] = {}
    for name in args.skills:
        if not NAME_PATTERN.fullmatch(name):
            raise ValueError(f"invalid skill name: {name}")
        source_dir = source / "skills" / name
        if not (source_dir / "SKILL.md").is_file():
            raise ValueError(f"skill does not exist: {name}")

        tree_sha = git_value(source, "rev-parse", f"{commit_sha}:skills/{name}")
        destination = target / ".github" / "skills" / name
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_dir, destination)
        lock_skills[name] = {
            "treeSha": tree_sha,
            "contentSha256": content_hash(destination),
            "path": destination.relative_to(target).as_posix(),
        }

    lock_data = {
        "source": args.source_repository,
        "ref": args.source_ref,
        "commitSha": commit_sha,
        "skills": lock_skills,
    }
    (target / LOCK_NAME).write_text(
        json.dumps(lock_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--source-repository", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--commit-sha")
    parser.add_argument("--skills", nargs="+", required=True)
    parser.add_argument("--repair-drift", action="store_true")
    args = parser.parse_args()

    try:
        synchronize(args)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"sync failed: {error}", file=sys.stderr)
        return 1

    print("Skill synchronization completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
