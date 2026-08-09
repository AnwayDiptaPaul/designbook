# Reference Documents & Calculation Workbooks (`doc-files/`)

This document serves as an inventory and reference guide for the regulatory documents, code-compliance materials, and design spreadsheets used to develop and verify **DesignBook**.

Due to the size of these reference binaries (PDFs and Excel workbooks), the raw files in the `doc-files/` directory are ignored by Git (configured in `.gitignore`) and are not hosted on GitHub. If you are developing locally, you can obtain these files from the project maintainers or place your own copies in the `doc-files/` folder.

---

## 🌐 External Reference Database

For a structured, machine-readable (AI-ready) version of the Bangladesh National Building Code (BNBC) 2020 clauses, tables, and Mermaid flowcharts, please refer to the following repository:

*   **Repository:** [bnbc-2020-database](https://github.com/AnwayDiptaPaul/bnbc-2020-database/)
*   **Description:** An AI-ready knowledge base of BNBC 2020 structured for RAG (Retrieval-Augmented Generation) applications, semantic routing, and compliance automation.

---

## 📁 Directory Structure of `doc-files/`

If populated locally, the directory contains the following layout:

```text
doc-files/
├── regulations/          # National building codes, area plans, and PWD rates
│   └── BNBC_2020/        # Split PDF files for each part of BNBC 2020
└── design-excel/         # 34 Excel sheets spanning loads, RCC design, and costing
```

---

## 🏛️ Regulations & Standards (`doc-files/regulations/`)

These documents provide the regulatory foundation for the design engine, including structural loads, detailing requirements, and material costs.

### BNBC 2020 (Bangladesh National Building Code)
The official code is split into parts for granular reference:

| File Name | Description / Topic |
|---|---|
| [`BNBC_2020_Index.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Index.pdf) | Table of Contents & Subject Index |
| [`BNBC_2020_Part-1.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Part-1.pdf) | Part 1: Administration |
| [`BNBC_2020_Part-2.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Part-2.pdf) | Part 2: Classification of Buildings and General Building Requirements |
| [`BNBC_2020_Part-3.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Part-3.pdf) | Part 3: General Building Requirements, Control and Regulation |
| [`BNBC_2020_Part-4.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Part-4.pdf) | Part 4: Fire Protection |
| [`BNBC_2020_Part-5.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Part-5.pdf) | Part 5: Building Materials |
| [`BNBC_2020_Part-6.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Part-6.pdf) | Part 6: Structural Design (Loads, Concrete, Soils/Foundations, Steel) |
| [`BNBC_2020_Part-7.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Part-7.pdf) | Part 7: Construction Practices and Safety |
| [`BNBC_2020_Part-8.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Part-8.pdf) | Part 8: Building Services (Electrical, Plumbing, HVAC, Mechanical) |
| [`BNBC_2020_Part-9.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Part-9.pdf) | Part 9: Alteration, Addition to and Change of Use of Existing Buildings |
| [`BNBC_2020_Part-10.pdf`](./doc-files/regulations/BNBC_2020/BNBC_2020_Part-10.pdf) | Part 10: Signs and Outdoor Display |

### General Dhaka Regulations & Planning Reference Maps
| File Name | Description / Topic |
|---|---|
| [`Detailed_Area_Plan_Map_Dhaka.pdf`](./doc-files/regulations/Detailed_Area_Plan_Map_Dhaka.pdf) | Detailed Area Plan (DAP) Map for Dhaka Metropolitan area |
| [`Dhaka_Building_Code_2008.pdf`](./doc-files/regulations/Dhaka_Building_Code_2008.pdf) | Dhaka Building Code (Mahanagar Imarat Nirman Bidhimala 2008) |
| [`Dhaka_Green_Index_Map.pdf`](./doc-files/regulations/Dhaka_Green_Index_Map.pdf) | Dhaka Green Index Map (Environmental zones and vegetation ratio) |
| [`Dhaka_Structure_Plan.pdf`](./doc-files/regulations/Dhaka_Structure_Plan.pdf) | Dhaka Structure Plan (Strategic planning guidelines) |
| [`PWDSoR2022-Revised-2.3.23.pdf`](./doc-files/regulations/PWDSoR2022-Revised-2.3.23.pdf) | Public Works Department (PWD) Schedule of Rates 2022 (Revised March 2023) |

---

## 📊 Structural Calculation Spreadsheets (`doc-files/design-excel/`)

These design sheets contain detailed calculations and formulas that serve as the parity benchmark for DesignBook's automated analysis and design engine.

### Group A: Load Calculations & Lateral Demands (Wind/Seismic)
Used to calculate live, dead, wind, and seismic loads based on BNBC 2020 and ASCE 7-05.

| File Name | Scope |
|---|---|
| [`A1-Earth-Quake-Analysis-Excel-As-per-BNBC-2020-ASCE-7-05.xlsx`](./doc-files/design-excel/A1-Earth-Quake-Analysis-Excel-As-per-BNBC-2020-ASCE-7-05.xlsx) | Seismic base shear and vertical force distribution |
| [`A2-Wind-load-Analysis-Excel-As-per-BNBC-2020-ASCE-7-05-Re-modifed-August-2021.xlsx`](./doc-files/design-excel/A2-Wind-load-Analysis-Excel-As-per-BNBC-2020-ASCE-7-05-Re-modifed-August-2021.xlsx) | Wind force calculation (MWFRS and C&C) |
| [`A3-Vertical-Earthquake-Effect-Cal.-Excel-As-per-BNBC-2020.xlsx`](./doc-files/design-excel/A3-Vertical-Earthquake-Effect-Cal.-Excel-As-per-BNBC-2020.xlsx) | Vertical earthquake acceleration calculations |

### Group B: Building Stability & Frame Checks
Critical stability checks required to govern the overall building configuration under lateral load combinations.

| File Name | Scope |
|---|---|
| [`B1-P-Delta-Check-of-a-Building.xlsx`](./doc-files/design-excel/B1-P-Delta-Check-of-a-Building.xlsx) | Second-order P-Delta stability verification |
| [`B2-Base-Shear-CheckSeismic-Value.xlsx`](./doc-files/design-excel/B2-Base-Shear-CheckSeismic-Value.xlsx) | Base shear comparison (analytical vs. empirical) |
| [`B3-Drifts-and-sway-limitation.xlsx`](./doc-files/design-excel/B3-Drifts-and-sway-limitation.xlsx) | Serviceability drift limits validation |
| [`B4-Soft-story-X-Y-Direction.xlsx`](./doc-files/design-excel/B4-Soft-story-X-Y-Direction.xlsx) | Stiffness check for vertical structural irregularity (soft story) |
| [`B5-Torsional-Irregularity.xlsx`](./doc-files/design-excel/B5-Torsional-Irregularity.xlsx) | Check for torsional amplification under eccentric loads |
| [`B6-Story-drift-and-drift-ratio-check.xlsx`](./doc-files/design-excel/B6-Story-drift-and-drift-ratio-check.xlsx) | Detailed story-by-story drift check |
| [`B7-Overturning-Moment-Check.xlsx`](./doc-files/design-excel/B7-Overturning-Moment-Check.xlsx) | Overall foundation overturning/stability check |

### Group C: RCC Member Design
Standard design formulas for beams, columns, slabs, and footings utilizing WSD (Working Stress Design) and USD (Ultimate Strength Design) methods.

| File Name | Scope |
|---|---|
| [`C1-Two-Way-Slab-Design-WSD.xlsx`](./doc-files/design-excel/C1-Two-Way-Slab-Design-WSD.xlsx) | Two-way slab flexure design using WSD |
| [`C2-Two-Way-Slab-Design-USD.xlsx`](./doc-files/design-excel/C2-Two-Way-Slab-Design-USD.xlsx) | Two-way slab flexure design using USD |
| [`C9-Cantilever-Slab-Balcony-Design-WSD.xlsx`](./doc-files/design-excel/C9-Cantilever-Slab-Balcony-Design-WSD.xlsx) | Cantilever slab bending and shear check (WSD) |
| [`C3-Beam-Design-as-per-BNBC-2020-and-ACI-318-08.xls`](./doc-files/design-excel/C3-Beam-Design-as-per-BNBC-2020-and-ACI-318-08.xls) | Flexure and shear design for RC Beams |
| [`C12-Column-Rectangle-Design-ACI-318-02.xlsx`](./doc-files/design-excel/C12-Column-Rectangle-Design-ACI-318-02.xlsx) | Rectangular column design and P-M interaction |
| [`C5-Circular-Column-ACI-318-02.xls`](./doc-files/design-excel/C5-Circular-Column-ACI-318-02.xls) | Circular column design (spiral or tied) |
| [`C6-Isolated-Footing.xls`](./doc-files/design-excel/C6-Isolated-Footing.xls) | Sizing and rebar design for isolated footing |
| [`C7-Combined-Footing.xls`](./doc-files/design-excel/C7-Combined-Footing.xls) | Design for combined footings (two columns) |
| [`C10-Single-Footing-Square-Design-USD.xlsx`](./doc-files/design-excel/C10-Single-Footing-Square-Design-USD.xlsx) | Square foundation design using USD |
| [`C11-Single-Footing-Rectangle-Design-USD.xlsx`](./doc-files/design-excel/C11-Single-Footing-Rectangle-Design-USD.xlsx) | Rectangular foundation design using USD |
| [`C8-Shear-Wall-Design-Excel.xls`](./doc-files/design-excel/C8-Shear-Wall-Design-Excel.xls) | Shear wall design for lateral loads |

### Group D: Staircase Design
Detailed designs for different geometries of staircases under USD.

| File Name | Scope |
|---|---|
| [`D1-Stair-Design-USD-Case-1.xlsx`](./doc-files/design-excel/D1-Stair-Design-USD-Case-1.xlsx) | Staircase design (USD) - Case 1 geometry |
| [`D2-Stair-Design-USD-Case-2.xlsx`](./doc-files/design-excel/D2-Stair-Design-USD-Case-2.xlsx) | Staircase design (USD) - Case 2 geometry |
| [`D3-Stair-Design-USD-Case-3.xlsx`](./doc-files/design-excel/D3-Stair-Design-USD-Case-3.xlsx) | Staircase design (USD) - Case 3 geometry |
| [`D4-Stair-Design-USD-Case-4.xlsx`](./doc-files/design-excel/D4-Stair-Design-USD-Case-4.xlsx) | Staircase design (USD) - Case 4 geometry |
| [`D5-Stair-Design-USD-Case-5.xlsx`](./doc-files/design-excel/D5-Stair-Design-USD-Case-5.xlsx) | Staircase design (USD) - Case 5 geometry |
| [`D6-Stair-Design-USD-Case-6.xlsx`](./doc-files/design-excel/D6-Stair-Design-USD-Case-6.xlsx) | Staircase design (USD) - Case 6 geometry |

### Group E: Reinforcement Details & Lapping
Detailing checks, development lengths, and shear reinforcements.

| File Name | Scope |
|---|---|
| [`E1-Shear-Reinforcement-Calculation-for-beam.xlsx`](./doc-files/design-excel/E1-Shear-Reinforcement-Calculation-for-beam.xlsx) | Beam stirrups detailing and calculations |
| [`E2-Shear-Reinforcement-Calculation-For-Column.xlsx`](./doc-files/design-excel/E2-Shear-Reinforcement-Calculation-For-Column.xlsx) | Column tie detailing and calculations |
| [`E3-Shear-Wall-Rebar-Calculation-ACI-318-14.xlsx`](./doc-files/design-excel/E3-Shear-Wall-Rebar-Calculation-ACI-318-14.xlsx) | Boundary element and web rebar for shear walls |
| [`E4-1-DL-AND-Lapping-Length.xlsx`](./doc-files/design-excel/E4-1-DL-AND-Lapping-Length.xlsx) | Lapping length for tension and compression reinforcement |
| [`E4-2-DEVELOPMENT-AND-SPLICES-OF-REINFORCEMENT.xlsx`](./doc-files/design-excel/E4-2-DEVELOPMENT-AND-SPLICES-OF-REINFORCEMENT.xlsx) | Detailed rebar development and splices calculations |

### Group F: Estimation & Quantity Takeoff (QTO)
Spreadsheets for calculating material quantity takeoffs and costs.

| File Name | Scope |
|---|---|
| [`F1-Foundation-Estimating-and-Costing.xlsx`](./doc-files/design-excel/F1-Foundation-Estimating-and-Costing.xlsx) | Costing, steel, and concrete quantities for foundations |
| [`F2-Beam-estimation.xlsx`](./doc-files/design-excel/F2-Beam-estimation.xlsx) | Steel and concrete quantity estimation for beams |
