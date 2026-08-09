# DesignBook: Professional Structural Engineer's Handbook

Welcome to **DesignBook**, the premier digital-twin toolkit for Reinforced Concrete (RCC) analysis and design. This guide provides a professional walkthrough of the system's capabilities, from initial model setup to production-ready documentation.

---

## ⚡ Quick Start Workflow
1.  **Environment Check**: Run `./dev.sh` to boot the local digital-twin server.
2.  **Initialize Project**: Navigate to the "Dashboard" and create a "New Structural Project."
3.  **Define Geometry**: In the "Geometry Studio," input your X/Y grid lines and Story Elevations.
4.  **Define Sections**: Setup standard concrete material properties (e.g., C25/30) and initial Beam/Column sizes.
5.  **Run Analysis**: Select "Linear Elastic" or "Advanced Modal" from the Analysis tab.
6.  **Review Results**: Inspect Story Drifts, P-M interaction curves, and member stress ratios.
7.  **Generate Documentation**: Download the comprehensive PDF technical report.

---

## 🛠️ Technical Module Guidance

### 1. Geometry Studio (The Digital Twin)
- **Grid Definitions**: Input absolute coordinates for your structural axes.
- **Member Assignment**: Use the 3D viewer to verify that Columns and Beams are mapped to the correct junctions.
- **Support Fixity**: Toggle between Pinned and Fixed base conditions. For high-fidelity foundation modeling, enable "Soil SSI" (Soil-Structure Interaction) in the boundary tab.

### 2. Loading & Envelopes
- **Gravity Loads**: Input slab Dead/Live loads. The engine auto-computes self-weight based on member cross-sections.
- **Lateral Demands**: Configure BNBC 2020 Wind or Seismic parameters. The toolkit generates the vertical load distribution for Equivalent Static Force Method (ESFM) automatically.
- **Combinations**: DesignBook follows ACI 318 load factor envelopes (e.g., $1.2DL + 1.6LL$).

### 3. Structural Analysis Engine (OpenSees)
- **Linear Static**: standard gravity and lateral analysis.
- **Modal Analysis**: View the first 12 vibration modes and periods (T).
- **P-Delta Effects**: Enabled via the "Geometric Non-linearity" toggle for critical tall-building stability checks.

### 4. Interactive Design Loop
DesignBook utilizes a unique "Auto-Convergence" loop:
- If a member fails a capacity check (e.g., Beam shear or Column interaction), the system can **auto-resize** the depth or reinforcement.
- You can review the "Iteration History" to see how the building stiffness matrix stabilized as member sizes shifted.

---

## 🏗️ Interpreting Results
- **P-M Interaction curves**: Located in the Member Details view. Ensure all load points reside within the envelope (capacity surface).
- **Story Drift**: Check the "Serviceability" tab. Ratios should remain within $0.005$ to $0.020$ per building code requirements.
- **Quantity Takeoff**: The toolkit provides a real-time estimate of Concrete Volume ($m^3$) and Steel Weight (tonnes) to assist in cost projection.

---

## 🆘 Technical Support & Troubleshooting
If you encounter a "Solver Singularity" or "Convergence Failure":
1.  Verify that all nodes are correctly connected in the 3D viewer (no "flying members").
2.  Ensure material strengths ($f'_c, f_y$) are positive non-zero values.
3.  Consult the `docs/fix.md` encyclopedia for specific engine error signatures.

*DesignBook: Engineering the future of structural integrity.*
