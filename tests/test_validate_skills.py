from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_skills import validate_collection


class ValidateSkillsTests(unittest.TestCase):
    def test_accepts_valid_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "sample-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: sample-skill\n"
                "description: A useful sample.\n"
                "---\n\n"
                "Follow the documented process.\n",
                encoding="utf-8",
            )

            self.assertEqual([], validate_collection(root))

    def test_rejects_directory_name_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "sample-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: different-name\n"
                "description: A useful sample.\n"
                "---\n",
                encoding="utf-8",
            )

            errors = validate_collection(root)
            self.assertTrue(any("does not match directory" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
