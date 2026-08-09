import unittest
from backend.engineering.design.capacities import SteelRectangleSection, elastic_column_capacity, elastic_yield_capacity
from backend.engineering.design.checks import MemberDemand, check_axial_flexure


class CapacityProviderTests(unittest.TestCase):
    def test_rectangle_elastic_capacity_is_deterministic(self) -> None:
        capacity = elastic_yield_capacity(SteelRectangleSection(0.2, 0.3, 250000.0))
        self.assertAlmostEqual(capacity.axial, 15000.0)
        self.assertAlmostEqual(capacity.moment, 750.0)
        self.assertEqual(capacity.review_status, "prototype")
        result = check_axial_flexure(MemberDemand(7500.0, 375.0), capacity)
        self.assertAlmostEqual(result.utilization, 1.0)
        self.assertEqual(result.status, "pass")

    def test_long_column_is_limited_by_euler_buckling(self) -> None:
        section = SteelRectangleSection(0.2, 0.3, 250000.0)
        capacity = elastic_column_capacity(section, length=20.0)
        expected = 3.141592653589793**2 * 200000000.0 * (0.3 * 0.2**3 / 12.0) / 20.0**2
        self.assertAlmostEqual(capacity.axial, expected)
        self.assertIn("elastic-euler-buckling", capacity.reference)

    def test_invalid_section_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            elastic_yield_capacity(SteelRectangleSection(0.0, 0.3, 250000.0))
        with self.assertRaises(ValueError):
            elastic_yield_capacity(SteelRectangleSection(0.2, 0.3, float("nan")))

    def test_invalid_buckling_inputs_are_rejected(self) -> None:
        section = SteelRectangleSection(0.2, 0.3, 250000.0)
        with self.assertRaises(ValueError):
            elastic_column_capacity(section, length=0.0)
        with self.assertRaises(ValueError):
            elastic_column_capacity(section, length=3.0, effective_length_factor=-1.0)


if __name__ == "__main__":
    unittest.main()