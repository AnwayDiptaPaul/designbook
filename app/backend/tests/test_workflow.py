import unittest
from backend.engineering.frame_solver import FrameElement2D, FrameNode2D
from backend.engineering.design.capacities import SteelRectangleSection, elastic_yield_capacity
from backend.engineering.workflow import run_frame_design_workflow


class FrameDesignWorkflowTests(unittest.TestCase):
    def test_combination_analysis_feeds_governing_member_check(self) -> None:
        nodes = (FrameNode2D(1, 0.0, 0.0, True, True, True), FrameNode2D(2, 3.0, 0.0))
        elements = (FrameElement2D(1, 1, 2, 0.01, 200000.0, 0.002),)
        capacity = elastic_yield_capacity(SteelRectangleSection(0.2, 0.3, 250000.0))
        result = run_frame_design_workflow(
            nodes, elements,
            {"U1": {2: (0.0, -10.0, 0.0)}, "U2": {2: (0.0, -20.0, 0.0)}},
            {1: capacity},
        )
        self.assertEqual(set(result.analyses_by_combination), {"U1", "U2"})
        self.assertEqual(result.checks_by_member[1].combination, "U2")
        self.assertAlmostEqual(result.demands_by_member[1]["U2"].moment, 60.0)

    def test_missing_capacity_is_rejected(self) -> None:
        nodes = (FrameNode2D(1, 0.0, 0.0, True, True, True), FrameNode2D(2, 1.0, 0.0))
        elements = (FrameElement2D(1, 1, 2, 1.0, 1.0, 1.0),)
        with self.assertRaises(ValueError):
            run_frame_design_workflow(nodes, elements, {"U1": {2: (0.0, -1.0, 0.0)}}, {})


if __name__ == "__main__":
    unittest.main()