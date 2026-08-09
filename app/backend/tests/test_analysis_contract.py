import unittest

from backend.engineering.analysis_contract import AnalysisContractError, prepare_run_config, verify_run_config


class AnalysisContractTests(unittest.TestCase):
    def test_prepare_adds_deterministic_snapshot_hash(self) -> None:
        config = {"snapshot": {"nodes": [], "elements": []}, "options": {"solver": "frame"}}
        prepared = prepare_run_config(config)
        self.assertEqual(len(prepared["snapshot_hash"]), 64)
        self.assertEqual(prepared, prepare_run_config(config))

    def test_mismatched_hash_is_rejected(self) -> None:
        with self.assertRaises(AnalysisContractError):
            prepare_run_config({"snapshot": {"nodes": []}, "snapshot_hash": "bad"})

    def test_missing_snapshot_is_rejected(self) -> None:
        with self.assertRaises(AnalysisContractError):
            prepare_run_config({"options": {"solver": "frame"}})

    def test_persisted_config_must_include_hash(self) -> None:
        with self.assertRaises(AnalysisContractError):
            verify_run_config({"snapshot": {"nodes": []}})


if __name__ == "__main__":
    unittest.main()