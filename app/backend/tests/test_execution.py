import unittest
from backend.engineering.execution import AnalysisState, ExecutionProvenance, can_transition, require_transition


class ExecutionContractTests(unittest.TestCase):
    def test_terminal_states_cannot_restart(self) -> None:
        self.assertTrue(can_transition(AnalysisState.PENDING, AnalysisState.RUNNING))
        self.assertFalse(can_transition(AnalysisState.COMPLETED, AnalysisState.RUNNING))
        with self.assertRaises(ValueError):
            require_transition(AnalysisState.FAILED, AnalysisState.RUNNING)

    def test_provenance_is_complete_and_serializable(self) -> None:
        provenance = ExecutionProvenance.create(
            revision_id="rev-1", snapshot_hash="abc123", code_standard="BNBC",
            code_edition="2020", engine="prototype", engine_version="0.1.0",
        )
        payload = provenance.as_dict()
        self.assertEqual(payload["snapshot_hash"], "abc123")
        self.assertTrue(payload["created_at"])
        with self.assertRaises(ValueError):
            ExecutionProvenance.create(revision_id="", snapshot_hash="x", code_standard="BNBC", code_edition="2020", engine="e", engine_version="v")


if __name__ == "__main__":
    unittest.main()
