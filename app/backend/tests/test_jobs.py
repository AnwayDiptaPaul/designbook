import unittest
from backend.engineering.execution import AnalysisState
from backend.engineering.jobs import AnalysisJobCommand, InMemoryJobIndex


class JobContractTests(unittest.TestCase):
    def _command(self, *, config=None, key="request-1"):
        return AnalysisJobCommand.create(project_id="project-1", revision_id="revision-1", analysis_type="linear_elastic", config=config or {"case": "strength"}, idempotency_key=key)

    def test_duplicate_submission_is_idempotent(self) -> None:
        index = InMemoryJobIndex()
        first, created = index.submit(self._command())
        second, created_again = index.submit(self._command())
        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertIs(first, second)

    def test_key_reuse_with_different_payload_is_rejected(self) -> None:
        index = InMemoryJobIndex()
        index.submit(self._command())
        with self.assertRaises(ValueError):
            index.submit(self._command(config={"case": "serviceability"}))

    def test_failure_requires_error_and_terminal_state_is_stable(self) -> None:
        record, _ = InMemoryJobIndex().submit(self._command())
        record.transition(AnalysisState.RUNNING)
        with self.assertRaises(ValueError):
            record.transition(AnalysisState.FAILED)
        record.transition(AnalysisState.FAILED, error="solver unavailable")
        with self.assertRaises(ValueError):
            record.transition(AnalysisState.RUNNING)


if __name__ == "__main__":
    unittest.main()