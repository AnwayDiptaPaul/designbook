import unittest
from backend.engineering.design.checks import MemberCapacity, MemberDemand, check_axial_flexure, check_governing_axial_flexure


class DesignCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.capacity = MemberCapacity(100.0, 200.0, "BNBC", "2020", "prototype-section-capacity")

    def test_utilization_and_pass_status(self) -> None:
        result = check_axial_flexure(MemberDemand(40.0, 80.0), self.capacity)
        self.assertAlmostEqual(result.utilization, 0.8)
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.capacity.review_status, "prototype")

    def test_failure_at_or_above_limit(self) -> None:
        result = check_axial_flexure(MemberDemand(100.0, 2.0), self.capacity)
        self.assertEqual(result.status, "fail")
        self.assertGreater(result.utilization, 1.0)

    def test_invalid_capacity_and_missing_provenance_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_axial_flexure(MemberDemand(1.0, 1.0), MemberCapacity(0.0, 1.0, "BNBC", "2020", "ref"))
        with self.assertRaises(ValueError):
            check_axial_flexure(MemberDemand(1.0, 1.0), MemberCapacity(1.0, 1.0, "", "2020", "ref"))

    def test_governing_combination_is_retained(self) -> None:
        result = check_governing_axial_flexure(
            {"U2": MemberDemand(40.0, 100.0), "U1": MemberDemand(80.0, 0.0)},
            self.capacity,
        )
        self.assertEqual(result.combination, "U2")
        self.assertAlmostEqual(result.check.utilization, 0.9)
        self.assertEqual(set(result.checks), {"U1", "U2"})

    def test_equal_utilization_uses_stable_name_tie_break(self) -> None:
        result = check_governing_axial_flexure(
            {"U2": MemberDemand(50.0, 0.0), "U1": MemberDemand(50.0, 0.0)},
            self.capacity,
        )
        self.assertEqual(result.combination, "U1")
    def test_non_finite_demand_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_axial_flexure(MemberDemand(float("nan"), 1.0), self.capacity)


if __name__ == "__main__":
    unittest.main()