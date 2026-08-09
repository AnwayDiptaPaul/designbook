import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder
from core.loads.seismic import calculate_seismic_loads, SeismicInput, SeismicResult
from core.loads.wind import calculate_wind_loads, WindLoadInput
from core.design.pile import PileDesign
from core.design.qto import QuantityTakeoff

def run_problem_21():
    print("==================================================")
    print("PROBLEM 21: HIGH-RISE (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Geometry
    num_stories = 15
    story_h = 3.5
    total_h = num_stories * story_h
    elevs = [story_h * (i+1) for i in range(num_stories)]
    weights = [2500.0] * num_stories
    
    # 2. Main App: Seismic
    seis_inp = SeismicInput("IV", "SE", "residential", "SMRF", total_h, weights, elevs)
    seis_res = calculate_seismic_loads(seis_inp)
    print(f"Seismic Base Shear: {seis_res.base_shear_kn:.2f} kN")
    
    # 3. Main App: Wind
    wind_inp = WindLoadInput(
        basic_wind_speed_mps=60.0, 
        exposure_category="D", 
        building_width_m=24.0, 
        building_depth_m=18.0, 
        floor_elevations_m=elevs, 
        floor_heights_m=[story_h]*num_stories
    )
    wind_res = calculate_wind_loads(wind_inp)
    print(f"Wind Base Shear: {wind_res.base_shear_kn:.2f} kN")
    
    # 4. Main App: OpenSees Model
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # 3D Grid from Story 0 to 15
    L_x = 6.0; L_y = 6.0
    node_map = {}
    tag = 1
    for s in range(num_stories + 1):
        for ix in range(5): # 4 bays
            for iy in range(4): # 3 bays
                builder.define_node(tag, ix*L_x, iy*L_y, s*story_h)
                if s == 0: builder.define_fixity(tag, [1]*6)
                # Assign lumped mass
                g = 9.81
                m = (2500.0 / 20.0) / g # 20 nodes per floor
                if s > 0: builder.define_mass(tag, m, m, 1e-9)
                node_map[(s, ix, iy)] = tag
                tag += 1
                
    # Transformations
    builder.define_geometric_transformation(1, 'Linear', [0, 1, 0])
    builder.define_geometric_transformation(2, 'Linear', [1, 0, 0])
    builder.define_geometric_transformation(3, 'PDelta', [1, 0, 0])
    
    # Elements
    E = 2.5e7; G = 1e7
    el_tag = 1
    for s in range(num_stories):
        for ix in range(5):
            for iy in range(4):
                n1 = node_map[(s, ix, iy)]
                n2 = node_map[(s+1, ix, iy)]
                builder.define_elastic_beam_column(el_tag, n1, n2, 0.6*0.6, E, G, 1e-3, 1e-3, 1e-3, 3)
                el_tag += 1
                
    # 5. Main App: Analysis
    periods = builder.analyze_modal(3)
    print(f"Modal Periods (s): {periods}")
    
    # 6. Main App: QTO
    vol = QuantityTakeoff.calculate_concrete_volume(0.6, 0.6, total_h)
    print(f"Column Concrete Volume per Line: {vol:.2f} m3")
    
    print("PROBLEM 21 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_21()
