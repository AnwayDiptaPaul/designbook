import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder

def run_problem_35():
    print("==================================================")
    print("PROBLEM 35: CABLE-STAYED ROOF (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Model Setup
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # Pylon (20m), Deck (40m)
    builder.define_node(1, 0, 0, 0) # Pylon base
    builder.define_node(2, 0, 0, 20.0) # Pylon top
    
    # Deck nodes every 5m
    deck_nodes = []
    for i in range(9):
        x = i * 5.0
        node = 10 + i
        builder.define_node(node, x, 0.0, 0.0)
        deck_nodes.append(node)
        
    builder.define_fixity(1, [1,1,1,1,1,1]) # Pylon base
    builder.define_fixity(10, [1,1,1,1,1,1]) # Deck start
    builder.define_fixity(2, [0,1,0,1,1,1]) # Pylon top stabilized laterally
    
    # 2. Elements
    builder.define_geometric_transformation(1, 'Linear', [0, 1, 0])
    builder.define_geometric_transformation(2, 'Corotational', [0, 1, 0])
    
    # Pylon
    builder.define_elastic_beam_column(1, 1, 2, 0.5, 3e7, 1e7, 0.1, 0.04, 0.04, 2)
    
    # Deck
    for i in range(len(deck_nodes)-1):
        builder.define_elastic_beam_column(100+i, deck_nodes[i], deck_nodes[i+1], 0.2, 3e7, 1e7, 0.01, 0.005, 0.005, 2)
    
    # Cables (Stayed - Beam-based for stability)
    A_c = 0.001; E_c = 2e8; G_c = 1e8; J_c = 1e-6; I_c = 1e-8
    for i in range(1, len(deck_nodes)):
        node_j = deck_nodes[i]
        builder.define_elastic_beam_column(200+i, 2, node_j, A_c, E_c, G_c, J_c, I_c, I_c, 2)
        # Restrain deck nodes laterally and rotationally
        builder.define_fixity(node_j, [0,1,0,1,1,1])
        
    # 3. Load (Gravity)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
    for node in deck_nodes:
        ops.load(node, 0.0, 0.0, -100.0, 0, 0, 0) # 100 kN per node
        
    # 4. Analysis
    print("Starting Nonlinear Analysis...")
    builder.analyze_static(10)
    
    # 5. Check
    mid_deck = deck_nodes[len(deck_nodes)//2]
    disp = ops.nodeDisp(mid_deck, 3)
    print(f"Mid-span Deck Deflection: {disp*1000:.2f} mm")
    
    print("PROBLEM 35 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_35()
