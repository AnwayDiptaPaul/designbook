import unittest
from backend.engineering.response_spectrum import evaluate_spectrum, modal_participation


class ResponseSpectrumTests(unittest.TestCase):
    def test_participation_and_effective_mass(self) -> None:
        result = modal_participation((2.0, 1.0), ((1.0, 0.0), (0.0, 1.0)), (1.0, 1.0))
        self.assertEqual(result.factors, (2.0, 1.0))
        self.assertEqual(result.effective_masses, (4.0, 1.0))
        self.assertEqual(result.cumulative_effective_mass, 5.0)

    def test_spectrum_interpolates_and_clamps_endpoints(self) -> None:
        points = ((0.0, 1.0), (1.0, 3.0), (2.0, 2.0))
        self.assertEqual(evaluate_spectrum(0.0, points), 1.0)
        self.assertEqual(evaluate_spectrum(0.5, points), 2.0)
        self.assertEqual(evaluate_spectrum(5.0, points), 2.0)

    def test_invalid_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            modal_participation((1.0,), ((1.0, 2.0),), (1.0,))
        with self.assertRaises(ValueError):
            evaluate_spectrum(1.0, ((0.0, 1.0), (0.0, 2.0)))
        with self.assertRaises(ValueError):
            evaluate_spectrum(-1.0, ((0.0, 1.0),))


if __name__ == "__main__":
    unittest.main()