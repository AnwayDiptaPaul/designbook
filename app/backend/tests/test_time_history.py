import unittest
from backend.engineering.time_history import solve_mdoF_newmark, solve_sdof_newmark


class TimeHistoryTests(unittest.TestCase):
    def test_zero_ground_motion_is_zero_response(self) -> None:
        result = solve_sdof_newmark(1.0, 100.0, 1.0, 0.01, (0.0,) * 10)
        self.assertTrue(all(value == 0.0 for value in result.displacements))
        self.assertEqual(result.times[-1], 0.09)

    def test_constant_ground_acceleration_approaches_static_relative_displacement(self) -> None:
        result = solve_sdof_newmark(1.0, 200.0, 10.0, 0.01, (1.0,) * 1001)
        self.assertAlmostEqual(result.displacements[-1], -1.0 / 200.0, delta=0.001)

    def test_multi_dof_zero_motion_and_single_dof_equivalence(self) -> None:
        multi = solve_mdoF_newmark(((1.0,),), ((100.0,),), ((1.0,),), 0.01, (0.0, 0.1, 0.0), (1.0,))
        scalar = solve_sdof_newmark(1.0, 100.0, 1.0, 0.01, (0.0, 0.1, 0.0))
        self.assertEqual(multi.displacements[0], (0.0,))
        self.assertAlmostEqual(multi.displacements[1][0], scalar.displacements[1])
        self.assertAlmostEqual(multi.accelerations[1][0], scalar.accelerations[1])

    def test_multi_dof_dimension_and_singularity_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            solve_mdoF_newmark(((1.0, 0.0),), ((1.0,),), ((1.0,),), 0.1, (0.0,), (1.0,))
        with self.assertRaises(ValueError):
            solve_mdoF_newmark(((0.0,),), ((0.0,),), ((0.0,),), 0.1, (0.0, 1.0), (1.0,))
    def test_invalid_time_history_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            solve_sdof_newmark(0.0, 100.0, 1.0, 0.01, (0.0,))
        with self.assertRaises(ValueError):
            solve_sdof_newmark(1.0, 100.0, 1.0, 0.01, ())
        with self.assertRaises(ValueError):
            solve_sdof_newmark(1.0, 100.0, 1.0, 0.01, (0.0, 1.0), beta=0.0)


if __name__ == "__main__":
    unittest.main()