import unittest
from enum import Enum

from backend.engineering.analysis_lifecycle import can_transition, require_transition


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisLifecycleTests(unittest.TestCase):
    def test_pending_can_start_or_cancel(self) -> None:
        self.assertTrue(can_transition(AnalysisStatus.PENDING, AnalysisStatus.RUNNING))
        self.assertTrue(can_transition(AnalysisStatus.PENDING, AnalysisStatus.CANCELLED))

    def test_running_has_explicit_terminal_paths(self) -> None:
        for target in (AnalysisStatus.COMPLETED, AnalysisStatus.FAILED, AnalysisStatus.CANCELLED):
            self.assertTrue(can_transition(AnalysisStatus.RUNNING, target))

    def test_terminal_states_cannot_be_overwritten(self) -> None:
        for current in (AnalysisStatus.COMPLETED, AnalysisStatus.FAILED, AnalysisStatus.CANCELLED):
            self.assertFalse(can_transition(current, AnalysisStatus.RUNNING))
            with self.assertRaises(ValueError):
                require_transition(current, AnalysisStatus.RUNNING)


if __name__ == "__main__":
    unittest.main()