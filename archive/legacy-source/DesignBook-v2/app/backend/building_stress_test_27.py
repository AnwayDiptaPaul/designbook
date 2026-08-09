import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder
from core.design.pile import PileDesign

def run_problem_27():
    print("==================================================")
    print("PROBLEM 27: DEEP PILE GROUP (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Input: 3x3 Pile Group
    num_piles = 9
    L = 20.0
    D = 0.6
    spacing = 3 * D
    
    # 2. Model Setup
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # Nodes for 9 piles
    tag = 1
    pile_nodes = {}
    for r in range(3):
        for c in range(3):
            # Pile segments (every 2m)
            for z in range(0, int(L) + 1, 2):
                builder.define_node(tag, c*spacing, r*spacing, -float(z))
                pile_nodes[(r, c, z)] = tag
                
                # Springs (p-y)
                if z > 0:
                    builder.define_node(tag+1000, c*spacing, r*spacing, -float(z))
                    builder.define_fixity(tag+1000, [1,1,1,1,1,1])
                    k_py = PileDesign.get_py_stiffness(D, 'sand', float(z))
                    # Define material and element directly via ops
                    ops.uniaxialMaterial('Elastic', tag+2000, k_py)
                    ops.element('zeroLength', tag+3000, tag+1000, tag, '-mat', tag+2000, '-dir', 1, 2)
                    # Vertical spring (point bearing / skin friction simplified)
                    ops.uniaxialMaterial('Elastic', tag+4000, 1e4)
                    ops.element('zeroLength', tag+5000, tag+1000, tag, '-mat', tag+4000, '-dir', 3)
                tag += 1
                
    # 3. Elements (Pile stems)
    E = 2.5e7; G = 1e7; A = math.pi*D**2/4; I = math.pi*D**4/64
    builder.define_geometric_transformation(1, 'Linear', [0, 1, 0]) # Y-vector for Z-elements
    
    el_tag = 1
    for r in range(3):
        for c in range(3):
            for z in range(0, int(L), 2):
                n1 = pile_nodes[(r, c, z)]
                n2 = pile_nodes[(r, c, z+2)]
                builder.define_elastic_beam_column(el_tag, n1, n2, A, E, G, 1e-3, I, I, 1)
                el_tag += 1
                if z + 2 == int(L):
                    # Fix bottom of pile to prevent singularity
                    builder.define_fixity(n2, [1,1,1,1,1,1])
                
    # 4. Load (Total 5000 kN on Pile Cap)
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    for r in range(3):
        for c in range(3):
            ops.load(pile_nodes[(r, c, 0)], 0, 0, -5000.0/9, 0, 0, 0)
            
    # 5. Analysis
    builder.analyze_static(1)
    
    # 6. Check
    settlement = ops.nodeDisp(pile_nodes[(1,1,0)], 3)
    print(f"Pile Group Settlement: {settlement*1000:.2f} mm")
    
    # 7. Design Capacity Check
    cap = PileDesign.design_axial_capacity(D, L, 'sand')
    print(f"Single Pile Allowable Capacity: {cap['Q_allowable']:.2f} kN")
    print(f"Group Capacity (Eff=1.0): {cap['Q_allowable']*9:.2f} kN")
    
    status = "OK" if 5000.0 < cap['Q_allowable']*9 else "OVERLOAD"
    print(f"Foundations Status: {status}")
    
    print("PROBLEM 27 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_27()
