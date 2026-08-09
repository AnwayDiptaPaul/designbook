import unittest
from pathlib import Path


class RuntimeSafetyTests(unittest.TestCase):
    def test_compose_enables_worker_only_in_local_stack(self) -> None:
        source = (Path(__file__).parents[2] / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertEqual(source.count('ENABLE_ANALYSIS_EXECUTION: "true"'), 2)
        self.assertIn('CREATE_SCHEMA_ON_STARTUP: "true"', source)

    def test_runtime_smoke_is_dependency_aware(self) -> None:
        source = (Path(__file__).parents[3] / "tools" / "runtime_smoke.py").read_text(encoding="utf-8")
        self.assertIn("/api/ready", source)
        self.assertIn("RUNTIME SMOKE FAILED", source)
        self.assertIn("return 2", source)


if __name__ == "__main__":
    unittest.main()