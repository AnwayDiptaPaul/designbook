# pyre-ignore-all-errors
"""Five Complete Building Design Problems.

Each problem exercises: wind load, seismic load, serviceability,
column, beam, shear wall, slab, soil-structure interaction.

Run: cd /home/garylan/Desktop/Codes/AntiGravity/DesignBook/app
     python -m backend.complete_design_problems
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.analysis.opensees_model import OpenSeesModelBuilder # pyre-ignore[21]
from backend.core.loads.wind import WindLoadInput, calculate_wind_loads # pyre-ignore[21]
from backend.core.loads.seismic import SeismicInput, calculate_seismic_loads # pyre-ignore[21]
from backend.core.design.beam import BeamDesign # pyre-ignore[21]
from backend.core.design.column import ColumnDesign # pyre-ignore[21]
from backend.core.design.slab_oneway import OneWaySlabDesign # pyre-ignore[21]
from backend.core.design.slab_twoway import TwoWaySlabDesign # pyre-ignore[21]
from backend.core.design.slab_beamless import FlatPlateDesign # pyre-ignore[21]
from backend.core.design.shear_wall import ShearWallDesign # pyre-ignore[21]
from backend.core.design.footing_isolated import IsolatedFootingDesign # pyre-ignore[21]
from backend.core.design.footing_combined import CombinedFootingDesign # pyre-ignore[21]
from backend.core.design.footing_raft import RaftFoundationDesign # pyre-ignore[21]
from backend.core.design.retaining_wall import RetainingWallDesign, RetainingWallInput # pyre-ignore[21]
from backend.core.design.staircase import StaircaseDesign # pyre-ignore[21]
from backend.core.design.dome import DomeDesign # pyre-ignore[21]
from backend.core.checks.serviceability import ServiceabilityChecks # pyre-ignore[21]
from backend.core.combinations.load_combos import get_standard_combinations, generate_envelope # pyre-ignore[21]
from backend.core.soil.soil_reaction import SoilMechanics # pyre-ignore[21]
from backend.models.member import MemberType # pyre-ignore[21]
from backend.core.design.service import StructuralDesignService # pyre-ignore[21]

LOG = []

def log(msg):
    print(msg)
    LOG.append(msg)

def separator(title):
    log("=" * 70)
    log(title)
    log("=" * 70)


# ═══════════════════════════════════════════════════════════════════════
# PROBLEM 1: 6-STORY RESIDENTIAL BUILDING (Dhaka, Zone II, OMRF)
# ═══════════════════════════════════════════════════════════════════════
def problem_1():
    separator("PROBLEM 1: 6-Story Residential (Dhaka, Zone II, OMRF)")
    
    # 1. LOADS
    n_stories = 6; story_h = 3.0
    grid_x = [0, 5, 10, 15, 20]   # 4 bays @ 5m
    grid_y = [0, 5, 10, 15]       # 3 bays @ 5m
    elevations = [(i+1)*story_h for i in range(n_stories)]
    
    # Wind
    wind_inp = WindLoadInput(
        basic_wind_speed_mps=47.0, exposure_category="B",
        building_width_m=20.0, building_depth_m=15.0,
        floor_elevations_m=elevations, floor_heights_m=[story_h]*n_stories,
    )
    wind = calculate_wind_loads(wind_inp)
    log(f"  Wind Base Shear: {wind.base_shear_kn:.2f} kN")
    log(f"  Wind Overturning Moment: {wind.overturning_moment_knm:.2f} kN-m")
    
    # Seismic
    floor_weight = 20.0 * 15.0 * (8.0 + 3.0) * 1.0  # DL+0.25LL
    seismic_inp = SeismicInput(
        seismic_zone="II", soil_class="SC", occupancy="residential",
        frame_type="OMRF", total_height_m=18.0,
        floor_weights_kn=[floor_weight]*n_stories, floor_elevations_m=elevations,
    )
    seismic = calculate_seismic_loads(seismic_inp)
    log(f"  Seismic Base Shear: {seismic.base_shear_kn:.2f} kN")
    log(f"  Period T: {seismic.T:.3f} s")
    
    # 2. STRUCTURAL MODEL
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    model_data = builder.build_building_model(
        grid_x=[float(x) for x in grid_x], grid_y=[float(y) for y in grid_y], story_heights=[story_h]*n_stories,
        beam_section={"b_mm": 300, "h_mm": 600},
        column_section={"b_mm": 450, "h_mm": 450},
        fc_mpa=25.0, rigid_diaphragm=True,
    )
    log(f"  Model: {model_data['n_nodes']} nodes, {model_data['n_elements']} elements")
    
    # 3. GRAVITY ANALYSIS
    trib_area = 5.0 * 5.0 / 4  # per node
    builder.apply_gravity_loads(model_data["floor_nodes"], 8.0, 3.0, trib_area)
    result = builder.run_full_pipeline(n_modes=6)
    log(f"  Gravity: {result['gravity']['status']}")
    if result["modal"]:
        log(f"  Modal Periods: {[f'{t:.3f}' for t in result['modal']['periods'][:3]]} s")
    
    # 4. MEMBER DESIGN
    
    # Beam
    beam_inputs = {"width": 300.0, "depth": 600.0, "fc": 25.0, "fy": 500.0}
    beam_forces = {"Mu": 180.0, "Vu": 120.0}
    beam_res = StructuralDesignService.design_member(MemberType.BEAM, beam_inputs, beam_forces)
    
    log(f"  Beam Flexure: As={beam_res['flexure']['As_req_mm2']:.0f} mm², {beam_res['flexure']['status']}")
    log(f"  Beam Shear: {beam_res['shear']['status']}")
    
    # Column
    col_inputs = {
        "width": 450.0, "depth": 450.0, "fc": 25.0, "fy": 500.0,
        "rebar_layers": [{"depth": 50, "As": 1200}, {"depth": 400, "As": 1200}]
    }
    col_forces = {"Pu": 1500.0, "Mux": 120.0, "Muy": 90.0, "Vu": 50.0}
    col_res = StructuralDesignService.design_member(MemberType.COLUMN, col_inputs, col_forces)
    
    log(f"  Column Biaxial: {col_res['biaxial_check']['status']}, ratio={col_res['biaxial_check']['ratio']:.3f}")
    
    # One-way slab
    slab_inputs = {"depth": 150.0, "fc": 25.0, "fy": 500.0}
    slab_forces = {"Mu": 12.0}
    slab_res = StructuralDesignService.design_member(MemberType.SLAB_ONEWAY, slab_inputs, slab_forces)
    log(f"  Slab: As={slab_res['slab_oneway']['As_req_mm2_m']:.0f} mm²/m, {slab_res['slab_oneway']['status']}")
    
    # Shear wall
    sw_inputs = {"width": 4000.0, "depth": 200.0, "fc": 25.0, "fy": 500.0}
    sw_forces = {"Vu": 400.0, "Mu": 3000.0, "Pu": 3000.0}
    sw_res = StructuralDesignService.design_member(MemberType.SHEAR_WALL, sw_inputs, sw_forces)
    log(f"  Shear Wall: {sw_res['shear_check']['status']}")
    
    # 5. FOOTING
    ftg_inputs = {"width": 450.0, "depth": 450.0, "fc": 25.0, "fy": 500.0, "q_allow": 150.0}
    ftg_forces = {"Pu": 1500.0, "Mu": 50.0, "Vu": 30.0}
    ftg_res = StructuralDesignService.design_member(MemberType.FOOTING_ISOLATED, ftg_inputs, ftg_forces)
    ftg_data = ftg_res['footing']
    log(f"  Footing: {ftg_data.get('L_m', 0):.2f}m x {ftg_data.get('B_m', 0):.2f}m, q_max={ftg_data.get('q_max_kPa', 0):.1f} kPa")
    
    # 6. SERVICEABILITY
    drift = ServiceabilityChecks.check_story_drift(5.0, 3000, 5.0, 1.0, 0.020)
    defl = ServiceabilityChecks.check_deflection(60.0, 40.0, 1.5e9, 8e8, 3.0)
    crack = ServiceabilityChecks.check_crack_width(280, 50, 150)
    log(f"  Story Drift: {drift['status']}, ratio={drift['drift_ratio']:.4f}")
    log(f"  Deflection: LT={defl['delta_long_term_mm']:.2f} mm")
    log(f"  Crack Control: {crack['status']}")
    
    log("  PROBLEM 1 COMPLETED SUCCESSFULLY.\n")


# ═══════════════════════════════════════════════════════════════════════
# PROBLEM 2: 10-STORY COMMERCIAL OFFICE (Chittagong, Zone III, IMRF)
# ═══════════════════════════════════════════════════════════════════════
def problem_2():
    separator("PROBLEM 2: 10-Story Commercial Office (Chittagong, Zone III, IMRF)")
    
    n_stories = 10; story_h = 3.5
    grid_x = [0, 6, 12, 18, 24, 30]  # 5 bays @ 6m
    grid_y = [0, 6, 12, 18, 24]       # 4 bays @ 6m
    elevations = [(i+1)*story_h for i in range(n_stories)]
    
    # Wind
    wind = calculate_wind_loads(WindLoadInput(
        basic_wind_speed_mps=60.0, exposure_category="C",
        building_width_m=30.0, building_depth_m=24.0,
        floor_elevations_m=elevations, floor_heights_m=[story_h]*n_stories,
    ))
    log(f"  Wind Base Shear: {wind.base_shear_kn:.2f} kN")
    
    # Seismic
    floor_w = 30.0 * 24.0 * 10.0
    seismic = calculate_seismic_loads(SeismicInput(
        seismic_zone="III", soil_class="SD", occupancy="commercial",
        frame_type="IMRF", total_height_m=35.0,
        floor_weights_kn=[floor_w]*n_stories, floor_elevations_m=elevations,
    ))
    log(f"  Seismic Base Shear: {seismic.base_shear_kn:.2f} kN, T={seismic.T:.3f} s")
    
    # Model
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    model = builder.build_building_model(
        [float(x) for x in grid_x], [float(y) for y in grid_y], [story_h]*n_stories,
        beam_section={"b_mm": 400, "h_mm": 700},
        column_section={"b_mm": 600, "h_mm": 600},
        fc_mpa=30.0, use_pdelta=True, rigid_diaphragm=True,
    )
    log(f"  Model: {model['n_nodes']} nodes, {model['n_elements']} elements")
    
    trib = 6.0 * 6.0 / 4.0
    builder.apply_gravity_loads(model["floor_nodes"], 10.0, 5.0, trib)
    result = builder.run_full_pipeline(n_modes=12)
    log(f"  Gravity: {result['gravity']['status']}")
    if result["modal"]:
        log(f"  Periods: {[f'{p:.3f}' for p in result['modal']['periods'][:3]]} s")
    
    # Design
    beam_inputs = {"width": 400.0, "depth": 700.0, "fc": 30.0, "fy": 500.0}
    beam_forces = {"Mu": 350.0}
    beam_res = StructuralDesignService.design_member(MemberType.BEAM, beam_inputs, beam_forces)
    log(f"  Beam: As={beam_res['flexure']['As_req_mm2']:.0f} mm², {beam_res['flexure']['status']}")
    
    col_inputs = {
        "width": 600.0, "depth": 600.0, "fc": 30.0, "fy": 500.0,
        "rebar_layers": [{"depth": 60, "As": 2000}, {"depth": 540, "As": 2000}]
    }
    col_forces = {"Pu": 2500.0, "Mux": 300.0, "Muy": 150.0}
    col_res = StructuralDesignService.design_member(MemberType.COLUMN, col_inputs, col_forces)
    log(f"  Column PM: {len(col_res['interaction_diagram']['points'])} points generated")
    
    tw_slab_inputs = {"depth": 175.0, "fc": 30.0, "fy": 500.0}
    tw_slab_forces = {"Mu_x": 25.0, "Mu_y": 18.0}
    tw_slab_res = StructuralDesignService.design_member(MemberType.SLAB_TWOWAY, tw_slab_inputs, tw_slab_forces)
    log(f"  Two-Way Slab: As_x={tw_slab_res['slab_twoway']['As_x_req_mm2_m']:.0f}, As_y={tw_slab_res['slab_twoway']['As_y_req_mm2_m']:.0f} mm²/m")
    
    sw_inputs = {"width": 3000.0, "depth": 250.0, "fc": 30.0, "fy": 500.0}
    sw_forces = {"Vu": 800.0, "Mu": 35000.0, "Pu": 4000.0}
    sw_res = StructuralDesignService.design_member(MemberType.SHEAR_WALL, sw_inputs, sw_forces)
    log(f"  Core Shear Wall: {sw_res['shear_check']['status']}")
    
    # Raft
    raft_inputs = {"depth": 800.0, "fc": 30.0, "fy": 500.0}
    raft_forces = {"Mu_x": 180.0, "Mu_y": 120.0}
    raft_res = StructuralDesignService.design_member(MemberType.FOOTING_RAFT, raft_inputs, raft_forces)
    log(f"  Raft: As_x={raft_res['raft_flexure']['As_x_req_mm2_m']:.0f}, As_y={raft_res['raft_flexure']['As_y_req_mm2_m']:.0f} mm²/m")
    
    # Envelope
    demo_forces = {
        "U1": {"M": 200.0, "V": 80.0, "P": -1800.0}, "U2": {"M": 350.0, "V": 120.0, "P": -2200.0},
        "U6a": {"M": 280.0, "V": 150.0, "P": -1500.0}, "U7a": {"M": 180.0, "V": 100.0, "P": -800.0},
    }
    env = generate_envelope(demo_forces)
    log(f"  Envelope M_max: {env.get('M_max', {}).get('value', 0):.0f} kN-m ({env.get('M_max', {}).get('combo', '')})")
    
    log("  PROBLEM 2 COMPLETED SUCCESSFULLY.\n")


# ═══════════════════════════════════════════════════════════════════════
# PROBLEM 3: 4-STORY HOSPITAL (Essential, Zone IV, SMRF)
# ═══════════════════════════════════════════════════════════════════════
def problem_3():
    separator("PROBLEM 3: 4-Story Hospital (Essential, Zone IV, SMRF)")
    
    n_stories = 4; story_h = 4.0
    grid_x = [0, 7, 14, 21, 28, 35, 42]
    grid_y = [0, 7, 14, 21, 28]
    elevations = [(i+1)*story_h for i in range(n_stories)]
    
    wind = calculate_wind_loads(WindLoadInput(
        basic_wind_speed_mps=55.0, exposure_category="B",
        building_width_m=42.0, building_depth_m=28.0,
        floor_elevations_m=elevations, floor_heights_m=[story_h]*n_stories,
    ))
    log(f"  Wind Base Shear: {wind.base_shear_kn:.2f} kN")
    
    floor_w = 42.0 * 28.0 * 12.0
    seismic = calculate_seismic_loads(SeismicInput(
        seismic_zone="IV", soil_class="SC", occupancy="essential",
        frame_type="SMRF", total_height_m=16.0,
        floor_weights_kn=[floor_w]*n_stories, floor_elevations_m=elevations,
    ))
    log(f"  Seismic Base Shear: {seismic.base_shear_kn:.2f} kN (I=1.5)")
    
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    model = builder.build_building_model(
        [float(x) for x in grid_x], [float(y) for y in grid_y], [story_h]*n_stories,
        beam_section={"b_mm": 400, "h_mm": 800},
        column_section={"b_mm": 700, "h_mm": 700},
        fc_mpa=35.0, rigid_diaphragm=True,
    )
    log(f"  Model: {model['n_nodes']} nodes, {model['n_elements']} elements")
    
    trib = 7.0 * 7.0 / 4.0
    builder.apply_gravity_loads(model["floor_nodes"], 10.0, 4.0, trib)
    result = builder.run_full_pipeline(n_modes=12)
    log(f"  Gravity: {result['gravity']['status']}")
    if result["modal"]:
        log(f"  Periods: {[f'{p:.3f}' for p in result['modal']['periods'][:3]]} s")
    
    # Beam
    beam_inputs = {"width": 400.0, "depth": 800.0, "fc": 35.0, "fy": 500.0}
    beam_forces = {"Mu": 500.0}
    beam_res = StructuralDesignService.design_member(MemberType.BEAM, beam_inputs, beam_forces)
    log(f"  Beam: As={beam_res['flexure']['As_req_mm2']:.0f} mm², {beam_res['flexure']['status']}")
    
    # Column
    col_inputs = {
        "width": 700.0, "depth": 700.0, "fc": 35.0, "fy": 500.0,
        "rebar_layers": [{"depth": 60, "As": 3000}, {"depth": 640, "As": 3000}]
    }
    col_forces = {"Pu": 4000.0, "Mux": 400.0, "Muy": 300.0}
    col_res = StructuralDesignService.design_member(MemberType.COLUMN, col_inputs, col_forces)
    log(f"  Column Biaxial: {col_res['biaxial_check']['status']}, ratio={col_res['biaxial_check']['ratio']:.3f}")
    
    # Flat slab with punching
    fp_inputs = {"depth": 170.0, "fc": 35.0, "width": 700.0, "depth_col": 700.0, "cover": 50.0}
    fp_forces = {"Vu": 800.0}
    fp_res = StructuralDesignService.design_member(MemberType.SLAB_BEAMLESS, fp_inputs, fp_forces)
    log(f"  Punching Shear: {fp_res['punching_shear']['status']}, Vu/phiVc={800/fp_res['punching_shear']['phi_Vc_kN']:.2f}")
    
    # Shear wall
    sw_inputs = {"width": 5000.0, "depth": 300.0, "fc": 35.0, "fy": 500.0}
    sw_forces = {"Vu": 1200.0, "Mu": 16000.0, "Pu": 4000.0}
    sw_res = StructuralDesignService.design_member(MemberType.SHEAR_WALL, sw_inputs, sw_forces)
    log(f"  Shear Wall: {sw_res['shear_check']['status']}")
    
    # Combined footing
    cf_inputs = {"fc": 35.0, "fy": 500.0, "q_allow": 200.0, "c_c_dist": 5.0} # use correct Pydantic field name
    cf_forces = {"P1": 2000.0, "P2": 2800.0} # use correct Pydantic field name
    cf_res = StructuralDesignService.design_member(MemberType.FOOTING_COMBINED, cf_inputs, cf_forces)
    cf_data = cf_res['combined_footing']
    log(f"  Combined Footing: {cf_data['L_m']:.2f}m x {cf_data['B_m']:.2f}m")
    
    # Staircase
    stair_inputs = {"going": 3.0, "rise": 150.0, "tread": 300.0, "width": 1200.0, "fc": 35.0, "fy": 500.0}
    stair_forces = {"LL": 5.0}
    stair_res = StructuralDesignService.design_member(MemberType.STAIRCASE, stair_inputs, stair_forces)
    stair_data = stair_res['staircase']
    log(f"  Staircase: waist={stair_data['waist_slab_t_mm']:.0f}mm, As={stair_data['As_req_mm2_m']:.0f} mm²/m")
    
    # Serviceability
    drift = ServiceabilityChecks.check_story_drift(8.0, 4000, 5.5, 1.5, 0.010)
    log(f"  Story Drift: {drift['status']}, ratio={drift['drift_ratio']:.5f}")
    
    log("  PROBLEM 3 COMPLETED SUCCESSFULLY.\n")


# ═══════════════════════════════════════════════════════════════════════
# PROBLEM 4: 8-STORY MIXED-USE + BASEMENT (Zone II, IMRF)
# ═══════════════════════════════════════════════════════════════════════
def problem_4():
    separator("PROBLEM 4: 8-Story Mixed-Use + Basement (Zone II, IMRF)")
    
    n_stories = 8; story_h = 3.2; basement_h = 4.0
    grid_x = [0, 5.5, 11, 16.5, 22]
    grid_y = [0, 5.5, 11, 16.5]
    elevations = [-basement_h] + [(i+1)*story_h for i in range(n_stories)]
    above_ground_elev = [(i+1)*story_h for i in range(n_stories)]
    
    wind = calculate_wind_loads(WindLoadInput(
        basic_wind_speed_mps=47.0, exposure_category="B",
        building_width_m=22.0, building_depth_m=16.5,
        floor_elevations_m=above_ground_elev, floor_heights_m=[story_h]*n_stories,
    ))
    log(f"  Wind Base Shear: {wind.base_shear_kn:.2f} kN")
    
    floor_w = 22.0 * 16.5 * 9.5
    seismic = calculate_seismic_loads(SeismicInput(
        seismic_zone="II", soil_class="SD", occupancy="mixed",
        frame_type="IMRF", total_height_m=n_stories*story_h,
        floor_weights_kn=[floor_w]*n_stories, floor_elevations_m=above_ground_elev,
    ))
    log(f"  Seismic Base Shear: {seismic.base_shear_kn:.2f} kN")
    
    # Model (above ground only for simplicity)
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    model = builder.build_building_model(
        [float(x) for x in grid_x], [float(y) for y in grid_y], [story_h]*n_stories,
        beam_section={"b_mm": 350, "h_mm": 650},
        column_section={"b_mm": 500, "h_mm": 500},
        fc_mpa=28.0, use_pdelta=True, rigid_diaphragm=True,
    )
    log(f"  Model: {model['n_nodes']} nodes, {model['n_elements']} elements")
    
    trib = 5.5 * 5.5 / 4.0
    builder.apply_gravity_loads(model["floor_nodes"], 9.0, 4.0, trib)
    result = builder.run_full_pipeline(n_modes=8)
    log(f"  Gravity: {result['gravity']['status']}")
    if result["modal"]:
        log(f"  Periods: {[f'{p:.3f}' for p in result['modal']['periods'][:3]]} s")
    
    # Retaining wall (basement)
    rw_inp = {"height": 4.0, "soil_gamma": 18.0, "soil_phi": 28.0, "surcharge": 12.0, "water_table_depth": 2.5}
    rw_res = StructuralDesignService.design_member(MemberType.RETAINING_WALL, rw_inp, {})
    pressures = rw_res["lateral_pressures"]
    max_p = max(p["pressure_kpa"] for p in pressures)
    log(f"  Basement Wall: max lateral pressure={max_p:.1f} kPa")
    
    # Design members
    beam_inputs = {"width": 350.0, "depth": 650.0, "fc": 28.0, "fy": 500.0}
    beam_forces = {"Mu": 250.0, "Vu": 150.0}
    beam_res = StructuralDesignService.design_member(MemberType.BEAM, beam_inputs, beam_forces)
    log(f"  Beam: As={beam_res['flexure']['As_req_mm2']:.0f} mm², {beam_res['flexure']['status']}")
    
    col_inputs = {
        "width": 500.0, "depth": 500.0, "fc": 28.0, "fy": 500.0,
        "rebar_layers": [{"depth": 50, "As": 1600}, {"depth": 450, "As": 1600}]
    }
    col_forces = {"Pu": 2500.0, "Mux": 200.0, "Muy": 150.0}
    col_res = StructuralDesignService.design_member(MemberType.COLUMN, col_inputs, col_forces)
    log(f"  Column Biaxial: {col_res['biaxial_check']['status']}, ratio={col_res['biaxial_check']['ratio']:.3f}")
    
    sw_inputs = {"width": 1500.0, "depth": 200.0, "fc": 28.0, "fy": 500.0}
    sw_forces = {"Vu": 600.0, "Mu": 3200.0 * 8, "Pu": 2000.0} # approximated
    sw_res = StructuralDesignService.design_member(MemberType.SHEAR_WALL, sw_inputs, sw_forces)
    log(f"  Shear Wall: {sw_res['shear_check']['status']}")
    
    ow_slab_inputs = {"depth": 150.0, "fc": 28.0, "fy": 500.0}
    ow_slab_forces = {"Mu": 15.0}
    ow_slab_res = StructuralDesignService.design_member(MemberType.SLAB_ONEWAY, ow_slab_inputs, ow_slab_forces)
    log(f"  One-Way Slab: As={ow_slab_res['slab_oneway']['As_req_mm2_m']:.0f} mm²/m")
    
    # Soil
    Ka = SoilMechanics.calculate_active_earth_pressure_coefficient(28)
    K0 = SoilMechanics.calculate_at_rest_earth_pressure_coefficient(28)
    log(f"  Earth Pressure: Ka={Ka:.3f}, K0={K0:.3f}")
    
    # Isolated footings
    ftg_inputs = {"fc": 28.0, "fy": 500.0, "q_allow": 180.0}
    ftg_forces = {"P": 2500.0, "Mx": 80.0, "My": 0.0}
    ftg_res = StructuralDesignService.design_member(MemberType.FOOTING_ISOLATED, ftg_inputs, ftg_forces)
    ftg = ftg_res['footing']
    log(f"  Footing: {ftg.get('L_m', 0):.2f}m x {ftg.get('B_m', 0):.2f}m")
    
    # Vibration
    vib = ServiceabilityChecks.check_floor_vibration(5.5, 25e9, 2.7e-3, 500)
    log(f"  Floor Vibration: {vib['status']}, fn={vib['fundamental_frequency_Hz']:.2f} Hz")
    
    log("  PROBLEM 4 COMPLETED SUCCESSFULLY.\n")


# ═══════════════════════════════════════════════════════════════════════
# PROBLEM 5: 12-STORY HIGH-RISE COMMERCIAL (Zone III, SMRF, Raft)
# ═══════════════════════════════════════════════════════════════════════
def problem_5():
    separator("PROBLEM 5: 12-Story High-Rise Commercial (Zone III, SMRF, Raft)")
    
    n_stories = 12; story_h = 3.5
    grid_x = [0, 6, 12, 18, 24, 30]
    grid_y = [0, 6, 12, 18, 24, 30]
    elevations = [(i+1)*story_h for i in range(n_stories)]
    
    wind = calculate_wind_loads(WindLoadInput(
        basic_wind_speed_mps=60.0, exposure_category="C",
        building_width_m=30.0, building_depth_m=30.0,
        floor_elevations_m=elevations, floor_heights_m=[story_h]*n_stories,
    ))
    log(f"  Wind Base Shear: {wind.base_shear_kn:.2f} kN")
    
    floor_w = 30.0 * 30.0 * 11.0
    seismic = calculate_seismic_loads(SeismicInput(
        seismic_zone="III", soil_class="SE", occupancy="commercial",
        frame_type="SMRF", total_height_m=42.0,
        floor_weights_kn=[floor_w]*n_stories, floor_elevations_m=elevations,
    ))
    log(f"  Seismic Base Shear: {seismic.base_shear_kn:.2f} kN, T={seismic.T:.3f} s")
    
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    model = builder.build_building_model(
        [float(x) for x in grid_x], [float(y) for y in grid_y], [story_h]*n_stories,
        beam_section={"b_mm": 450, "h_mm": 750},
        column_section={"b_mm": 700, "h_mm": 700},
        fc_mpa=35.0, use_pdelta=True, rigid_diaphragm=True,
    )
    log(f"  Model: {model['n_nodes']} nodes, {model['n_elements']} elements")
    
    trib = 6.0 * 6.0 / 4.0
    builder.apply_gravity_loads(model["floor_nodes"], 11.0, 5.0, trib)
    
    # Apply lateral forces from seismic
    story_forces = [sf.force_kn for sf in seismic.story_forces]
    builder.apply_lateral_forces(model["floor_nodes"], story_forces, "X", ts_tag=3, pattern_tag=3)
    
    result = builder.run_full_pipeline(n_modes=12)
    log(f"  Gravity: {result['gravity']['status']}")
    if result["modal"]:
        log(f"  Periods: {[f'{p:.3f}' for p in result['modal']['periods'][:3]]} s")
    
    # Extract story drifts
    drifts = builder.extract_story_drifts(
        model["floor_nodes"], model["floor_elevations"], "X"
    )
    max_drift = max(d["drift_ratio"] for d in drifts) if drifts else 0
    log(f"  Max Story Drift Ratio: {max_drift:.6f}")
    
    # Extract member forces for a sample beam
    if model["beam_tags"]:
        sample_forces = builder.extract_member_forces(model["beam_tags"][:3])
        for tag, f in sample_forces.items():
            if "error" not in f:
                log(f"  Beam {tag}: M_i={f.get('Mzi', 0):.2f} kN-m, V_i={f.get('Vyi', 0):.2f} kN")
    
    # Design members
    beam_inputs = {"width": 450.0, "depth": 750.0, "fc": 35.0, "fy": 500.0}
    beam_forces = {"Mu": 450.0}
    beam_res = StructuralDesignService.design_member(MemberType.BEAM, beam_inputs, beam_forces)
    log(f"  Beam: As={beam_res['flexure']['As_req_mm2']:.0f} mm², {beam_res['flexure']['status']}")
    
    col_inputs = {
        "width": 700.0, "depth": 700.0, "fc": 35.0, "fy": 500.0,
        "rebar_layers": [{"depth": 60, "As": 4000}, {"depth": 640, "As": 4000}],
        "klu_over_r": 45.0 # slender
    }
    col_forces = {"Pu": 6000.0, "Mux": 500.0, "Muy": 400.0}
    col_res = StructuralDesignService.design_member(MemberType.COLUMN, col_inputs, col_forces)
    log(f"  Column: {col_res['biaxial_check']['status']}, ratio={col_res['biaxial_check']['ratio']:.3f}")
    
    # Slenderness check (manual check for logging purposes as it isn't in service yet)
    slender = ColumnDesign.check_slenderness(45.0, 200.0, 500.0, is_sway=True)
    log(f"  Slender Column: {'Can ignore' if slender else 'Must magnify moments'}")
    
    # Two-way slab
    tw_slab_inputs = {"depth": 200.0, "fc": 35.0, "fy": 500.0}
    tw_slab_forces = {"Mu_x": 35.0, "Mu_y": 25.0}
    tw_slab_res = StructuralDesignService.design_member(MemberType.SLAB_TWOWAY, tw_slab_inputs, tw_slab_forces)
    log(f"  Two-Way Slab: As_x={tw_slab_res['slab_twoway']['As_x_req_mm2_m']:.0f} mm²/m")
    
    sw_inputs = {"width": 8000.0, "depth": 300.0, "fc": 35.0, "fy": 500.0}
    sw_forces = {"Vu": 1500.0, "Mu": 42000.0, "Pu": 5000.0}
    sw_res = StructuralDesignService.design_member(MemberType.SHEAR_WALL, sw_inputs, sw_forces)
    log(f"  Shear Wall: {sw_res['shear_check']['status']}")
    
    # Raft
    raft_inputs = {"depth": 1000.0, "fc": 35.0, "fy": 500.0}
    raft_forces = {"Mu_x": 250.0, "Mu_y": 180.0}
    raft_res = StructuralDesignService.design_member(MemberType.FOOTING_RAFT, raft_inputs, raft_forces)
    log(f"  Raft: As_x={raft_res['raft_flexure']['As_x_req_mm2_m']:.0f}, As_y={raft_res['raft_flexure']['As_y_req_mm2_m']:.0f} mm²/m")
    
    # Soil
    Ks = SoilMechanics.calculate_winkler_spring_stiffness(100, 3.0, 0.025)
    log(f"  Winkler Spring Ks: {Ks:.0f} kN/m³")
    q_ult = SoilMechanics.calculate_bearing_capacity(0, 18*2, 18, 30, 5.7, 1.0, 0.0)
    log(f"  Bearing Capacity q_ult: {q_ult:.0f} kPa")
    
    # Serviceability
    drift_check = ServiceabilityChecks.check_story_drift(12.0, 3500, 5.5, 1.0, 0.020)
    log(f"  Drift Check: {drift_check['status']}, ratio={drift_check['drift_ratio']:.4f}")
    
    # Dome (if top of building has a dome feature)
    dome_inputs = {"radius": 15.0, "thickness": 0.15, "theta_edge_deg": 45.0}
    dome_forces = {"DL": 4.0, "LL": 0.5}
    dome_res = StructuralDesignService.design_member(MemberType.DOME, dome_inputs, dome_forces)
    dome_data = dome_res['dome']
    log(f"  Dome: N_phi={dome_data['meridional_force_N_phi_kN_m']:.1f} kN/m, Ring As={dome_data['As_ring_beam_mm2']:.0f} mm²")
    
    log("  PROBLEM 5 COMPLETED SUCCESSFULLY.\n")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════
import multiprocessing
import traceback

def run_problem_isolated(prob_func, result_queue):
    """Runs a single design problem in an isolated process to prevent OpenSees hard crashes."""
    global LOG
    try:
        # Clear log for this isolated process
        LOG.clear()
        
        prob_func()
        
        # Pass the local logs and success status back
        result_queue.put({"success": True, "logs": list(LOG)})
    except Exception as e:
        # Capture error and trace
        error_info = traceback.format_exc()
        result_queue.put({"success": False, "error": str(e), "trace": error_info, "logs": list(LOG)})

if __name__ == "__main__":
    log("=" * 70)
    log("FIVE COMPLETE BUILDING DESIGN PROBLEMS")
    log("Running through main app core modules with Multiprocessing Isolation")
    log("=" * 70 + "\n")
    
    problems = [problem_1, problem_2, problem_3, problem_4, problem_5]
    passed: int = 0
    all_logs = []
    
    for i, prob in enumerate(problems, 1):
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=run_problem_isolated, args=(prob, q))
        p.start()
        p.join()
        
        # Check if process terminated abnormally (OpenSees exit/segfault)
        if p.exitcode != 0 and p.exitcode is not None:
            # The queue might be empty if it crashed severely
            log(f"  PROBLEM {i} ({prob.__name__}) FAILED: OpenSees Hard Crash / Process Terminated (Exit Code {p.exitcode})\n")
            all_logs.append(f"PROBLEM {i} HARD CRASH (Exit Code {p.exitcode})\n")
        else:
            if not q.empty():
                res = q.get()
                # Store logs from the child process
                all_logs.extend(res.get("logs", []))
                
                if res["success"]:
                    passed += 1 # pyre-ignore[58]
                else:
                    log(f"  PROBLEM {i} ({prob.__name__}) FAILED: {res.get('error')}\n")
                    all_logs.append(res.get('trace', ''))
            else:
                log(f"  PROBLEM {i} ({prob.__name__}) FAILED: Process terminated without results.\n")
                all_logs.append(f"PROBLEM {i} SILENT CRASH\n")
    
    log("=" * 70)
    log(f"RESULTS: {passed}/5 problems completed successfully.")
    log("=" * 70)
    
    # Save to log
    import os
    log_path = os.path.join(os.path.dirname(__file__), "batch_stress_test.log")
    with open(log_path, "a") as f:
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("COMPLETE DESIGN PROBLEMS (5 BUILDINGS)\n")
        f.write("=" * 70 + "\n")
        for line in all_logs:
            f.write(line + "\n")
        f.write(f"RESULTS: {passed}/5 problems completed successfully.\n")
