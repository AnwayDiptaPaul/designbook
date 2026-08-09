# pyre-ignore-all-errors
"""Automated Design Loop — Iterates analysis ↔ design until structural convergence.

Implements plan.md §Module 4: The Auto-Design Loop Flow.
Integrates with OpenSeesModelBuilder for re-analysis after member resizing.

The loop follows this cycle:
1. Run structural analysis (gravity + modal).
2. Extract member demands (Mu, Vu, Pu).
3. Run ACI 318 / BNBC capacity checks via StructuralDesignService.
4. If any member FAILS, auto-resize (increase depth by 10%) and re-analyze.
5. Repeat until all members pass OR max_iter is reached.
"""

import logging
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger("designbook.design_loop")

# Epsilon to prevent division-by-zero in ratio calculations
EPSILON = 1e-9


class DesignLoop:
    """
    Production-grade automated iteration engine.
    Resizes members based on analysis failures and loops until the structure
    converges on a viable set of member sizes.
    """

    @staticmethod
    def iterate(
        model_runner: Any,
        member_set: List[Dict[str, Any]],
        max_iterations: int = 10,
        convergence_tol: float = 0.01,
        resize_factor: float = 1.10,
    ) -> Dict[str, Any]:
        """
        Full design-loop implementation connecting analysis → design → resize.

        Args:
            model_runner: An object with a callable `run(members)` method that
                          rebuilds the OpenSees model with updated member sizes
                          and returns extracted member forces.
            member_set:   List of member dicts, each containing:
                            - "label": str (e.g., "B-1", "C-3")
                            - "member_type": MemberType enum
                            - "inputs": dict (geometry/material)
                            - "forces": dict (Mu, Vu, Pu — updated each iteration)
            max_iterations:   Hard cap to prevent infinite loops.
            convergence_tol:  Maximum fractional size change below which
                              we declare convergence.
            resize_factor:    Multiplier applied to depth/thickness on failure
                              (default 1.10 = 10% increase per iteration).

        Returns:
            Dict with keys: converged, iterations, member_results, telemetry.
        """
        from backend.core.design.service import StructuralDesignService  # type: ignore

        t_start = time.perf_counter()
        results: Dict[str, Any] = {}
        converged = False
        iteration = 0
        history: List[Dict[str, Any]] = []

        for iteration in range(1, max_iterations + 1):
            t_iter = time.perf_counter()
            max_change = 0.0
            iter_summary: Dict[str, Any] = {
                "iteration": iteration,
                "members_failed": 0,
                "members_resized": 0,
            }

            # ── Step 1: Run analysis (if model_runner is provided) ────────
            if model_runner is not None:
                try:
                    analysis_forces = model_runner.run(member_set)
                    # Update member forces from the analysis result
                    if analysis_forces:
                        for m in member_set:
                            label = m.get("label", "")
                            if label in analysis_forces:
                                m["forces"].update(analysis_forces[label])
                except Exception as e:
                    logger.warning(f"Analysis runner failed at iteration {iteration}: {e}")

            # ── Step 2–3: Design each member ──────────────────────────────
            for i, member in enumerate(member_set):
                mtype = member["member_type"]
                inputs = member["inputs"]
                forces = member["forces"]
                member_key = member.get("label", f"M-{i+1}")

                try:
                    result = StructuralDesignService.design_member(mtype, inputs, forces)
                except Exception as e:
                    logger.error(f"Design failed for {member_key}: {e}")
                    result = {"error": {"status": f"FAIL - Exception: {e}"}}

                # ── Step 4: Check for failures ────────────────────────────
                any_fail = False
                for k, v in result.items():
                    if isinstance(v, dict):
                        st = str(v.get("status", ""))
                        if "FAIL" in st.upper() or "Inadequate" in st:
                            any_fail = True
                            break

                if any_fail:
                    iter_summary["members_failed"] += 1

                # ── Step 5: Auto-resize on failure ────────────────────────
                if any_fail and iteration < max_iterations:
                    size_key = "thickness" if "thickness" in inputs else "depth"
                    old_size = float(inputs.get(size_key, 600.0) or 600.0)
                    new_size = old_size * resize_factor

                    member["inputs"][size_key] = new_size
                    iter_summary["members_resized"] += 1

                    change = abs(new_size - old_size) / max(old_size, EPSILON)
                    max_change = max(max_change, change)
                    logger.info(
                        f"  [{member_key}] FAIL → resized {size_key}: "
                        f"{old_size:.0f} → {new_size:.0f} mm (Δ={change:.1%})"
                    )

                results[member_key] = {
                    "iteration": iteration,
                    "design": result,
                    "converged_size": not any_fail,
                }

            dt_iter = time.perf_counter() - t_iter
            iter_summary["max_change"] = round(max_change, 6)
            iter_summary["duration_seconds"] = round(dt_iter, 4)
            history.append(iter_summary)

            logger.info(
                f"Iteration {iteration}: {iter_summary['members_failed']} failures, "
                f"{iter_summary['members_resized']} resized, Δmax={max_change:.4f} ({dt_iter:.3f}s)"
            )

            if max_change < convergence_tol:
                converged = True
                break

        dt_total = time.perf_counter() - t_start
        status = "Converged" if converged else "Max Iterations Reached"
        logger.info(f"Design loop {status} after {iteration} iterations in {dt_total:.3f}s")

        return {
            "status": status,
            "converged": converged,
            "iterations": iteration,
            "member_results": results,
            "iteration_history": history,
            "telemetry": {
                "total_seconds": round(dt_total, 4),
                "iterations_run": iteration,
            },
        }
