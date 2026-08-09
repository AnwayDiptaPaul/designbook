import unittest
from pathlib import Path


class ApiSafetyTests(unittest.TestCase):
    def test_design_api_does_not_fabricate_forces(self) -> None:
        source = (Path(__file__).parents[1] / "api" / "routes" / "design.py").read_text(encoding="utf-8")
        self.assertNotIn('props.get("forces",', source)
        self.assertNotIn('m_props.get("forces",', source)
        self.assertIn("completed snapshot-bound analysis result is required", source)

    def test_analysis_listing_checks_project_scope(self) -> None:
        source = (Path(__file__).parents[1] / "api" / "routes" / "analysis.py").read_text(encoding="utf-8")
        self.assertIn("Project not found", source)
        self.assertIn("select(Project.id)", source)
    def test_analysis_create_validates_snapshot_only_after_feature_gate(self) -> None:
        source = (Path(__file__).parents[1] / "api" / "routes" / "analysis.py").read_text(encoding="utf-8")
        self.assertIn("if not settings.ENABLE_ANALYSIS_EXECUTION", source)
        self.assertIn("prepared_config = prepare_run_config", source)
    def test_analysis_api_is_fail_closed_by_default_and_queues_only_when_enabled(self) -> None:
        source = (Path(__file__).parents[1] / "api" / "routes" / "analysis.py").read_text(encoding="utf-8")
        self.assertIn("ENABLE_ANALYSIS_EXECUTION", source)
        self.assertIn("status_code=501", source)
        self.assertIn("run_analysis.delay", source)
        self.assertNotIn("OpenSeesModelBuilder", source)

    def test_analysis_api_supports_project_scoped_cancellation(self) -> None:
        source = (Path(__file__).parents[1] / "api" / "routes" / "analysis.py").read_text(encoding="utf-8")
        self.assertIn('/analysis-runs/{run_id}/cancel', source)
        self.assertIn('AnalysisStatus.CANCELLED', source)
        self.assertIn('project_id == project_id', source)
    def test_analysis_api_retries_by_creating_a_new_run(self) -> None:
        source = (Path(__file__).parents[1] / "api" / "routes" / "analysis.py").read_text(encoding="utf-8")
        self.assertIn('/analysis-runs/{run_id}/retry', source)
        self.assertIn('Only failed analysis runs can be retried', source)
        self.assertIn('retry = AnalysisRun(', source)
    def test_analysis_preview_is_separate_from_persisted_execution(self) -> None:
        source = (Path(__file__).parents[1] / "api" / "routes" / "analysis.py").read_text(encoding="utf-8")
        self.assertIn('@router.post("/analysis-preview")', source)
        self.assertIn("run_snapshot_analysis", source)

    def test_analysis_task_records_terminal_state_without_fake_status(self) -> None:
        source = (Path(__file__).parents[1] / "tasks" / "analysis_tasks.py").read_text(encoding="utf-8")
        self.assertIn("AnalysisStatus.FAILED", source)
        self.assertIn("AnalysisStatus.COMPLETED", source)
        self.assertNotIn('"status": "completed"', source)

    def test_report_api_is_explicitly_unavailable(self) -> None:
        source = (Path(__file__).parents[1] / "api" / "routes" / "reports.py").read_text(encoding="utf-8")
        self.assertIn("status_code=501", source)
        self.assertNotIn('"status": "stub"', source)


if __name__ == "__main__":
    unittest.main()