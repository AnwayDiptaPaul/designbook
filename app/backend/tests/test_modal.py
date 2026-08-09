import math
import unittest
from backend.engineering.modal import solve_modes


class ModalSolverTests(unittest.TestCase):
    def test_single_degree_of_freedom_period(self) -> None:
        result = solve_modes(((200.0,),), (2.0,))
        self.assertAlmostEqual(result.angular_frequencies[0], 10.0)
        self.assertAlmostEqual(result.periods[0], 2.0 * math.pi / 10.0)
        self.assertAlmostEqual(abs(result.mode_shapes[0][0]), 1.0 / math.sqrt(2.0))

    def test_modes_are_sorted_for_coupled_system(self) -> None:
        result = solve_modes(((4.0, -1.0), (-1.0, 4.0)), (1.0, 1.0))
        self.assertAlmostEqual(result.eigenvalues[0], 3.0)
        self.assertAlmostEqual(result.eigenvalues[1], 5.0)
        self.assertGreater(result.periods[0], result.periods[1])
        for shape in result.mode_shapes:
            mass_norm = sum(value * value for value in shape)
            self.assertAlmostEqual(mass_norm, 1.0)
        self.assertAlmostEqual(sum(result.mode_shapes[0][i] * result.mode_shapes[1][i] for i in range(2)), 0.0)

    def test_invalid_modal_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            solve_modes(((1.0, 0.0),), (1.0,))
        with self.assertRaises(ValueError):
            solve_modes(((1.0, 2.0), (0.0, 1.0)), (1.0, 1.0))
        with self.assertRaises(ValueError):
            solve_modes(((0.0,),), (1.0,))


if __name__ == "__main__":
    unittest.main()