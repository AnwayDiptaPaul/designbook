import unittest
from backend.engineering.solver import Node2D, TrussElement2D, solve_linear_truss


class LinearTrussSolverTests(unittest.TestCase):
    def test_axial_bar_displacement_and_reaction(self) -> None:
        result = solve_linear_truss(
            nodes=(Node2D(1, 0.0, 0.0, fix_x=True, fix_y=True), Node2D(2, 2.0, 0.0, fix_y=True)),
            elements=(TrussElement2D(1, 1, 2, area=0.01, elastic_modulus=200000.0),),
            loads={2: (10.0, 0.0)},
        )
        self.assertAlmostEqual(result.displacements[2][0], 0.01)
        self.assertAlmostEqual(result.reactions[1][0], -10.0)
        self.assertAlmostEqual(result.reactions[2][0], 0.0)
        self.assertAlmostEqual(result.member_forces[1], 10.0)

    def test_singular_model_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            solve_linear_truss(
                nodes=(Node2D(1, 0.0, 0.0, fix_x=True, fix_y=True), Node2D(2, 2.0, 0.0)),
                elements=(TrussElement2D(1, 1, 2, area=1.0, elastic_modulus=1.0),),
                loads={2: (1.0, 0.0)},
            )

    def test_invalid_element_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            solve_linear_truss(
                nodes=(Node2D(1, 0.0, 0.0, fix_x=True, fix_y=True), Node2D(2, 1.0, 0.0, fix_y=True)),
                elements=(TrussElement2D(1, 1, 2, area=0.0, elastic_modulus=1.0),),
                loads={2: (1.0, 0.0)},
            )


if __name__ == "__main__":
    unittest.main()