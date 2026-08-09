# pyre-ignore-all-errors
import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api.schemas.design_standards import BeamDesignInput, ColumnDesignInput, MaterialProps
from backend.core.design.service import StructuralDesignService
from backend.models.member import MemberType
from pydantic import ValidationError

def run_edge_cases():
    print("=" * 60)
    print("EDGE-CASE & BOUNDARY VALIDATION FOR PYDANTIC SCHEMAS")
    print("=" * 60)
    passed = 0
    total = 0

    def assert_validation_error(test_name: str, member_type: MemberType, inputs: dict, forces: dict):
        nonlocal passed, total
        total += 1
        print(f"\n[TEST {total}] {test_name}")
        try:
            StructuralDesignService.design_member(member_type, inputs, forces)
            print("  ❌ FAILED: Expected ValidationError, but passed.")
        except ValidationError as e:
            print("  ✅ PASSED: Caught expected Pydantic ValidationError.")
            for err in e.errors():
                print(f"      - {err['loc'][0]}: {err['msg']}")
        except Exception as e:
            print(f"  ❌ FAILED: Caught unexpected Exception: {e}")

    def assert_success(test_name: str, member_type: MemberType, inputs: dict, forces: dict):
        nonlocal passed, total
        total += 1
        print(f"\n[TEST {total}] {test_name}")
        try:
            res = StructuralDesignService.design_member(member_type, inputs, forces)
            print("  ✅ PASSED: Successfully ran with valid edge-case data.")
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: Expected Success but threw Exception: {e}")

    # TEST 1: Missing Required Fields (width/depth)
    assert_validation_error(
        "Missing required 'width' in Beam design",
        MemberType.BEAM,
        {"depth": 600, "fc": 25, "fy": 400},
        {"Mu": 100, "Vu": 50}
    )

    # TEST 2: Invalid Types (string instead of float)
    assert_validation_error(
        "Invalid type 'string' for forces parameter 'Mu'",
        MemberType.BEAM,
        {"width": 300, "depth": 600},
        {"Mu": "one_hundred", "Vu": 50}
    )

    # TEST 3: Edge Case Success (Negative Bending Moment)
    # The models should accept negative moments
    assert_success(
        "Negative Bending Moment (Valid Edge Case)",
        MemberType.BEAM,
        {"width": 300, "depth": 600},
        {"Mu": -250.0, "Vu": 100.0}
    )

    # TEST 4: Material Defaults Initialization
    # A valid model should default 'fc' to 28 and 'fy' to 420 if material props are omitted,
    # or if we don't supply them at the top level dictionary.
    assert_success(
        "Material Property Defaults fallback",
        MemberType.BEAM,
        {"width": 250, "depth": 500}, # Omitting fc, fy entirely
        {"Mu": 100, "Vu": 50}
    )
    
    # TEST 5: Extreme Values
    assert_validation_error(
        "Invalid negative dimensions",
        MemberType.COLUMN,
        {"b": -400, "h": 400},
        {"Pu": 1000}
    )

    print("\n" + "=" * 60)
    print(f"EDGE CASE VALIDATION COMPLETE: {passed}/{total} manual success assertions passed.")
    print("=" * 60)

if __name__ == "__main__":
    run_edge_cases()
