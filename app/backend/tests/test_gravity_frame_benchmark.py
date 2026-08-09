import json
from pathlib import Path
import unittest

from backend.engineering.codes.registry import get_default_registry
from backend.engineering.loads import evaluate_envelope, generate_combinations


class GravityFrameBenchmarkTests(unittest.TestCase):
    def test_reference_fixture_is_reproducible(self) -> None:
        fixture_path = Path(__file__).parents[1] / "engineering" / "verification" / "fixtures" / "gravity_frame_member_envelope.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        release = get_default_registry().get("BNBC", "2020")
        envelope = evaluate_envelope(generate_combinations(release, category="strength"), fixture["responses"])
        self.assertEqual(envelope["Mu"].maximum, fixture["expected"]["maximum"]["value"])
        self.assertEqual(envelope["Mu"].maximum_combination, fixture["expected"]["maximum"]["combination"])
        self.assertEqual(envelope["Mu"].minimum, fixture["expected"]["minimum"]["value"])
        self.assertEqual(envelope["Mu"].minimum_combination, fixture["expected"]["minimum"]["combination"])
        self.assertEqual(fixture["status"], "prototype")
        self.assertEqual(fixture["provenance"]["review_status"], "prototype")


if __name__ == "__main__":
    unittest.main()