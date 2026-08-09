import math
import unittest
from backend.engineering.modal_response import combine_cqc, combine_orthogonal_directions, combine_srss, compute_modal_spectral_response


class ModalResponseTests(unittest.TestCase):
    def test_modal_spectral_response_uses_srss(self) -> None:
        result = compute_modal_spectral_response((0.5, 1.0), (2.0, 1.0), ((0.0, 1.0), (1.0, 3.0)))
        self.assertEqual(result.modal_demands, (4.0, 3.0))
        self.assertAlmostEqual(result.combined_srss, 5.0)

    def test_srss_is_order_independent(self) -> None:
        self.assertAlmostEqual(combine_srss((3.0, 4.0)), combine_srss((4.0, 3.0)))
        self.assertAlmostEqual(combine_srss((-3.0, 4.0)), 5.0)

    def test_cqc_single_mode_matches_absolute_response(self) -> None:
        self.assertAlmostEqual(combine_cqc((10.0,), (-3.0,)), 3.0)

    def test_cqc_is_symmetric_for_mode_order(self) -> None:
        first = combine_cqc((10.0, 12.0), (3.0, 4.0))
        second = combine_cqc((12.0, 10.0), (4.0, 3.0))
        self.assertAlmostEqual(first, second)

    def test_invalid_cqc_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            combine_cqc((10.0,), (1.0, 2.0))
        with self.assertRaises(ValueError):
            combine_cqc((10.0,), (1.0,), damping_ratio=1.0)
    def test_orthogonal_directional_cases_preserve_sign(self) -> None:
        result = combine_orthogonal_directions(10.0, -5.0, secondary_factor=0.3)
        self.assertAlmostEqual(result.x_primary, 8.5)
        self.assertAlmostEqual(result.y_primary, -2.0)

    def test_invalid_directional_factor_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            combine_orthogonal_directions(1.0, 1.0, secondary_factor=1.1)
    def test_invalid_modal_response_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            compute_modal_spectral_response((1.0,), (1.0, 2.0), ((0.0, 1.0),))
        with self.assertRaises(ValueError):
            combine_srss(())
        with self.assertRaises(ValueError):
            combine_srss((math.nan,))


if __name__ == "__main__":
    unittest.main()