"""Five Complete Building Design Problems.

Each problem exercises: wind load, seismic load, serviceability,
column, beam, shear wall, slab, soil-structure interaction.

Run: cd /home/garylan/Desktop/Codes/AntiGravity/DesignBook/app
     python -m backend.complete_design_problems
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.analysis.opensees_model import OpenSeesModelBuilder
from backend.core.loads.wind import WindLoadInput, calculate_wind_loads
from backend.core.loads.seismic import SeismicInput, calculate_seismic_loads
from backend.core.design.beam import BeamDesign
from backend.core.design.column import ColumnDesign
from backend.core.design.slab_oneway import OneWaySlabDesign
from backend.core.design.slab_twoway import TwoWaySlabDesign
from backend.core.design.slab_beamless import FlatPlateDesign
from backend.core.design.shear_wall import ShearWallDesign
from backend.core.design.footing_isolated import IsolatedFootingDesign
from backend.core.design.footing_combined import CombinedFootingDesign
from backend.core.design.footing_raft import RaftFoundationDesign
from backend.core.design.retaining_wall import RetainingWallDesign, RetainingWallInput
from backend.core.design.staircase import StaircaseDesign
from backend.core.design.dome import DomeDesign
from backend.core.checks.serviceability import ServiceabilityChecks
from backend.core.combinations.load_combos import get_standard_combinations, generate_envelope
from backend.core.soil.soil_reaction import SoilMechanics

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
        grid_x=grid_x, grid_y=grid_y, story_heights=[story_h]*n_stories,
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
    beam_flex = BeamDesign.design_flexure(180.0, 300, 540, 25, 500)
    beam_shear = BeamDesign.design_shear(120.0, 300, 540, 25, 500)
    log(f"  Beam Flexure: As={beam_flex['As_req_mm2']:.0f} mm², {beam_flex['status']}")
    log(f"  Beam Shear: {beam_shear['status']}")
    
    # Column
    col_diag = ColumnDesign.generate_interaction_diagram(
        450, 450, 25, 500, [{"depth": 50, "As": 1200}, {"depth": 400, "As": 1200}]
    )
    col_biax = ColumnDesign.check_biaxial_capacity(
        1500, 120, 90, col_diag["points"], col_diag["points"]
    )
    log(f"  Column Biaxial: {col_biax['status']}, ratio={col_biax['ratio']:.3f}")
    
    # One-way slab
    slab = OneWaySlabDesign.design_flexure(12.0, 150, 25, 500)
    log(f"  Slab: As={slab['As_req_mm2_m']:.0f} mm²/m, {slab['status']}")
    
    # Shear wall
    sw = ShearWallDesign.design_shear(400, 200, 3000, 3000, 200, 25, 500)
    log(f"  Shear Wall: {sw['status']}")
    
    # 5. FOOTING
    ftg = IsolatedFootingDesign.design(1500, 50, 30, 150, 25, 500)
    log(f"  Footing: {ftg.get('L_m', 0):.2f}m x {ftg.get('B_m', 0):.2f}m, q_max={ftg.get('q_max_kPa', 0):.1f} kPa")
    
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
        grid_x, grid_y, [story_h]*n_stories,
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
    beam_f = BeamDesign.design_flexure(350, 400, 640, 30, 500)
    log(f"  Beam: As={beam_f['As_req_mm2']:.0f} mm², {beam_f['status']}")
    
    col_d = ColumnDesign.generate_interaction_diagram(600, 600, 30, 500,
        [{"depth": 60, "As": 2000}, {"depth": 540, "As": 2000}])
    log(f"  Column PM: {len(col_d['points'])} points generated")
    
    tw_slab = TwoWaySlabDesign.design_flexure_fea(25, 18, 175, 30, 500)
    log(f"  Two-Way Slab: As_x={tw_slab['As_x_req_mm2_m']:.0f}, As_y={tw_slab['As_y_req_mm2_m']:.0f} mm²/m")
    
    sw_s = ShearWallDesign.design_shear(800, 3000, 4000, 35000, 250, 30, 500)
    log(f"  Core Shear Wall: {sw_s['status']}")
    
    # Raft
    raft = RaftFoundationDesign.design_flexure_fea(180, 120, 800, 30, 500)
    log(f"  Raft: As_x={raft['As_x_req_mm2_m']:.0f}, As_y={raft['As_y_req_mm2_m']:.0f} mm²/m")
    
    # Envelope
    demo_forces = {
        "U1": {"M": 200, "V": 80, "P": -1800}, "U2": {"M": 350, "V": 120, "P": -2200},
        "U6a": {"M": 280, "V": 150, "P": -1500}, "U7a": {"M": 180, "V": 100, "P": -800},
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
        grid_x, grid_y, [story_h]*n_stories,
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
    beam = BeamDesign.design_flexure(500, 400, 740, 35, 500)
    log(f"  Beam: As={beam['As_req_mm2']:.0f} mm², {beam['status']}")
    
    # Column
    col_d = ColumnDesign.generate_interaction_diagram(700, 700, 35, 500,
        [{"depth": 60, "As": 3000}, {"depth": 640, "As": 3000}])
    biax = ColumnDesign.check_biaxial_capacity(4000, 400, 300, col_d["points"], col_d["points"])
    log(f"  Column Biaxial: {biax['status']}, ratio={biax['ratio']:.3f}")
    
    # Flat slab with punching
    punch = FlatPlateDesign.check_punching_shear(800, 50, 700, 700, 170, 35)
    log(f"  Punching Shear: {punch['status']}, Vu/phiVc={800/punch['phi_Vc_kN']:.2f}")
    
    # Shear wall
    sw = ShearWallDesign.design_shear(1200, 5000, 4000, 16000, 300, 35, 500)
    log(f"  Shear Wall: {sw['status']}")
    
    # Combined footing
    cf = CombinedFootingDesign.design(2000, 2800, 5.0, 200, 35, 500)
    log(f"  Combined Footing: {cf['L_m']:.2f}m x {cf['B_m']:.2f}m")
    
    # Staircase
    stair = StaircaseDesign.design(3.0, 150, 300, 1200, 5.0, 35, 500)
    log(f"  Staircase: waist={stair['waist_slab_t_mm']:.0f}mm, As={stair['As_req_mm2_m']:.0f} mm²/m")
    
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
        grid_x, grid_y, [story_h]*n_stories,
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
    rw_inp = RetainingWallInput(height_m=4.0, soil_gamma=18.0, soil_phi=28.0, surcharge_kpa=12.0, water_table_depth_m=2.5)
    pressures = RetainingWallDesign.calculate_lateral_pressures(rw_inp)
    max_p = max(p["pressure_kpa"] for p in pressures)
    log(f"  Basement Wall: max lateral pressure={max_p:.1f} kPa")
    
    # Design members
    beam = BeamDesign.design_flexure(250, 350, 590, 28, 500)
    beam_v = BeamDesign.design_shear(150, 350, 590, 28, 500)
    log(f"  Beam: As={beam['As_req_mm2']:.0f} mm², {beam['status']}")
    
    col = ColumnDesign.generate_interaction_diagram(500, 500, 28, 500,
        [{"depth": 50, "As": 1600}, {"depth": 450, "As": 1600}])
    biax = ColumnDesign.check_biaxial_capacity(2500, 200, 150, col["points"], col["points"])
    log(f"  Column Biaxial: {biax['status']}, ratio={biax['ratio']:.3f}")
    
    sw = ShearWallDesign.design_shear(600, 1500, 3000, 3200*8, 200, 28, 500)
    log(f"  Shear Wall: {sw['status']}")
    
    ow_slab = OneWaySlabDesign.design_flexure(15, 150, 28, 500)
    log(f"  One-Way Slab: As={ow_slab['As_req_mm2_m']:.0f} mm²/m")
    
    # Soil
    Ka = SoilMechanics.calculate_active_earth_pressure_coefficient(28)
    K0 = SoilMechanics.calculate_at_rest_earth_pressure_coefficient(28)
    log(f"  Earth Pressure: Ka={Ka:.3f}, K0={K0:.3f}")
    
    # Isolated footings
    ftg = IsolatedFootingDesign.design(2500, 100, 80, 180, 28, 500)
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
        grid_x, grid_y, [story_h]*n_stories,
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
    beam = BeamDesign.design_flexure(450, 450, 690, 35, 500)
    log(f"  Beam: As={beam['As_req_mm2']:.0f} mm², {beam['status']}")
    
    col_d = ColumnDesign.generate_interaction_diagram(700, 700, 35, 500,
        [{"depth": 60, "As": 4000}, {"depth": 640, "As": 4000}])
    biax = ColumnDesign.check_biaxial_capacity(6000, 500, 400, col_d["points"], col_d["points"])
    log(f"  Column: {biax['status']}, ratio={biax['ratio']:.3f}")
    
    # Slenderness
    slender = ColumnDesign.check_slenderness(45, 200, 500, is_sway=True)
    log(f"  Slender Column: {'Can ignore' if slender else 'Must magnify moments'}")
    if not slender:
        Mu_mag = ColumnDesign.magnify_moments(500, 6000, 700, 700, 35, 45)
        log(f"  Magnified Mu: {Mu_mag:.1f} kN-m")
    
    # Two-way slab
    tw = TwoWaySlabDesign.design_flexure_fea(35, 25, 200, 35, 500)
    log(f"  Two-Way Slab: As_x={tw['As_x_req_mm2_m']:.0f} mm²/m")
    
    # Shear wall
    sw = ShearWallDesign.design_shear(1500, 8000, 5000, 42000, 300, 35, 500)
    log(f"  Shear Wall: {sw['status']}")
    
    # Raft
    raft = RaftFoundationDesign.design_flexure_fea(250, 180, 1000, 35, 500)
    log(f"  Raft: As_x={raft['As_x_req_mm2_m']:.0f}, As_y={raft['As_y_req_mm2_m']:.0f} mm²/m")
    
    # Soil
    Ks = SoilMechanics.calculate_winkler_spring_stiffness(100, 3.0, 0.025)
    log(f"  Winkler Spring Ks: {Ks:.0f} kN/m³")
    q_ult = SoilMechanics.calculate_bearing_capacity(0, 18*2, 18, 30, 5.7, 1.0, 0.0)
    log(f"  Bearing Capacity q_ult: {q_ult:.0f} kPa")
    
    # Serviceability
    drift_check = ServiceabilityChecks.check_story_drift(12.0, 3500, 5.5, 1.0, 0.020)
    log(f"  Drift Check: {drift_check['status']}, ratio={drift_check['drift_ratio']:.4f}")
    
    # Dome (if top of building has a dome feature)
    dome = DomeDesign.calculate_membrane_forces(15.0, 0.15, 4.0, 0.5, 45)
    log(f"  Dome: N_phi={dome['meridional_force_N_phi_kN_m']:.1f} kN/m, Ring As={dome['As_ring_beam_mm2']:.0f} mm²")
    
    log("  PROBLEM 5 COMPLETED SUCCESSFULLY.\n")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    log("=" * 70)
    log("FIVE COMPLETE BUILDING DESIGN PROBLEMS")
    log("Running through main app core modules")
    log("=" * 70 + "\n")
    
    problems = [problem_1, problem_2, problem_3, problem_4, problem_5]
    passed = 0
    
    for i, prob in enumerate(problems, 1):
        try:
            prob()
            passed += 1
        except Exception as e:
            log(f"  PROBLEM {i} FAILED: {e}\n")
    
    log("=" * 70)
    log(f"RESULTS: {passed}/5 problems completed successfully.")
    log("=" * 70)
    
    # Save to log
    log_path = os.path.join(os.path.dirname(__file__), "batch_stress_test.log")
    with open(log_path, "a") as f:
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("COMPLETE DESIGN PROBLEMS (5 BUILDINGS)\n")
        f.write("=" * 70 + "\n")
        for line in LOG:
            f.write(line + "\n")
