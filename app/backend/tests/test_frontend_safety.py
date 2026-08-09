import unittest
from pathlib import Path


class FrontendSafetyTests(unittest.TestCase):
    def test_analysis_ui_does_not_simulate_progress_or_success(self) -> None:
        source = (Path(__file__).parents[2] / "frontend" / "src" / "pages" / "AnalysisControl.tsx").read_text(encoding="utf-8")
        self.assertNotIn("setInterval", source)
        self.assertNotIn("Math.random", source)
        self.assertIn("Analysis execution is not currently available", source)

    def test_shared_viewer_does_not_render_fake_building_geometry(self) -> None:
        source = (Path(__file__).parents[2] / "frontend" / "src" / "components" / "ThreeViewer.tsx").read_text(encoding="utf-8")
        self.assertIn("No {mode ===", source)
        self.assertNotIn("Array(25)", source)
        self.assertNotIn("Isometric Building Container", source)
    def test_results_and_detailing_ui_do_not_present_sample_artifacts(self) -> None:
        results = (Path(__file__).parents[2] / "frontend" / "src" / "pages" / "ResultsViewer.tsx").read_text(encoding="utf-8")
        detailing = (Path(__file__).parents[2] / "frontend" / "src" / "pages" / "DetailingDrawings.tsx").read_text(encoding="utf-8")
        self.assertIn("No result set selected", results)
        self.assertNotIn("0.0018", results)
        self.assertNotIn("Node ID", results)
        self.assertIn("Detailing is unavailable", detailing)
        self.assertNotIn("B-1", detailing)
        self.assertNotIn("Export DXF", detailing)
    def test_design_ui_does_not_present_mock_member_results(self) -> None:
        source = (Path(__file__).parents[2] / "frontend" / "src" / "pages" / "DesignModule.tsx").read_text(encoding="utf-8")
        self.assertNotIn("mockMembers", source)
        self.assertNotIn("setInterval", source)
        self.assertIn("No completed analysis result", source)
    def test_analysis_api_client_exposes_cancellation(self) -> None:
        source = (Path(__file__).parents[2] / "frontend" / "src" / "lib" / "api.ts").read_text(encoding="utf-8")
        self.assertIn("cancelAnalysis", source)
        self.assertIn("/cancel", source)
    def test_analysis_api_client_exposes_retry(self) -> None:
        source = (Path(__file__).parents[2] / "frontend" / "src" / "lib" / "api.ts").read_text(encoding="utf-8")
        self.assertIn("retryAnalysis", source)
        self.assertIn("/retry", source)
    def test_dashboard_does_not_present_sample_results(self) -> None:
        source = (Path(__file__).parents[2] / "frontend" / "src" / "pages" / "Dashboard.tsx").read_text(encoding="utf-8")
        self.assertIn("const recentProjects: RecentProject[] = []", source)
        self.assertNotIn("Analysis Complete", source)
        self.assertNotIn("ACI 318-19 Compliant", source)
        self.assertNotIn("Report Generated", source)
    def test_analysis_ui_does_not_present_demo_modal_or_pushover_values(self) -> None:
        source = (Path(__file__).parents[2] / "frontend" / "src" / "pages" / "AnalysisControl.tsx").read_text(encoding="utf-8")
        self.assertIn("No modal periods are available", source)
        self.assertIn("Pushover execution is not currently available", source)
        self.assertNotIn("0.45 / mode", source)
        self.assertNotIn("Roof Center (Auto)", source)
        self.assertNotIn("4.0% of Height", source)
    def test_report_ui_does_not_claim_download(self) -> None:
        source = (Path(__file__).parents[2] / "frontend" / "src" / "pages" / "Reports.tsx").read_text(encoding="utf-8")
        self.assertIn("no document was generated", source)
        self.assertNotIn("PDF Generated and Downloaded", source)


if __name__ == "__main__":
    unittest.main()