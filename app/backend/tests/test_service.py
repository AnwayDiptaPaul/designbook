import unittest
from backend.engineering.service import run_snapshot_analysis


class SnapshotServiceTests(unittest.TestCase):
    def _snapshot(self):
        return {
            "nodes": [{"id": 1, "x": 0, "y": 0, "fix_x": True, "fix_y": True, "fix_rotation": True}, {"id": 2, "x": 3, "y": 0}],
            "elements": [{"id": 1, "start": 1, "end": 2, "area": 0.01, "elastic_modulus": 200000, "moment_of_inertia": 0.002}],
            "loads_by_combination": {"U1": {"2": [0, -10, 0]}},
            "capacities": {"1": {"axial": 1000, "moment": 100, "standard": "BNBC", "edition": "2020", "reference": "review-required"}},
        }

    def test_snapshot_service_returns_audited_report(self) -> None:
        report = run_snapshot_analysis(self._snapshot(), {"standard": "BNBC", "edition": "2020"})
        self.assertEqual(report.overall_status, "pass")
        self.assertEqual(report.members[0].governing_combination, "U1")
        self.assertTrue(report.audit["input_hash"])
        self.assertIn("capacity providers", report.warnings[0])

    def test_malformed_snapshot_is_rejected(self) -> None:
        snapshot = self._snapshot()
        del snapshot["capacities"]
        with self.assertRaises(ValueError):
            run_snapshot_analysis(snapshot, {})


if __name__ == "__main__":
    unittest.main()