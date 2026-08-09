# pyre-ignore-all-errors
import sys, os, time
import traceback
import json
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from backend.core.analysis.opensees_model import OpenSeesModelBuilder

def run_increasing_stress_tests():
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs/batch_stress_test.log'))
    
    with open(log_path, 'a') as f:
        f.write("\n\n" + "="*70 + "\n")
        f.write("EXTENDED STRESS TESTS: 15 INCREASINGLY DIFFICULT PROBLEMS\n")
        f.write("="*70 + "\n")
    
    passed = 0
    for idx in range(1, 16):
        test_no = idx
        
        # Scale difficulty
        n_stories = 4 + test_no * 2  # Increases from 6 stories up to 34 stories
        bay_width = 4.0 + (test_no % 3)
        bay_depth = 5.0 + (test_no % 4)
        
        n_bays_x = 2 + test_no
        n_bays_y = 2 + (test_no // 2)
        
        grid_x = [float(i * bay_width) for i in range(n_bays_x + 1)]
        grid_y = [float(i * bay_depth) for i in range(n_bays_y + 1)]
        stories = [3.5 for _ in range(n_stories)]
        
        log_msgs = []
        log_msgs.append(f"\n--- EXTENDED PROBLEM {test_no} ---")
        log_msgs.append(f"Stories: {n_stories}")
        log_msgs.append(f"Grid Size: {len(grid_x)} x {len(grid_y)} nodes per floor")
        
        try:
            # Memory isolation implicitly handled via small test structure if not parallelized, 
            # but to be safe we'll use OpenSeesPy directly since it's just modeling
            builder = OpenSeesModelBuilder(ndm=3, ndf=6)
            builder.initialize_model()
            
            c_props = builder.compute_section_properties(500, 500, 30.0)
            b_props = builder.compute_section_properties(300, 600, 30.0)
            
            model = builder.build_building_model(grid_x, grid_y, stories, b_props, c_props)
            log_msgs.append(f"Generated Model: {model['n_nodes']} nodes, {model['n_elements']} elements")
            
            floor_nodes = {}
            import openseespy.opensees as ops # type: ignore
            import math
            for s in range(1, n_stories+1):
                z = float(sum(stories[:s]))
                floor_nodes[s] = [
                    n_id for _, n_id in builder._node_map.items()
                    if (len(ops.nodeCoord(n_id)) > 2 and math.isclose(float(ops.nodeCoord(n_id, 3)), z))
                ]
                
            trib_area = bay_width * bay_depth / 4.0
            builder.apply_gravity_loads(floor_nodes, 8.0, 3.0, trib_area)
            
            # Use smaller number of modes to prevent slow eigenvalue decomp on huge matrix
            n_modes = min(3, n_stories)
            st = time.time()
            result = builder.run_full_pipeline(n_modes=n_modes, run_gravity=True)
            elapsed = time.time() - st
            
            log_msgs.append(f"Gravity Status: {result['gravity']['status']}")
            if result['modal']:
               log_msgs.append(f"First Period: {result['modal']['periods'][0]:.3f} s")
            log_msgs.append(f"Solved in {elapsed:.2f} seconds")
            
            passed += 1
            log_msgs.append("SUCCESS")
        except Exception as e:
            log_msgs.append(f"FAILED: {str(e)}")
            log_msgs.append(traceback.format_exc())
            
        with open(log_path, 'a') as f:
            for msg in log_msgs:
                f.write(msg + "\n")
                print(msg)
                
    with open(log_path, 'a') as f:
        msg = f"\nRESULTS: {passed}/15 Extended Problems Completed."
        f.write(msg + "\n")
        print(msg)

LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs/interaction_log.json'))

def record_io(module_name: str, input_payload: dict, output_payload: dict = None, error: str = None):
    """
    Safely records UI inputs dispatched to the backend, and the OpenSeesPy outputs 
    received, without requiring modifications to the core backend codebase.
    """
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "module": module_name,
        "input": input_payload,
        "output": output_payload,
        "error": error
    }
    
    # Ensure directory exists if needed
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            pass
            
    logs.append(record)
    
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

if __name__ == "__main__":
    run_increasing_stress_tests()
