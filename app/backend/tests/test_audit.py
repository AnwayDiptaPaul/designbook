import unittest
from backend.engineering.audit import AnalysisAuditRecord


class AuditRecordTests(unittest.TestCase):
    def test_input_and_output_fingerprints_are_reproducible(self) -> None:
        kwargs = dict(model={"nodes": [1, 2]}, configuration={"combination": "U1"}, output={"moment": 12.5}, solver="linear-frame", solver_version="0.1", standard="BNBC", edition="2020")
        first = AnalysisAuditRecord.create(**kwargs)
        second = AnalysisAuditRecord.create(**kwargs)
        self.assertEqual(first.input_hash, second.input_hash)
        self.assertEqual(first.output_hash, second.output_hash)
        self.assertNotEqual(first.created_at, "")
        self.assertEqual(first.as_dict()["warnings"], [])

    def test_changed_output_and_warnings_are_recorded(self) -> None:
        record = AnalysisAuditRecord.create(model={"n": 1}, configuration={}, output={"u": 0.9}, solver="solver", solver_version="1", standard="BNBC", edition="2020", warnings=("prototype capacity",))
        changed = AnalysisAuditRecord.create(model={"n": 1}, configuration={}, output={"u": 0.95}, solver="solver", solver_version="1", standard="BNBC", edition="2020")
        self.assertNotEqual(record.output_hash, changed.output_hash)
        self.assertEqual(record.as_dict()["warnings"], ["prototype capacity"])

    def test_invalid_metadata_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AnalysisAuditRecord.create(model={}, configuration={}, output={}, solver="", solver_version="1", standard="BNBC", edition="2020")
        with self.assertRaises(ValueError):
            AnalysisAuditRecord.create(model={}, configuration={}, output={}, solver="s", solver_version="1", standard="BNBC", edition="2020", warnings=("",))


if __name__ == "__main__":
    unittest.main()