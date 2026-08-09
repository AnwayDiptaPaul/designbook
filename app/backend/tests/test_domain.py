"""Dependency-free contract tests for the canonical domain seam."""

from __future__ import annotations

import unittest

from backend.domain import Quantity, canonical_json, convert, ensure_positive, snapshot_hash


class UnitContractTests(unittest.TestCase):
    def test_length_conversion_is_exact_at_boundary(self) -> None:
        self.assertEqual(convert(2500.0, "mm", "m"), 2.5)
        self.assertEqual(Quantity(2.5, "m").to("mm").value, 2500.0)

    def test_invalid_conversion_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            convert(1.0, "m", "MPa")

    def test_positive_inputs_reject_zero_and_non_finite_values(self) -> None:
        self.assertEqual(ensure_positive(3, "span"), 3.0)
        for invalid in (0, -1, float("inf")):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                ensure_positive(invalid, "span")


class SnapshotContractTests(unittest.TestCase):
    def test_key_order_does_not_change_snapshot_hash(self) -> None:
        left = {"loads": {"dead": 3.0, "live": 2.0}, "version": 1}
        right = {"version": 1, "loads": {"live": 2.0, "dead": 3.0}}
        self.assertEqual(snapshot_hash(left), snapshot_hash(right))

    def test_snapshot_changes_when_input_changes(self) -> None:
        self.assertNotEqual(snapshot_hash({"span_m": 5}), snapshot_hash({"span_m": 6}))

    def test_canonical_json_rejects_nan(self) -> None:
        with self.assertRaises(ValueError):
            canonical_json({"value": float("nan")})


if __name__ == "__main__":
    unittest.main()
