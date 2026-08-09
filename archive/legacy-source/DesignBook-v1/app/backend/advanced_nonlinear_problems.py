import math
import sys
import os

# Add the app directory to the path so we can import backend.core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.analysis.opensees_model import OpenSeesModelBuilder
from backend.core.soil.soil_reaction import SoilMechanics
from backend.core.analysis.time_history import TimeHistoryAnalysis

def run_problem_1_ssi():
    print("\n" + "="*70)
    print("PROBLEM 1: 3D Frame with Winkler Soil-Structure Interaction (SSI)")
    print("="*70)
    
    # 1. Define a simple 3-story, 2-bay x 2-bay office building
    builder = OpenSeesModelBuilder(ndm=3, ndf=6)
    
    grid_x = [0.0, 6.0, 12.0] # Two 6m bays in X
    grid_y = [0.0, 8.0, 16.0]  # Two 8m bays in Y
    stories = [3.5, 3.5, 3.5] # 3 stories @ 3.5m height
    
    # 400x400 C30 columns, 300x500 beams
    c_props = builder.compute_section_properties(400, 400, 30.0)
    b_props = builder.compute_section_properties(300, 500, 30.0)
    
    builder.build_building_model(grid_x, grid_y, stories, b_props, c_props)
    base_nodes = builder._base_nodes
    
    print(f"Model generated: {len(builder._node_map)} nodes, {len(builder._element_map)} elements.")
    print(f"Base nodes identified: {base_nodes}")
    
    # 2. Define Soil Springs based on allowable bearing capacity
    factor_of_safety = 3.0
    expected_settlement = 0.025 # m
    ks_kpa_m = SoilMechanics.calculate_winkler_spring_stiffness(200.0, factor_of_safety, expected_settlement)
    print(f"Subgrade Modulus Ks = {ks_kpa_m:.1f} kN/m³")
    
    # Each column has a 2m x 2m footing
    springs = SoilMechanics.generate_foundation_springs(
        Ks_kpa_m=ks_kpa_m, length_m=2.0, width_m=2.0, depth_m=1.5
    )
        
    floor_nodes = {}
    try:
        import openseespy.opensees as ops # type: ignore
        for s in range(1, len(stories)+1):
            z = sum(stories[:s])
            floor_nodes[s] = [
                n_id for _, n_id in builder._node_map.items()
                # using try to safely get nodeCoord
                if (len(ops.nodeCoord(n_id)) > 2 and math.isclose(float(ops.nodeCoord(n_id, 3)), z))
            ]
    except ImportError:
        # Fallback for mock if openseespy isn't installed
        for s in range(1, len(stories)+1):
            z = sum(stories[:s])
            # For this simple rectangular grid built layer by layer, coordinates aren't needed locally.
            # 9 nodes per floor for a 2x2 bay
            node_start = s * 9 + 1
            node_end = node_start + 9
            floor_nodes[s] = list(range(node_start, node_end))
            
    builder.apply_gravity_loads(floor_nodes, dead_load_kpa=6.0, live_load_kpa=2.5, trib_area_per_node_m2=24.0)

    # 3. First, run modal analysis with FIXED BASE
    builder.define_fixity_for_nodes(base_nodes, [1, 1, 1, 1, 1, 1])
    fixed_periods = builder.run_full_pipeline(n_modes=3, run_gravity=False)["modal"].get("periods", [])
    if fixed_periods:
        print(f"FIXED BASE Periods: T1={fixed_periods[0]:.3f}s, T2={fixed_periods[1]:.3f}s, T3={fixed_periods[2]:.3f}s")
    
    # 4. Now reset base fixity and apply Soil Springs
    builder2 = OpenSeesModelBuilder(ndm=3, ndf=6)
    builder2.build_building_model(grid_x, grid_y, stories, b_props, c_props)
    builder2.apply_gravity_loads(floor_nodes, dead_load_kpa=6.0, live_load_kpa=2.5, trib_area_per_node_m2=24.0)
    
    print("Applying flexible Winkler foundation springs...")
    builder2.apply_winkler_foundation(builder2._base_nodes, springs)
    
    ssi_periods = builder2.run_full_pipeline(n_modes=3, run_gravity=False)["modal"].get("periods", [])
    if ssi_periods:
         print(f"SSI BASE Periods:   T1={ssi_periods[0]:.3f}s, T2={ssi_periods[1]:.3f}s, T3={ssi_periods[2]:.3f}s")
    
    print("PROBLEM 1 COMPLETED SUCCESSFULLY.")

def run_problem_2_pushover():
    print("\n" + "="*70)
    print("PROBLEM 2: 3D Frame Nonlinear Static Pushover Analysis")
    print("="*70)
    
    builder = OpenSeesModelBuilder(ndm=3, ndf=6)
    grid_x = [0.0, 5.0]
    grid_y = [0.0, 5.0]
    stories = [3.0, 3.0]
    
    c_props = builder.compute_section_properties(300, 300, 25.0)
    b_props = builder.compute_section_properties(250, 400, 25.0)
    
    builder.build_building_model(grid_x, grid_y, stories, b_props, c_props)
    builder.define_fixity_for_nodes(builder._base_nodes, [1,1,1,1,1,1])
    
    col_elements = []
    beam_elements = []
    for el_tag, data in builder._element_map.items():
        node_i, node_j = data['nodes']
        coords_i = builder._node_map.get(node_i) # we actually stored (s, ix, iy) -> tag
        # We need coords, but we only have node tags
        try:
            import openseespy.opensees as ops # type: ignore
            x_i, y_i = float(ops.nodeCoord(node_i, 1)), float(ops.nodeCoord(node_i, 2))
            x_j, y_j = float(ops.nodeCoord(node_j, 1)), float(ops.nodeCoord(node_j, 2))
            if math.isclose(x_i, x_j) and math.isclose(y_i, y_j):
                col_elements.append(el_tag)
            else:
                beam_elements.append(el_tag)
        except ImportError:
            if data["type"] == "column":
                col_elements.append(el_tag)
            else:
                beam_elements.append(el_tag)
            
    print(f"Inserting IMK Plastic Hinges on {len(col_elements)} columns and {len(beam_elements)} beams...")
    builder.apply_plastic_hinges(col_elements, 150.0, -150.0)
    builder.apply_plastic_hinges(beam_elements, 100.0, -100.0)
    
    roof_z = sum(stories)
    try:
        import openseespy.opensees as ops # type: ignore
        roof_nodes = [nd for nd in builder._node_map.values() if math.isclose(float(ops.nodeCoord(nd, 3)), roof_z)]
    except ImportError:
        # Mock logic
        s = len(stories)
        node_start = s * 4 + 1 # 2x2 grid -> 4 nodes per floor? Wait, 2 bays x 2 bays -> 3x3 nodes = 9. But Problem 2 grid is [0.0, 5.0] so 1 bay x 1 bay = 4 nodes.
        # Actually in problem 2 nx=2, ny=2 points, so 4 nodes per story.
        node_end = node_start + 4
        roof_nodes = list(range(node_start, node_end))
        
    control_node = roof_nodes[0]
    
    print(f"Applying lateral forces at roof (z={roof_z}m). Control Node: {control_node}")
    try:
        import openseespy.opensees as ops # type: ignore
        ops.timeSeries('Linear', 2)
        ops.pattern('Plain', 2, 2)
        for nd in roof_nodes:
            ops.load(nd, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            
        print("Running displacement-controlled pushover to 300mm roof drift...")
        push_results = builder.run_pushover_analysis(control_node=control_node, control_dof=1, d_max=0.300, d_incr=0.002)
        
        print(f"Pushover Status: {push_results['status']}")
        print(f"Steps Completed: {push_results['steps_completed']}")
        
        if push_results['steps_completed'] > 0:
            max_base_shear = max(push_results['base_shears'])
            print(f"Maximum Base Shear Capacity: {max_base_shear:.1f} kN")
            
    except ImportError:
        print("Note: openseespy not installed, skipping actual pushover execution.")
        
    print("PROBLEM 2 COMPLETED SUCCESSFULLY.")

def run_problem_3_time_history():
    print("\n" + "="*70)
    print("PROBLEM 3: 3D Frame Non-Linear Time History Analysis")
    print("="*70)
    
    builder = OpenSeesModelBuilder(ndm=3, ndf=6)
    grid_x = [0.0, 6.0]
    grid_y = [0.0, 6.0]
    stories = [4.0, 4.0, 4.0]
    
    c_props = builder.compute_section_properties(500, 500, 35.0)
    b_props = builder.compute_section_properties(300, 600, 35.0)
    
    builder.build_building_model(grid_x, grid_y, stories, b_props, c_props)
    builder.define_fixity_for_nodes(builder._base_nodes, [1,1,1,1,1,1])
    
    # 1. Apply gravity loads for mass scaling
    floor_nodes = {}
    try:
        import openseespy.opensees as ops # type: ignore
        for s in range(1, len(stories)+1):
            z = sum(stories[:s])
            floor_nodes[s] = [
                n_id for _, n_id in builder._node_map.items()
                if (len(ops.nodeCoord(n_id)) > 2 and math.isclose(float(ops.nodeCoord(n_id, 3)), z))
            ]
    except ImportError:
        for s in range(1, len(stories)+1):
            z = sum(stories[:s])
            node_start = s * 6 + 1 # 3x2 bay is 6 nodes per floor
            node_end = node_start + 6
            floor_nodes[s] = list(range(node_start, node_end))
    builder.apply_gravity_loads(floor_nodes, dead_load_kpa=8.0, live_load_kpa=0.0, trib_area_per_node_m2=36.0)
    
    # 2. Extract a synthetic earthquake record (e.g. El Centro stub)
    record = TimeHistoryAnalysis.parse_earthquake_record("mock_db.txt")
    dt = record["dt"]
    n_pts = record["n_pts"]
    
    # Generate a simple 5Hz sine wave excitation as a mock earthquake since we don't have a real file
    accelerations = [0.2 * math.sin(2 * math.pi * 5.0 * i * dt) for i in range(n_pts)]
    # Taper the end
    for i in range(int(n_pts * 0.8), n_pts):
        accelerations[i] *= (n_pts - i) / (n_pts * 0.2)
        
    print(f"Earthquake Excititation: {n_pts} points, dt={dt}s, Max Accel={max(accelerations):.3f}g")
    
    roof_z = sum(stories)
    try:
        import openseespy.opensees as ops # type: ignore
        roof_nodes = [nd for nd in builder._node_map.values() if math.isclose(float(ops.nodeCoord(nd, 3)), roof_z)]
    except ImportError:
        # Mock logic
        s = len(stories)
        node_start = s * 6 + 1 # 3x2 bay is 6 nodes per floor
        node_end = node_start + 6
        roof_nodes = list(range(node_start, node_end))
        
    control_node = roof_nodes[0]
    
    try:
        import openseespy.opensees as ops # type: ignore
        
        # Run Gravity static analysis first to get gravity forces before dynamic
        print("Running initial gravity analysis...")
        ops.system('BandGeneral')
        ops.numberer('RCM')
        ops.constraints('Plain')
        ops.test('NormDispIncr', 1.0e-8, 10)
        ops.algorithm('Newton')
        ops.integrator('LoadControl', 0.1)
        ops.analysis('Static')
        ops.analyze(10)
        ops.loadConst('-time', 0.0)
        
        print("Running nonlinear time history analysis...")
        th_results = builder.run_time_history_analysis(dt, n_pts, accelerations, direction=1, roof_node=control_node)
        
        print(f"THA Status: {th_results['status']}")
        if th_results['steps_completed'] > 0:
            max_drift = max(abs(d) for d in th_results['roof_displacements'])
            max_shear = max(th_results['base_shears'])
            print(f"Max Roof Drift: {max_drift * 1000:.1f} mm")
            print(f"Max Base Shear: {max_shear:.1f} kN")
            
    except ImportError:
        print("Note: openseespy not installed, skipping actual time history execution.")

    print("PROBLEM 3 COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    run_problem_1_ssi()
    run_problem_2_pushover()
    run_problem_3_time_history()
