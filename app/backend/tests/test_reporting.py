import unittest
from backend.engineering.audit import AnalysisAuditRecord
from backend.engineering.design.capacities import SteelRectangleSection, elastic_yield_capacity
from backend.engineering.frame_solver import FrameElement2D, FrameNode2D
from backend.engineering.reporting import build_frame_design_report
from backend.engineering.workflow import run_frame_design_workflow


class ReportingTests(unittest.TestCase):
    def _report(self):
        nodes = (FrameNode2D(1, 0.0, 0.0, True, True, True), FrameNode2D(2, 3.0, 0.0))
        elements = (FrameElement2D(1, 1, 2, 0.01, 200000.0, 0.002),)
        capacity = elastic_yield_capacity(SteelRectangleSection(0.2, 0.3, 250000.0))
        workflow = run_frame_design_workflow(nodes, elements, {"U1": {2: (0.0, -10.0, 0.0)}}, {1: capacity})
        audit = AnalysisAuditRecord.create(model={"nodes": 2}, configuration={"combination": "U1"}, output={"member": 1}, solver="linear-frame", solver_version="0.1", standard="BNBC", edition="2020", warnings=("review required",))
        return build_frame_design_report(workflow, audit)

    def test_report_contains_governing_member_and_audit(self) -> None:
        report = self._report()
        self.assertEqual(report.overall_status, "pass")
        self.assertEqual(report.members[0].governing_combination, "U1")
        self.assertLess(report.max_free_dof_residual, 1e-8)
        self.assertIn("max_free_dof_residual", report.as_dict())
        self.assertIn("review required", report.warnings)
        self.assertIn("prototype-level", report.warnings[1])
        self.assertEqual(report.as_dict()["members"][0]["member_id"], 1)

    def test_failed_member_changes_overall_status(self) -> None:
        nodes = (FrameNode2D(1, 0.0, 0.0, True, True, True), FrameNode2D(2, 3.0, 0.0))
        elements = (FrameElement2D(1, 1, 2, 0.01, 200000.0, 0.002),)
        capacity = elastic_yield_capacity(SteelRectangleSection(0.2, 0.3, 1000.0))
        workflow = run_frame_design_workflow(nodes, elements, {"U1": {2: (0.0, -1000.0, 0.0)}}, {1: capacity})
        audit = AnalysisAuditRecord.create(model={}, configuration={}, output={}, solver="s", solver_version="1", standard="BNBC", edition="2020")
        self.assertEqual(build_frame_design_report(workflow, audit).overall_status, "fail")


if __name__ == "__main__":
    unittest.main()