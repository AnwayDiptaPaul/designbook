# Structural Building Design App — Development Instructions

---

## 1. Project Overview

Build a full-featured **Reinforced Concrete (RCC) Structural Building Design Application** with a modern web-based UI/UX. The app integrates:

- **OpenSeesPy** for Finite Element Analysis (FEA) and advanced structural analysis
- **Excel-based design sheets** (provided in `./doc-files/design-excel/`) as calculation engines and reference templates
- **Building codes** selectable by the user: BNBC (Bangladesh National Building Code) and any applicable local code (provided in `./doc-files/regulations/`)
- **PWD Material & Price Schedule** for costing (provided in `./doc-files/regulations/`)
- **Area plan and plan maps** as spatial references for model geometry input (provided in `./doc-files/regulations/`)

---

## 2. Provided Reference Files

### 2.1 Design Excel Files (`./doc-files/design-excel/`)
These Excel files are the existing manual calculation templates for RCC design. They cover individual structural member design (beams, columns, slabs, footings, etc.).

**Instructions for integrating and enhancing the Excel files:**
- Parse each Excel file using `openpyxl` or `xlwings` to extract:
  - Cell formulas and their logic
  - Input parameter cells (yellow/highlighted cells by convention)
  - Output result cells
  - Section titles and structural member types covered
- Replicate all formula logic as Python functions/modules so the app can compute independently of Excel
- Enhance the Excel files by:
  - Adding automated formula protection and input validation
  - Adding drop-down selections for bar sizes (8, 10, 12, 16, 20, 25, 32 mm), concrete grades (f'c: 20, 25, 28, 30, 35 MPa), and steel grades (fy: 250, 415, 500 MPa)
  - Adding conditional formatting for pass/fail checks (green/red)
  - Adding cover sheet with project info, code selection, and summary
  - Adding chart sheets for moment, shear, and deflection diagrams per member
  - Linking all member sheets to a master summary sheet
  - Adding a "Design Loop" sheet that flags members needing resize and re-check
  - Exporting the enhanced Excel files back to `./doc-files/design-excel/enhanced/`

### 2.2 Regulatory Documents (`./doc-files/regulations/`)
- **National Building Code (BNBC):** Primary code for structural design, load calculations, seismic and wind provisions
- **Local Building Code:** Secondary/override code where local rules differ from BNBC
- **PWD Material & Price Schedule:** Unit rates for cost estimation of structural elements
- **Area Plan Presentation & Plan Maps:** Used to extract or verify building footprint, site area, zone, and exposure category

---

## 3. Technology Stack

### Backend
| Component | Technology |
|---|---|
| API Framework | FastAPI (Python) |
| Structural FEA | OpenSeesPy |
| Numerical Engine | NumPy, SciPy |
| Excel I/O | openpyxl, xlwings |
| PDF Generation | ReportLab or WeasyPrint |
| Database | PostgreSQL (projects) + Redis (session cache) |
| Task Queue | Celery + Redis (for long analysis runs) |
| File Storage | Local filesystem or S3-compatible |

### Frontend
| Component | Technology |
|---|---|
| Framework | React + TypeScript |
| UI Library | Tailwind CSS + shadcn/ui |
| 3D Visualization | Three.js or React Three Fiber |
| 2D Drawing Canvas | Konva.js or Fabric.js |
| Charts & Diagrams | Recharts + D3.js |
| State Management | Zustand |
| Form Management | React Hook Form + Zod validation |
| API Client | Axios + React Query |

### Deployment
- Docker Compose for local development
- Nginx reverse proxy
- Optional: Kubernetes for production scale

---

## 4. Application Architecture

```
app/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── projects.py
│   │   │   ├── building_input.py
│   │   │   ├── loads.py
│   │   │   ├── analysis.py
│   │   │   ├── design.py
│   │   │   ├── reports.py
│   │   │   └── excel.py
│   │   └── schemas/
│   ├── core/
│   │   ├── loads/
│   │   │   ├── dead_live.py
│   │   │   ├── wind.py          # BNBC wind load per code
│   │   │   └── seismic.py       # EQ static, RSA, TH
│   │   ├── analysis/
│   │   │   ├── opensees_model.py
│   │   │   ├── linear_elastic.py
│   │   │   ├── pdelta.py
│   │   │   ├── nonlinear_hinge.py
│   │   │   └── response_spectrum.py
│   │   ├── design/
│   │   │   ├── beam.py
│   │   │   ├── column.py
│   │   │   ├── slab_oneway.py
│   │   │   ├── slab_twoway.py
│   │   │   ├── slab_beamless.py
│   │   │   ├── shear_wall.py
│   │   │   ├── retaining_wall.py
│   │   │   ├── footing_isolated.py
│   │   │   ├── footing_combined.py
│   │   │   ├── footing_raft.py
│   │   │   ├── staircase.py
│   │   │   └── dome.py
│   │   ├── soil/
│   │   │   └── soil_reaction.py
│   │   ├── combinations/
│   │   │   └── load_combos.py   # BNBC/ACI load combinations
│   │   ├── checks/
│   │   │   └── serviceability.py
│   │   └── detailing/
│   │       └── rebar_detailing.py
│   └── utils/
│       ├── excel_parser.py
│       └── report_generator.py
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── store/
│   │   └── hooks/
└── doc-files/
    ├── design-excel/
    └── regulations/
```

---

## 5. UI/UX Design Guidelines

### 5.1 Overall Layout
- **Left Sidebar:** Project tree — floors, structural members, load cases, analysis runs
- **Center Panel:** Active workspace (3D model viewer / form inputs / analysis results)
- **Right Panel:** Properties inspector, design outputs, warnings
- **Top Toolbar:** Code selector, analysis mode, save, export, report generation
- **Bottom Status Bar:** Analysis progress, warnings count, last-saved time

### 5.2 Design Principles
- **Dark/Light mode** toggle
- Color-coded member status: Gray (not designed), Blue (designing), Green (pass), Red (fail/overstressed), Orange (warning)
- Collapsible panels and resizable panes
- Keyboard shortcuts for power users (e.g., `R` to run analysis, `D` to design all)
- Undo/Redo stack for all model changes
- Autosave every 2 minutes
- Responsive layout (minimum 1280px width recommended)
- Tooltips on all technical input fields referencing the relevant code clause

### 5.3 Key Screens / Modules
1. **Dashboard** — project list, recent projects, quick-start templates
2. **Project Setup** — building info, code selection, site data
3. **Building Geometry Input** — grid definition, floor heights, member placement
4. **Load Input** — dead, live, wind, seismic, soil
5. **Analysis Control** — analysis type selection, run panel, progress viewer
6. **Results Viewer** — deformed shape, force diagrams, stress contours
7. **Design Module** — per-member design with iterative loop controls
8. **Detailing Drawings** — auto-generated rebar layout diagrams
9. **Reports** — design report, quantity takeoff, cost estimate
10. **Excel Manager** — view/edit/export enhanced Excel design sheets

---

## 6. Module 1: Building Inputs

### 6.1 Project Information
```
- Project name, location, client name, engineer name
- Date, revision number
- Building use/occupancy (residential, commercial, industrial, mixed)
- Number of floors (basement, ground, typical, penthouse)
- Total building height
```

### 6.2 Site & Exposure Data
```
- Site coordinates (lat/lon) — auto-fetch seismic zone from BNBC map
- Seismic zone (I, II, III, IV per BNBC)
- Soil type / site class (SA, SB, SC, SD, SE per BNBC)
- Wind exposure category (A, B, C, D)
- Basic wind speed (Vb) from BNBC wind speed map
- Terrain category
- Topographic factor
- Site elevation
```

### 6.3 Grid & Floor Definition
```
- Structural grid: X-axis lines (A, B, C...), Y-axis lines (1, 2, 3...)
- Grid spacing (variable)
- Floor-to-floor heights per story
- Import DXF/DWG floor plan as underlay for grid alignment
- Import area plan from provided plan maps (PDF overlay)
```

### 6.4 Structural Member Placement
```
For each member:
- Select type: Beam / Column / Slab / Shear Wall / etc.
- Assign to grid intersection or span
- Set orientation (local x, y, z axes)
- Set preliminary section size
- Set material properties (concrete grade, steel grade)
- Set clear cover
- Assign to floor level
```

---

## 7. Module 2: Structural Member Orientations

For each member type, define:

| Member | Orientation Parameters |
|---|---|
| Beam | Span direction (X/Y), offset from grid, top/bottom of slab |
| Column | Vertical orientation, local x-axis rotation, eccentric if any |
| One-way Slab | Span direction, supported edges |
| Two-way Slab | Panel bounds, support conditions |
| Beamless Slab (Flat Plate/Flat Slab) | Column grid, drop panel if any, column capital if any |
| Shear Wall | Wall plane (XZ or YZ), pier/spandrel definition |
| Retaining Wall | Stem direction, heel/toe orientation, soil side |
| Isolated Footing | Column it supports, plan dimensions, depth |
| Combined Footing | Columns it supports, geometry |
| Raft Footing | Full plan extents, thickened bands at columns |
| Staircase | Flight direction, landing levels, waist slab direction |
| Dome | Center coordinates, radius, rise, support ring |

Auto-assign local coordinate system per BNBC/ACI convention. Display orientation arrows in 3D viewer.

---

## 8. Module 3: Load Input

### 8.1 Dead Loads
```
- Self-weight: computed automatically from member geometry + unit weight
- Superimposed dead load (SDL): floor finish, partitions, MEP allowance (kPa)
- Wall loads: input as line loads (kN/m) on beams
- Equipment loads: point or area loads
```

### 8.2 Live Loads
```
- Per occupancy per BNBC Table 8.2
- Roof live load
- Live load reduction per BNBC clause (tributary area-based)
```

### 8.3 Wind Loads (auto-calculated — see Module 4)

### 8.4 Seismic Loads (auto-calculated — see Module 5)

### 8.5 Other Loads
```
- Temperature loads (if applicable)
- Hydrostatic pressure (basement/retaining walls)
- Soil pressure (lateral earth pressure on retaining walls / basement)
- Construction loads
- Crane loads (if industrial)
```

---

## 9. Module 4: Wind Load Calculation (per BNBC)

Implement BNBC Part 6, Chapter 2 wind load provisions.

### 4.1 Design Wind Pressure
```
p = q_z × G × C_p − q_i × G_i × C_pi

Where:
- q_z = velocity pressure at height z = 0.613 × K_z × K_zt × K_d × V²  (N/m²)
- V  = basic wind speed (from input, per BNBC wind speed map)
- K_z = velocity pressure exposure coefficient (per Table, terrain category)
- K_zt = topographic factor
- K_d = wind directionality factor
- G   = gust factor (rigid: 0.85, flexible: computed)
- C_p = external pressure coefficient (per BNBC figures)
- C_pi = internal pressure coefficient
```

### 4.2 Steps Implemented
1. Auto-fetch basic wind speed from BNBC map based on site location
2. Compute K_z at each floor level
3. Compute K_zt from user-input topographic feature
4. Calculate q_z per floor
5. Apply C_p for windward wall, leeward wall, side walls, roof
6. Apply C_pi for enclosed, partially enclosed, or open building
7. Generate wind pressure profile (diagram of pressure vs. height)
8. Compute base shear and overturning moment due to wind
9. Distribute wind forces to each floor level (tributary area method)
10. Apply as lateral load cases: Wind-X+, Wind-X−, Wind-Y+, Wind-Y−

---

## 10. Module 5: Seismic Load Calculation (per BNBC)

Implement BNBC Part 6, Chapter 3 seismic provisions.

### 5.1 Analysis Method Selection
Provide a toggle for:
- **Equivalent Static Force Method (ESFM)**
- **Response Spectrum Analysis (RSA)**
- **Time-History Analysis (THA)**

### 5.2 Moment Frame Type Selection
- **OMRF** — Ordinary Moment Resisting Frame
- **IMRF** — Intermediate Moment Resisting Frame
- **SMRF** — Special Moment Resisting Frame

Frame type affects:
- Response modification factor R
- Detailing requirements
- Height restrictions

### 5.3 Equivalent Static Force Method
```
Base Shear: V = (Z × I × S × C_s) / R × W

Where:
- Z  = seismic zone factor (BNBC Table 6.2.12)
- I  = importance factor (occupancy-based)
- S  = site coefficient (soil class SA–SE)
- C_s = seismic response coefficient
- R  = response modification factor (OMRF/IMRF/SMRF)
- W  = seismic weight (DL + applicable LL)

Vertical distribution per BNBC:
F_x = C_vx × V
C_vx = w_x × h_x^k / Σ(w_i × h_i^k)
k = 1 for T ≤ 0.5s, 2 for T ≥ 2.5s, interpolated
```

### 5.4 Response Spectrum Analysis
```
- Use BNBC design response spectrum or user-supplied spectrum
- Perform modal analysis in OpenSeesPy (eigenvalue extraction)
- Extract natural frequencies, mode shapes, modal participation factors
- Combine modal responses using CQC or SRSS method
- Scale combined response to match minimum base shear (BNBC requirement)
- Display mode shapes in 3D viewer with animation
```

### 5.5 Time-History Analysis
```
- Allow user to upload ground motion records (.AT2 or .txt format)
- Support multiple ground motion pairs (X and Y direction)
- Run nonlinear time-history in OpenSeesPy (Newmark integration)
- Display time-history of displacement, velocity, acceleration at each floor
- Extract maximum response envelope for design
```

### 5.6 Outputs
- Seismic base shear per direction
- Story forces and overturning moments
- Drift check per BNBC (max allowable story drift)
- Torsional irregularity check

---

## 11. Module 6: Soil Reaction Calculations

Input from soil investigation report (geotechnical report):
```
- Borehole data: depth, SPT N-values, soil description per layer
- Soil classification (USCS or AASHTO)
- Allowable bearing capacity (q_a) — net or gross
- Subgrade modulus (k_s) for raft/mat foundation (Winkler spring model)
- Active/passive earth pressure coefficients (Ka, Kp, K0)
- Groundwater table depth
- Liquefaction susceptibility (if seismic zone II+)
```

Calculations:
```
- Gross and net bearing pressure under each footing
- Bearing capacity adequacy check: q_actual ≤ q_allowable
- Settlement check: immediate (elastic) + consolidation (if cohesive)
- Subgrade reaction forces (for raft foundation on Winkler springs)
- Lateral earth pressure diagrams for retaining walls and basement walls
- Uplift check for hydrostatic pressure
```

---

## 12. Module 7: Load Combinations & Envelopes

### 12.1 Strength (Ultimate) Combinations — ACI 318 / BNBC
```
U1  = 1.4 D
U2  = 1.2 D + 1.6 L + 0.5 (Lr or S or R)
U3  = 1.2 D + 1.6 (Lr or S or R) + (1.0 L or 0.5 W)
U4  = 1.2 D + 1.0 W + 1.0 L + 0.5 (Lr or S or R)
U5  = 0.9 D + 1.0 W
U6  = 1.2 D + 1.0 E + 1.0 L
U7  = 0.9 D + 1.0 E
```

### 12.2 Serviceability (Unfactored) Combinations
```
S1  = D + L                       (for deflection)
S2  = D + 0.5 L                   (long-term deflection)
S3  = D + L + W                   (service wind)
S4  = D + 0.7 E                   (service seismic)
```

### 12.3 Envelope Generation
- For each structural member, extract:
  - Maximum positive moment envelope
  - Maximum negative moment envelope
  - Maximum shear envelope
  - Maximum axial force envelope
  - Maximum torsion envelope
- Envelopes computed across all applicable load combinations

---

## 13. Module 8: Structural Analysis (OpenSeesPy)

### 13.1 Model Build
```python
# Pseudocode structure
import openseespy.opensees as ops

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Define nodes at column/beam intersections per grid
# Define beam-column elements (elasticBeamColumn or forceBeamColumn)
# Define slab elements (ShellMITC4 or ShellDKGQ)
# Define shear wall elements (ShellMITC4)
# Define foundation elements (Winkler springs for raft)
# Apply boundary conditions (fixed base, pinned, etc.)
# Apply gravity loads, lateral loads per combination
```

### 13.2 Gravity Analysis
```
- Apply dead and live loads as distributed/point loads
- Run static linear elastic analysis
- Extract member forces and nodal displacements
```

### 13.3 Lateral Analysis
```
- Apply wind or seismic story forces at each floor diaphragm
- Run for each direction (X+, X−, Y+, Y−)
- Extract story drifts, base shear, member forces
```

### 13.4 Modal Analysis
```
- Run eigenvalue analysis
- Extract first N modes (typically 3× number of floors, min 12)
- Compute mass participation ratios (≥90% in each direction required by BNBC)
- Store mode shapes for RSA
```

### 13.5 P-Delta Analysis
*(Activate if building is slender or seismic zone ≥ II)*
```
- Use geometric transformation 'PDelta' in OpenSeesPy
- Apply gravity loads first, then lateral loads
- Check stability coefficient θ = P×Δ / (V×h_story) ≤ 0.10 (or amplified if ≤ 0.25)
- If θ > 0.10: amplify lateral forces by 1/(1−θ)
- If θ > 0.25: redesign required — flag to user
```
User toggle: **Enable P-Delta Analysis** (recommended for buildings > 5 stories or in seismic zones III/IV)

### 13.6 Nonlinear Plastic Hinge Analysis
*(For pushover analysis and performance-based design)*
```
- Replace elastic beam-column elements with nonlinear elements
  (beamWithHinges or nonlinearBeamColumn)
- Define fiber section or concentrated hinge using 
  Ibarra-Medina-Krawinkler (IMK) deterioration model
- Apply gravity loads (constant) then monotonically increasing lateral load
- Generate pushover curve (base shear vs. roof drift)
- Identify performance points: IO (Immediate Occupancy), 
  LS (Life Safety), CP (Collapse Prevention) per FEMA 356
- Flag members with plastic rotation demand > capacity
```
User toggle: **Enable Pushover / Plastic Hinge Analysis**

---

## 14. Module 9: Structural Member Design

All design per ACI 318-19 provisions cross-referenced with BNBC selected code.

### 14.1 Beam Design
```
Inputs: Mu(+), Mu(−), Vu, Tu (from analysis envelope)

Flexural design:
- Compute required As = Mu / (φ × fy × (d − a/2))
- Iterate for 'a' (depth of stress block)
- Check ρ_min ≤ ρ ≤ ρ_max (ACI 9.6, 9.7)
- Select bar arrangement (number and size)
- Design for T-beam effect if slab is in compression

Shear design:
- Compute Vc (concrete shear capacity)
- If Vu > φVc/2: design stirrups
- Compute required Av/s, select bar size and spacing
- Apply maximum stirrup spacing (d/2 or 600mm)

Torsion design:
- Check if torsion exceeds threshold
- Design closed stirrups and longitudinal bars for torsion

Detailing:
- Bar cutoff locations
- Development lengths (straight, hooked)
- Splice lengths
```

### 14.2 Column Design
```
Inputs: Pu, Mu_x, Mu_y, Vu (from all combinations)

- Classify as tied or spiral column
- Check slenderness: if λ = kL/r > 34−12(M1/M2): slender column
  - Apply moment magnification (non-sway and sway cases)
- Generate P-M interaction diagram (biaxial)
  - Compute for multiple angle increments (0°, 15°, 30°, ..., 360°)
  - Plot combined P-Mx-My surface
- Check all load combination points lie within interaction surface
- Design transverse reinforcement (ties or spiral) per ACI 25.7
- Output: section size (b×h), longitudinal bars (number, size, arrangement),
  tie/spiral size and spacing
```

### 14.3 One-Way Slab Design
```
- Analyze as continuous beam on supports (moment coefficients or FEM)
- Design flexural steel top and bottom
- Check shear (typically no shear steel in slabs, check Vc ≥ Vu)
- Check minimum temperature & shrinkage steel (As_min = 0.0018bh)
- Check deflection (L/d ratio or direct calculation)
```

### 14.4 Two-Way Slab Design (Direct Design Method or Equivalent Frame)
```
- Divide into column and middle strips
- Distribute moments to strips per ACI Table 8.10.5
- Design each strip as one-way element
- Check for punching shear at columns
- Check for punching shear at concentrated loads
```

### 14.5 Beamless Slab (Flat Plate / Flat Slab)
```
- Apply Direct Design or Equivalent Frame Method
- Critical punching shear check at column perimeters (ACI 22.6)
  bo = perimeter at d/2 from column face
  Vu ≤ φVc = φ × (0.33√f'c) × bo × d
- If punching fails: add shear studs, drop panel, or column capital
- Check edge and corner column moment transfer (fraction transferred by flexure)
```

### 14.6 Shear Wall Design
```
- Classify as ordinary, intermediate, or special shear wall (per OMER/IMRF/SMRF)
- Design for combined axial + bending + shear
- Minimum distributed steel: ρ_horizontal and ρ_vertical ≥ 0.0025
- Boundary element check (if extreme fiber stress > 0.2f'c: provide boundary elements)
- Coupling beam design if openings present
```

### 14.7 Retaining Wall Design
```
Inputs: Soil data (γ, φ, c), surcharge, water table

- Check overturning stability: FS ≥ 2.0
- Check sliding stability: FS ≥ 1.5
- Check bearing capacity: q_actual ≤ q_allowable
- Design stem for cantilever moment and shear
- Design base (heel and toe) for upward soil pressure
- Design shear key if sliding FS insufficient
```

### 14.8 Isolated Footing Design
```
- Size footing plan: B × L based on P_service / q_allowable
- Compute factored net upward soil pressure: q_u
- Check wide-beam shear at d from column face
- Check two-way (punching) shear at d/2 from column face
- Design flexural steel in both directions
- Check development length of column dowels into footing
```

### 14.9 Combined Footing Design
```
- Size footing so centroid coincides with column load resultant
- Compute pressure distribution (uniform or trapezoidal)
- Design as beam in longitudinal direction (bending + shear)
- Design transverse beams under each column
```

### 14.10 Raft Foundation Design
```
- Model on Winkler spring foundation in OpenSeesPy
- Springs: k = k_s × tributary area (k_s = subgrade modulus from soil report)
- Compute pressure distribution, settlements
- Design raft slab for flexure and shear (two-way behavior)
- Check differential settlement
- Thickened band beams at column lines if needed
```

### 14.11 Staircase Design
```
- Design waist slab (inclined slab) as one-way spanning element
- Include dead weight of steps (average thickness method)
- Design longitudinal steel and check shear at supports
- Design landing slab
- Check lateral support of stringer beams
```

### 14.12 Dome Design
```
- Compute membrane forces: meridional (N_φ) and hoop (N_θ) forces
  N_φ = −wR / (1 + cos φ) (meridional thrust)
  N_θ = wR (cos φ − 1/(1 + cos φ)) (hoop force)
- Identify tension ring and compression crown requirements
- Check for tension zone (hoop tension) beyond φ = 51.8° from crown
- Design reinforcement for tension zone
- Design ring beam at base for horizontal thrust
- Check buckling of dome shell
```

---

## 15. Module 10: Serviceability Checks

### 15.1 Deflection Checks (ACI 318, BNBC)
```
Immediate deflection (short-term):
  Δ_i = 5wL⁴ / (384 E_c I_e)  [for simple beam, use appropriate formula for continuity]
  I_e = effective moment of inertia (Branson equation, ACI 24.2.3)

Long-term deflection (creep + shrinkage):
  Δ_LT = λ_Δ × Δ_i (sustained)
  λ_Δ = ξ / (1 + 50ρ')
  ξ = time-dependent factor (5 years: 2.0)

Allowable deflections (ACI Table 24.2.2):
  L/360 for floors supporting non-structural elements susceptible to damage
  L/480 for roofs
  L/240 for non-critical members
```

### 15.2 Crack Width Check
```
- Compute maximum bar spacing: s ≤ 380(280/fs) − 2.5c_c (ACI 24.3.2)
- Or check max bar spacing ≤ 300(280/fs)
- fs = service stress in tension steel = Ms / (As × jd)
```

### 15.3 Story Drift Limits (BNBC seismic)
```
- Compute story drift ratio = Δ / h_story
- Allowable: 0.010 for brittle non-structural elements
             0.020 for ductile non-structural elements
             0.025 for flexible buildings (BNBC)
```

### 15.4 Vibration Check (Floors)
```
- Compute fundamental frequency of floor panel
- Natural frequency fn > 4 Hz for walking comfort
```

---

## 16. Module 11: Design Loop System

The design loop ensures members are consistently sized and all checks pass.

### 16.1 Loop Logic
```
1. Run analysis with preliminary member sizes
2. Extract member force demands (Mu, Vu, Pu, Tu)
3. Design member reinforcement
4. Check all code requirements (strength + serviceability)
5. If any check fails:
   a. Increase section size (depth first, then width)
   b. Increase reinforcement (up to ρ_max)
   c. Flag if both limits exceeded: notify user to resize manually
6. Update section properties (I, A) in the structural model
7. Rerun analysis with updated properties
8. Repeat until:
   - All checks pass, AND
   - Section properties change < 1% between iterations
9. Convergence typically achieved in 3–5 iterations
```

### 16.2 Loop Controls in UI
```
- Toggle: Auto Loop ON / OFF
- Max iterations slider (default: 10)
- Convergence tolerance input (default: 1%)
- Per-member override: lock size and only design reinforcement
- Visual indicator: loop iteration count per member, color status
```

### 16.3 Loop for Foundations
```
- Loop includes soil bearing capacity check
- If q_actual > q_allow: increase footing size
- Re-check settlement after each resize
```

---

## 17. Module 12: Detailing & Design Report

### 17.1 Auto-Generated Detailing
For each member type, generate:
- **Beam:** Elevation view with bar locations, cutoffs, stirrup spacing zones, hooks
- **Column:** Cross-section with bar layout, tie arrangement, lap splice zones
- **Slab:** Plan view with bar arrangement, top/bottom steel per strip
- **Footing:** Plan and section view with reinforcement grid
- **Shear Wall:** Elevation with boundary element reinforcement, distributed steel
- **Staircase:** Section with waist slab steel, landing steel
- **Retaining Wall:** Section with stem and base reinforcement

Detailing per:
- ACI 318-19 detailing requirements
- BNBC detailing provisions
- Selected frame type (OMRF/IMRF/SMRF) additional ductility requirements

### 17.2 Design Report Contents
```
Cover page:
- Project name, location, engineer, date, revision, code used

Section 1: Project Summary
- Building description, number of floors, total height, occupancy

Section 2: Material Properties
- Concrete f'c, Steel fy, unit weights, E_c, E_s

Section 3: Load Summary
- Dead, live, wind, seismic base shear summary

Section 4: Analysis Results
- Model description, number of nodes/elements
- Natural periods and frequencies (modal analysis)
- Story forces, drifts, base shear
- P-Delta stability check (if performed)

Section 5: Member Design
- For each member: inputs, demands, design, checks, output
- Include interaction diagrams for columns
- Include moment/shear diagrams for beams

Section 6: Foundation Design
- Soil parameters, bearing checks, settlement summary, reinforcement

Section 7: Serviceability
- Deflection summary, crack width checks, drift checks

Section 8: Detailing Drawings
- Auto-generated detailing sketches (embedded as vector images)

Section 9: Quantity Takeoff
- Concrete volume (m³) per member type
- Reinforcement weight (kg) per member type
- Formwork area (m²)

Section 10: Cost Estimate
- Unit rates from PWD Material & Price Schedule
- Total estimated cost per element and overall
```

Report export formats: **PDF**, **Word (.docx)**, **Excel (.xlsx summary)**

---

## 18. Code Compliance Reference Table

| Item | BNBC Reference | ACI 318-19 Reference |
|---|---|---|
| Live loads | Part 6, Chapter 2, Table 6.2.1 | — |
| Wind loads | Part 6, Chapter 2, Section 6.2.4 | ASCE 7 |
| Seismic loads | Part 6, Chapter 3 | ASCE 7 |
| Beam flexure | Part 6, Chapter 6 | ACI 9 |
| Column design | Part 6, Chapter 6 | ACI 10 |
| Two-way slab | Part 6, Chapter 6 | ACI 8.10 |
| Shear design | Part 6, Chapter 6 | ACI 22 |
| Footing design | Part 6, Chapter 6 | ACI 13 |
| Development lengths | Part 6, Chapter 6 | ACI 25 |
| Deflection limits | Part 6, Chapter 6 | ACI 24 |
| Special detailing (SMRF) | Part 6, Chapter 6 | ACI 18 |

---

## 19. Implementation Phases

### Phase 1 — Foundation (Months 1–2)
- [ ] Project setup, database schema, API skeleton
- [ ] Building input forms (geometry, grid, materials)
- [ ] Excel file parser and enhancer
- [ ] Basic OpenSeesPy model builder (nodes, beams, columns)
- [ ] Gravity analysis (linear elastic)
- [ ] Dead and live load application
- [ ] Basic beam and column design (no iteration)
- [ ] Simple PDF report

### Phase 2 — Lateral Loads (Months 3–4)
- [ ] Wind load calculator (full BNBC procedure)
- [ ] Seismic ESFM calculator
- [ ] Load combinations engine
- [ ] Lateral analysis with story drift checks
- [ ] Response Spectrum Analysis (modal + CQC/SRSS)
- [ ] 3D model viewer with deformed shape

### Phase 3 — Full Design Suite (Months 5–6)
- [ ] All 12 member types design modules
- [ ] Serviceability checks
- [ ] Design loop system
- [ ] Soil reaction and foundation design
- [ ] Detailing generation
- [ ] Full design report

### Phase 4 — Advanced Analysis (Months 7–8)
- [ ] P-Delta analysis
- [ ] Nonlinear pushover analysis
- [ ] Time-History Analysis
- [ ] SMRF/IMRF special detailing
- [ ] Raft foundation on Winkler springs

### Phase 5 — Polish & Reporting (Month 9)
- [ ] UI/UX refinement
- [ ] Cost estimation module (PWD rates)
- [ ] Excel export of design sheets
- [ ] Quantity takeoff
- [ ] User documentation

---

## 20. Key Dependencies

```txt
# requirements.txt (backend)
fastapi>=0.110.0
uvicorn
openseespy>=3.4.0
numpy>=1.26.0
scipy>=1.12.0
openpyxl>=3.1.0
xlwings>=0.30.0
reportlab>=4.0.0
weasyprint>=60.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
celery>=5.3.0
redis>=5.0.0
matplotlib>=3.8.0
pandas>=2.0.0
python-multipart
python-jose[cryptography]
passlib[bcrypt]
```

```json
// package.json (frontend dependencies)
{
  "dependencies": {
    "react": "^18.2.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "latest",
    "three": "^0.162.0",
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.99.0",
    "konva": "^9.3.0",
    "recharts": "^2.12.0",
    "d3": "^7.9.0",
    "zustand": "^4.5.0",
    "react-hook-form": "^7.51.0",
    "zod": "^3.22.0",
    "@tanstack/react-query": "^5.28.0",
    "axios": "^1.6.0"
  }
}
```

---

## 21. Notes for Developers

1. **OpenSeesPy model state** should be rebuilt fresh for each analysis run (no persistent ops state between runs). Store model parameters in the database and rebuild the ops model in the Celery worker.

2. **Excel files** should be treated as authoritative design references. The Python design modules should replicate the Excel logic exactly and the outputs should match. Run regression tests comparing Python outputs to Excel outputs for sample inputs.

3. **Code selection** (BNBC vs local code) must be enforced as a global context throughout the app. Any code-specific parameter (load factors, allowable stresses, detailing rules) must be keyed to the selected code.

4. **P-Delta** and **nonlinear hinge** analysis are computationally expensive. Always run via Celery async tasks with real-time progress streaming to the frontend via WebSocket.

5. **The design loop** should track section property changes between iterations. If properties converge but any check still fails, alert the user rather than looping infinitely.

6. **Detailing drawings** should be generated as SVG (scalable) and embedded in both the web UI and the PDF report.

7. **Units** — maintain SI units (kN, m, MPa) throughout the backend. The frontend may optionally display imperial units (kip, ft, psi) with a toggle, but all computations remain SI.

8. **Seismic zone and wind speed** should be auto-filled from site coordinates using digitized BNBC hazard maps stored as GeoJSON lookups.

---

*End of Instructions — Version 1.0*
