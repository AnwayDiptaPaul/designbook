"""Governing-combination benchmark tests."""

from __future__ import annotations

import unittest

from backend.engineering.codes.registry import get_default_registry
from backend.engineering.loads.envelopes import evaluate_envelope


class EnvelopeTests(unittest.TestCase):
    def test_member_moment_envelope_retains_governing_combinations(self) -> None:
        release = get_default_registry().get("BNBC", "2020")
        result = evaluate_envelope(
            release.combinations_for("strength"),
            {"Mu": {"D": 100.0, "L": 50.0, "R": 20.0, "W": -80.0, "E": 30.0}},
        )["Mu"]
        self.assertEqual(result.maximum_combination, "U2")
        self.assertEqual(result.minimum_combination, "U5")
        self.assertAlmostEqual(result.maximum, 210.0)
        self.assertAlmostEqual(result.minimum, 10.0)

    def test_empty_inputs_are_rejected(self) -> None:
        release = get_default_registry().get("BNBC", "2020")
        with self.assertRaises(ValueError):
            evaluate_envelope((), {})
        with self.assertRaises(ValueError):
            evaluate_envelope(release.combinations, {})


if __name__ == "__main__":
    unittest.main()