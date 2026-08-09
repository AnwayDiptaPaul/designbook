import unittest
from backend.engineering.frame_solver import FrameElement2D, FrameNode2D, solve_linear_frame


class LinearFrameSolverTests(unittest.TestCase):
    def test_cantilever_tip_load_matches_closed_form(self) -> None:
        length, load, elastic_modulus, inertia = 3.0, 10.0, 200000.0, 0.002
        result = solve_linear_frame(
            nodes=(FrameNode2D(1, 0.0, 0.0, True, True, True), FrameNode2D(2, length, 0.0)),
            elements=(FrameElement2D(1, 1, 2, 0.01, elastic_modulus, inertia),),
            loads={2: (0.0, -load, 0.0)},
        )
        expected_translation = -load * length**3 / (3 * elastic_modulus * inertia)
        expected_rotation = -load * length**2 / (2 * elastic_modulus * inertia)
        self.assertAlmostEqual(result.displacements[2][1], expected_translation)
        self.assertAlmostEqual(result.displacements[2][2], expected_rotation)
        self.assertAlmostEqual(result.reactions[1][1], load)
        self.assertAlmostEqual(result.reactions[1][2], load * length)
        self.assertLess(result.free_dof_residual_max, 1e-8)

    def test_singular_frame_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            solve_linear_frame(
                nodes=(FrameNode2D(1, 0.0, 0.0, fix_x=True, fix_y=True), FrameNode2D(2, 1.0, 0.0)),
                elements=(FrameElement2D(1, 1, 2, 1.0, 1.0, 1.0),),
                loads={2: (1.0, 0.0, 0.0)},
            )

    def test_invalid_load_shape_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            solve_linear_frame(
                nodes=(FrameNode2D(1, 0.0, 0.0, True, True, True), FrameNode2D(2, 1.0, 0.0, True, True, False)),
                elements=(FrameElement2D(1, 1, 2, 1.0, 1.0, 1.0),),
                loads={2: (1.0, 0.0)},
            )


if __name__ == "__main__":
    unittest.main()