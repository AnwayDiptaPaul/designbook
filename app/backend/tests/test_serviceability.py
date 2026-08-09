import unittest
from backend.engineering.design.serviceability import check_deflection, check_governing_deflection, check_governing_story_drift, check_story_drift


class ServiceabilityTests(unittest.TestCase):
    def test_deflection_limit(self) -> None:
        result = check_deflection(0.01, 5.0, 360.0)
        self.assertAlmostEqual(result.limit, 5.0 / 360.0)
        self.assertEqual(result.status, "pass")
        self.assertAlmostEqual(result.utilization, 0.72)

    def test_drift_limit_and_failure(self) -> None:
        result = check_story_drift(0.025, 3.0, 0.007)
        self.assertEqual(result.status, "fail")
        self.assertGreater(result.utilization, 1.0)
        self.assertEqual(result.reference, "prototype-serviceability")

    def test_governing_service_combination_is_retained(self) -> None:
        result = check_governing_deflection({"S2": 0.02, "S1": 0.01}, 5.0, 360.0)
        self.assertEqual(result.combination, "S2")
        self.assertAlmostEqual(result.check.demand, 0.02)
        drift = check_governing_story_drift({"S2": 0.01, "S1": 0.01}, 3.0, 0.01)
        self.assertEqual(drift.combination, "S1")
    def test_invalid_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_deflection(0.01, 0.0, 360.0)
        with self.assertRaises(ValueError):
            check_story_drift(0.01, 3.0, -0.007)
        with self.assertRaises(ValueError):
            check_deflection(0.01, 5.0, 360.0, reference="")


if __name__ == "__main__":
    unittest.main()