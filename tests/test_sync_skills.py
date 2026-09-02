from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.sync_skills import content_hash, synchronize


class SyncSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.source = self.root / "source"
        self.target = self.root / "target"
        skill = self.source / "skills" / "sample-skill"
        skill.mkdir(parents=True)
        self.target.mkdir()
        (skill / "SKILL.md").write_text(
            "---\n"
            "name: sample-skill\n"
            "description: A useful sample.\n"
            "---\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q", str(self.source)], check=True)
        subprocess.run(["git", "-C", str(self.source), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.source),
                "-c",
                "user.name=Demo",
                "-c",
                "user.email=demo@example.invalid",
                "commit",
                "-qm",
                "Initial skill",
            ],
            check=True,
        )
        self.initial_commit = self.git("rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.source), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def args(
        self,
        repair_drift: bool = False,
        source_ref: str = "v0.1.0",
        commit_sha: str | None = None,
    ) -> argparse.Namespace:
        return argparse.Namespace(
            source=self.source,
            target=self.target,
            source_repository="demo/skills",
            source_ref=source_ref,
            commit_sha=commit_sha,
            skills=["sample-skill"],
            repair_drift=repair_drift,
        )

    def test_writes_skill_and_lock(self) -> None:
        synchronize(self.args())

        destination = self.target / ".github" / "skills" / "sample-skill"
        lock = json.loads(
            (self.target / ".agent-skills-lock.json").read_text(encoding="utf-8")
        )
        self.assertTrue((destination / "SKILL.md").is_file())
        self.assertEqual(
            content_hash(destination),
            lock["skills"]["sample-skill"]["contentSha256"],
        )

    def test_rejects_drift_without_repair_flag(self) -> None:
        synchronize(self.args())
        installed = self.target / ".github" / "skills" / "sample-skill" / "SKILL.md"
        installed.write_text("changed\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "local drift detected"):
            synchronize(self.args())

    def test_same_release_is_a_no_op(self) -> None:
        synchronize(self.args())
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        subprocess.run(["git", "-C", str(self.target), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.target),
                "-c",
                "user.name=Demo",
                "-c",
                "user.email=demo@example.invalid",
                "commit",
                "-qm",
                "Installed skill",
            ],
            check=True,
        )

        synchronize(self.args())

        status = subprocess.run(
            ["git", "-C", str(self.target), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertEqual("", status)

    def test_upgrade_and_rollback(self) -> None:
        synchronize(self.args())
        skill_file = self.source / "skills" / "sample-skill" / "SKILL.md"
        initial_content = skill_file.read_text(encoding="utf-8")
        skill_file.write_text(initial_content + "\nUpdated guidance.\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.source), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.source),
                "-c",
                "user.name=Demo",
                "-c",
                "user.email=demo@example.invalid",
                "commit",
                "-qm",
                "Update skill",
            ],
            check=True,
        )
        updated_commit = self.git("rev-parse", "HEAD")

        synchronize(self.args(source_ref="v0.2.0"))
        upgraded = (
            self.target / ".github" / "skills" / "sample-skill" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Updated guidance.", upgraded)

        self.git("checkout", "-q", self.initial_commit)
        synchronize(self.args(source_ref="v0.1.0"))
        rolled_back = (
            self.target / ".github" / "skills" / "sample-skill" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(initial_content, rolled_back)
        self.git("checkout", "-q", updated_commit)

    def test_rejects_commit_that_is_not_checked_out(self) -> None:
        with self.assertRaisesRegex(
            ValueError, "commit SHA does not match the checked-out source"
        ):
            synchronize(self.args(commit_sha="0" * 40))


if __name__ == "__main__":
    unittest.main()
