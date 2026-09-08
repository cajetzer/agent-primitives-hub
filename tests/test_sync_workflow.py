from __future__ import annotations

import unittest
from pathlib import Path


class SyncWorkflowGuardTests(unittest.TestCase):
    def test_restricts_sync_targets_to_consumer_a(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[1] / ".github" / "workflows" / "sync-skills.yml"
        )
        content = workflow.read_text(encoding="utf-8")

        self.assertIn("repositories: agent-primitives-consumer-a", content)
        self.assertIn("Consumer B is not a supported sync target", content)
        self.assertNotIn(
            "repositories: agent-primitives-consumer-a,agent-primitives-consumer-b",
            content,
        )
        self.assertIn("\n          esac\n", content)
        self.assertNotIn("gh pr merge", content)


if __name__ == "__main__":
    unittest.main()
