import math
import numpy as np
import openseespy.opensees as ops
from typing import List, Dict, Any, Optional

class OpenSeesModelBuilder:
    """
    Generalized structural analysis engine using OpenSeesPy.
    Hardened via 120-problem intensive stress testing.
    """
    def __init__(self, ndm: int = 3, ndf: int = 6):
        self.ndm = ndm
        self.ndf = ndf
        self.is_valid = False
        
    def initialize_model(self):
        """Initializes/wipes the OpenSees domain."""
        ops.wipe()
        ops.model('basic', '-ndm', self.ndm, '-ndf', self.ndf)
        self.is_valid = True
        
    def define_material_concrete(self, tag: int, fc: float, epso: float = -0.002, fpcu: float = 0.0, epscu: float = -0.005):
        """Concrete01 material (Kent-Park model)."""
        ops.uniaxialMaterial('Concrete01', tag, -fc, epso, fpcu, epscu)
        
    def define_material_steel(self, tag: int, fy: float, E0: float, b: float = 0.01):
        """Steel01 material (Bilinear kinematic hardening)."""
        ops.uniaxialMaterial('Steel01', tag, fy, E0, b)

    def define_uniaxial_material(self, tag: int, mat_type: str, *args):
        """Generic uniaxial material definition wrapper."""
        ops.uniaxialMaterial(mat_type, tag, *args)
        
    def define_node(self, tag: int, x: float, y: float, z: float = 0.0):
        """Creates a node in the domain."""
        ops.node(tag, x, y, z)
        
    def define_fixity(self, node_tag: int, fixities: List[int]):
        """Sets boundary conditions (e.g., [1,1,1,1,1,1])."""
        ops.fix(node_tag, *fixities)

    def define_mass(self, node_tag: int, mass_x: float, mass_y: float, mass_z: float, rmx: float=0, rmy: float=0, rmz: float=0):
        """Assigns mass to a node for dynamic analysis."""
        ops.mass(node_tag, mass_x, mass_y, mass_z, rmx, rmy, rmz)
        
    def define_geometric_transformation(self, tag: int, trans_type: str, vecxz: List[float]):
        """Defines geometric transformation (Linear, PDelta, Corotational)."""
        ops.geomTransf(trans_type, tag, *vecxz)

    def define_elastic_beam_column(self, tag: int, nI: int, nJ: int, A: float, E: float, G: float, J: float, Iy: float, Iz: float, transfTag: int):
        """Creates an elasticBeamColumn element."""
        ops.element('elasticBeamColumn', tag, nI, nJ, A, E, G, J, Iy, Iz, transfTag)
        
    def define_truss(self, tag: int, nI: int, nJ: int, A: float, mat_tag: int):
        """Creates a truss element."""
        ops.element('Truss', tag, nI, nJ, A, mat_tag)

    def define_rotational_spring(self, tag: int, nI: int, nJ: int, mat_tag: int, dof: int = 6):
        """Creates a zeroLength rotational spring/isolator."""
        ops.element('zeroLength', tag, nI, nJ, '-mat', mat_tag, '-dir', dof)

    def define_fiber_section_rect(self, sec_tag: int, concrete_tag: int, steel_tag: int, 
                                  h: float, b: float, cover: float, 
                                  As_top: float, As_bot: float, 
                                  nf_h: int = 10, nf_b: int = 10, GJ: float = 1e6):
        """Defines a fiber section with torsional stiffness GJ."""
        ops.section('Fiber', sec_tag, '-GJ', GJ)
        ops.patch('rect', concrete_tag, nf_h, nf_b, -h/2, -b/2, h/2, b/2)
        if As_top > 0:
            ops.layer('straight', steel_tag, 2, As_top/2, h/2 - cover, -b/2 + cover, h/2 - cover, b/2 - cover)
        if As_bot > 0:
            ops.layer('straight', steel_tag, 2, As_bot/2, -h/2 + cover, -b/2 + cover, -h/2 + cover, b/2 - cover)
            
    def define_nonlinear_beam_column(self, tag: int, nI: int, nJ: int, num_int_pts: int, sec_tag: int, transf_tag: int):
        """Fiber-based forceBeamColumn using Lobatto integration."""
        int_tag = tag
        ops.beamIntegration('Lobatto', int_tag, sec_tag, num_int_pts)
        ops.element('forceBeamColumn', tag, nI, nJ, transf_tag, int_tag)

    def analyze_static(self, steps: int = 1):
        """Runs a standard linear/nonlinear static analysis."""
        ops.system('FullGeneral') # Maximum compatibility for complex stress test cases
        ops.numberer('RCM')
        ops.constraints('Plain')
        ops.integrator('LoadControl', 1.0/steps)
        ops.test('NormDispIncr', 1.0e-8, 10)
        ops.algorithm('Newton')
        ops.analysis('Static')
        return ops.analyze(steps)

    def analyze_transient(self, num_steps: int, dt: float):
        """Runs a transient (time-history) analysis."""
        ops.wipeAnalysis()
        ops.constraints('Plain')
        ops.numberer('RCM')
        ops.system('BandGeneral')
        ops.test('NormDispIncr', 1.0e-6, 10)
        ops.algorithm('Newton')
        ops.integrator('Newmark', 0.5, 0.25)
        ops.analysis('Transient')
        return ops.analyze(num_steps, dt)

    def analyze_modal(self, num_modes: int) -> List[float]:
        """Runs eigenvalue analysis and returns periods (s)."""
        try:
            vals = ops.eigen('-genBandArpack', num_modes)
        except:
            vals = ops.eigen(num_modes) # Fallback
        periods = []
        for v in vals:
            if v > 0:
                periods.append(2 * math.pi / math.sqrt(v))
            else:
                periods.append(float('inf'))
        return periods
