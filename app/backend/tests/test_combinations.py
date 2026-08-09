"""Benchmark-style tests for the deterministic combination boundary."""

from __future__ import annotations

import unittest

from backend.engineering.codes.registry import get_default_registry
from backend.engineering.loads.combinations import combination_value, generate_combinations


class CombinationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.release = get_default_registry().get("BNBC", "2020")

    def test_registry_exposes_strength_and_serviceability_sets(self) -> None:
        self.assertEqual(len(generate_combinations(self.release, "strength")), 7)
        self.assertEqual(len(generate_combinations(self.release, "serviceability")), 4)

    def test_standard_strength_combination_is_evaluated(self) -> None:
        u2 = next(item for item in self.release.combinations if item.name == "U2")
        self.assertAlmostEqual(combination_value(u2, {"D": 100.0, "L": 50.0, "R": 20.0}), 210.0)

    def test_missing_case_is_not_silently_treated_as_zero(self) -> None:
        u4 = next(item for item in self.release.combinations if item.name == "U4")
        with self.assertRaises(KeyError):
            combination_value(u4, {"D": 100.0, "L": 50.0})

    def test_available_case_filter_is_explicit(self) -> None:
        selected = generate_combinations(self.release, available_cases=["D", "L"])
        self.assertEqual([item.name for item in selected], ["U1", "S1", "S2"])


if __name__ == "__main__":
    unittest.main()
