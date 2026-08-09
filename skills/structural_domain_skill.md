# Structural Engineering Domain Skill

When writing engineering logic or augmenting analytical modules, strict adherence to international building science standards is legally and functionally essential.

## Authorized Building Codes
- BNBC 2020 (Bangladesh National Building Code) acts as the primary benchmark for external environment loadings, system parameters, and load combination generators.
- ACI 318-19 (American Concrete Institute) acts as the fundamental mathematical logic layer for structural member design checks (Concrete strength mapping, crack width thresholds).

## Loading & Load Combinations
- **Wind Parameters**: Always follow BNBC Part 6, Chapter 2 formulations. Ensure velocity pressure equations strictly honor $q_z = 0.613 K_z K_{zt} K_d V^2$.
- **Seismic Parameters**: Conform precisely to the Equivalent Static Force Method (ESFM) using exact Zone coefficients ($Z$), Importance factors ($I$), and Building Response Modifications ($R$) under BNBC logic.
- Compute serviceability checks independently utilizing unfactored load derivations (e.g. `S1`, `S2` deflection bounds).

## The Auto-Design Loop Flow
When members fail capacity checks during validation, execute the established "Iterative Resize Logic":
1. Execute gravity and lateral Finite Element loops utilizing `OpenSeesPy`.
2. Determine explicit member forces (Shear $V_u$, Axial $P_u$, Moment $M_{u}$, Torsion $T_u$).
3. Compare against Code interaction curves ($P-M$ combinations for Columns, $\phi V_n$ mapping for beams).
4. If checking fails: incrementally increase section depth (preferred) or section width.
5. If reinforcing ratios ($\rho$) drift past allowed limits, force physical section upscaling.
6. Auto-re-run system stiffness matrices across the FEA engine via OpenSees until convergence < 1% variation is reached. (Normally achieved in 3-5 iterations max).

## Model Integrity Guidelines
Always enforce rigorous unit scaling. Standard metric conversions (Newtons, meters) should map down to the underlying `ops` scripts. The `backend/core/design` directory now contains modules for all standard RCC structural members (beams, columns, slabs, footings, walls, stairs, domes) as well as extended modules for cold-formed steel (`cfs.py`), liquid tanks (`liquid_tank.py`), piles (`pile.py`), quantity takeoffs (`qto.py`), and the iterative design loop controller (`loop.py`). New member types should follow the same pattern: one file per member type with a dedicated design class.
