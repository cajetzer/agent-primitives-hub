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

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def args(self, repair_drift: bool = False) -> argparse.Namespace:
        return argparse.Namespace(
            source=self.source,
            target=self.target,
            source_repository="demo/skills",
            source_ref="v0.1.0",
            commit_sha=None,
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


if __name__ == "__main__":
    unittest.main()
