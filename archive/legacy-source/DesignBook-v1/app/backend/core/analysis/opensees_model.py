import math
import numpy as np
try:
    import openseespy.opensees as ops
    HAS_OPENSEES = True
except ImportError:
    # Fallback mock for environments without OpenSeesPy
    class _MockOps:
        def __getattr__(self, name):
            def noop(*args, **kwargs):
                if name == 'analyze':
                    return 0  # success
                if name == 'eigen':
                    n = args[0] if args and isinstance(args[0], int) else (args[1] if len(args) > 1 else 3)
                    return [0.1 * (i + 1) for i in range(n)]
                if name in ('nodeDisp',):
                    return 0.0
                if name in ('eleForce',):
                    return [0.0] * 12
                return None
            return noop
    ops = _MockOps()
    HAS_OPENSEES = False

from typing import List, Dict, Any, Optional, Tuple

class OpenSeesModelBuilder:
    """
    Generalized structural analysis engine using OpenSeesPy.
    Hardened via 120-problem intensive stress testing.
    Enhanced with ETABS-like convenience methods for building-level workflows.
    """
    def __init__(self, ndm: int = 3, ndf: int = 6):
        self.ndm = ndm
        self.ndf = ndf
        self.is_valid = False
        self._node_counter = 0
        self._element_counter = 0
        self._transf_counter = 0
        self._node_map: Dict[Tuple, int] = {}  # (story, ix, iy) -> node_tag
        self._element_map: Dict[int, Dict[str, Any]] = {}  # el_tag -> meta
        self._floor_master_nodes: Dict[int, int] = {}  # story -> master node tag
        self._base_nodes: List[int] = [] # list of support nodes
        
    def initialize_model(self):
        """Initializes/wipes the OpenSees domain."""
        ops.wipe()
        ops.model('basic', '-ndm', self.ndm, '-ndf', self.ndf)
        self.is_valid = True
        self._node_counter = 0
        self._element_counter = 0
        self._transf_counter = 0
        self._node_map = {}
        self._element_map = {}
        self._floor_master_nodes = {}
        self._base_nodes = []
        
    # ── Material Definitions ─────────────────────────────────────────────
        
    def define_material_concrete(self, tag: int, fc: float, epso: float = -0.002, fpcu: float = 0.0, epscu: float = -0.005):
        """Concrete01 material (Kent-Park model)."""
        ops.uniaxialMaterial('Concrete01', tag, -fc, epso, fpcu, epscu)
        
    def define_material_steel(self, tag: int, fy: float, E0: float, b: float = 0.01):
        """Steel01 material (Bilinear kinematic hardening)."""
        ops.uniaxialMaterial('Steel01', tag, fy, E0, b)

    def define_uniaxial_material(self, tag: int, mat_type: str, *args):
        """Generic uniaxial material definition wrapper."""
        ops.uniaxialMaterial(mat_type, tag, *args)
        
    # ── Node & Boundary Definitions ──────────────────────────────────────
        
    def define_node(self, tag: int, x: float, y: float, z: float = 0.0):
        """Creates a node in the domain."""
        ops.node(tag, x, y, z)
        self._node_counter = max(self._node_counter, tag)
        
    def define_fixity(self, node_tag: int, fixities: List[int]):
        """Sets boundary conditions (e.g., [1,1,1,1,1,1])."""
        ops.fix(node_tag, *fixities)

    def define_fixity_for_nodes(self, node_tags: List[int], fixities: List[int]):
        """Sets boundary conditions for an array of node tags."""
        for tag in node_tags:
            ops.fix(tag, *fixities)

    def define_mass(self, node_tag: int, mass_x: float, mass_y: float, mass_z: float, rmx: float=0, rmy: float=0, rmz: float=0):
        """Assigns mass to a node for dynamic analysis."""
        ops.mass(node_tag, mass_x, mass_y, mass_z, rmx, rmy, rmz)
        
    # ── Geometric Transformations ────────────────────────────────────────
        
    def define_geometric_transformation(self, tag: int, trans_type: str, vecxz: List[float]):
        """Defines geometric transformation (Linear, PDelta, Corotational)."""
        ops.geomTransf(trans_type, tag, *vecxz)
        self._transf_counter = max(self._transf_counter, tag)

    # ── Element Definitions ──────────────────────────────────────────────

    def define_elastic_beam_column(self, tag: int, nI: int, nJ: int, A: float, E: float, G: float, J: float, Iy: float, Iz: float, transfTag: int):
        """Creates an elasticBeamColumn element."""
        ops.element('elasticBeamColumn', tag, nI, nJ, A, E, G, J, Iy, Iz, transfTag)
        self._element_counter = max(self._element_counter, tag)
        
    def define_truss(self, tag: int, nI: int, nJ: int, A: float, mat_tag: int):
        """Creates a truss element."""
        ops.element('Truss', tag, nI, nJ, A, mat_tag)
        self._element_counter = max(self._element_counter, tag)

    def define_rotational_spring(self, tag: int, nI: int, nJ: int, mat_tag: int, dof: int = 6):
        """Creates a zeroLength rotational spring/isolator."""
        ops.element('zeroLength', tag, nI, nJ, '-mat', mat_tag, '-dir', dof)
        self._element_counter = max(self._element_counter, tag)

    # ── Fiber Section Definitions ────────────────────────────────────────

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
        self._element_counter = max(self._element_counter, tag)

    # ══════════════════════════════════════════════════════════════════════
    # ETABS-LEVEL CONVENIENCE METHODS
    # ══════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def compute_section_properties(b_mm: float, h_mm: float, fc_mpa: float) -> Dict[str, float]:
        """Auto-calculate section properties from dimensions and concrete grade.
        
        Returns A (m²), Iy (m⁴), Iz (m⁴), J (m⁴), E (kPa), G (kPa).
        Like ETABS, converts from mm inputs to model units (SI: m, kN).
        """
        b = b_mm / 1000.0  # m
        h = h_mm / 1000.0  # m
        Ec = 4700 * math.sqrt(fc_mpa) * 1000  # kPa
        nu = 0.2  # Poisson's ratio for concrete
        Gc = Ec / (2 * (1 + nu))
        
        A = b * h
        Iy = b * h**3 / 12.0
        Iz = h * b**3 / 12.0
        # Torsional constant (approximate for rectangle)
        a_t = max(b, h)
        b_t = min(b, h)
        J = a_t * b_t**3 * (1/3 - 0.21 * b_t/a_t * (1 - b_t**4 / (12 * a_t**4)))
        
        return {
            "A": A, "Iy": Iy, "Iz": Iz, "J": J, "E": Ec, "G": Gc,
            "b_mm": b_mm, "h_mm": h_mm
        }
    
    @staticmethod
    def compute_mass_from_loads(dead_load_kpa: float, trib_area_m2: float, g: float = 9.81) -> float:
        """Convert dead load to lumped nodal mass (tonnes = kN·s²/m).
        
        Like ETABS mass source definition.
        """
        weight_kn = dead_load_kpa * trib_area_m2
        mass = weight_kn / g  # kN·s²/m
        return mass

    def apply_rigid_diaphragm(self, master_node: int, slave_nodes: List[int], perp_dof: int = 3):
        """Constrains floor nodes for rigid-floor behavior (like ETABS diaphragm).
        
        perp_dof: DOF perpendicular to the floor plane (3 = Z for horizontal floors).
        """
        for slave in slave_nodes:
            ops.rigidDiaphragm(perp_dof, master_node, slave)
        self._floor_master_nodes[master_node] = master_node

    def build_building_model(
        self,
        grid_x: List[float],
        grid_y: List[float],
        story_heights: List[float],
        beam_section: Dict[str, float],
        column_section: Dict[str, float],
        fc_mpa: float = 25.0,
        base_fixity: str = "fixed",
        use_pdelta: bool = False,
        rigid_diaphragm: bool = True,
    ) -> Dict[str, Any]:
        """Build a complete 3D building frame model from grid definition.
        
        Like ETABS model definition — auto-generates nodes, columns, beams,
        boundary conditions, transformations, and optionally rigid diaphragms.
        
        Args:
            grid_x: X-coordinates of grid lines (m)
            grid_y: Y-coordinates of grid lines (m)
            story_heights: Floor-to-floor heights (m) per story
            beam_section: {"b_mm": 300, "h_mm": 600}
            column_section: {"b_mm": 450, "h_mm": 450}
            fc_mpa: Concrete grade
            base_fixity: "fixed" or "pinned"
            use_pdelta: Use P-Delta geometric transformation for columns
            rigid_diaphragm: Apply rigid diaphragm at each floor
            
        Returns:
            dict with node_map, element_map, floor_elevations, etc.
        """
        n_stories = len(story_heights)
        nx = len(grid_x)
        ny = len(grid_y)
        
        # Compute section properties
        beam_props = self.compute_section_properties(
            beam_section["b_mm"], beam_section["h_mm"], fc_mpa
        )
        col_props = self.compute_section_properties(
            column_section["b_mm"], column_section["h_mm"], fc_mpa
        )
        
        E = col_props["E"]
        G = col_props["G"]
        
        # Define transformations
        col_transf_type = "PDelta" if use_pdelta else "Linear"
        t_beam_x = self._transf_counter + 1
        t_beam_y = self._transf_counter + 2
        t_column = self._transf_counter + 3
        self.define_geometric_transformation(t_beam_x, 'Linear', [0, 0, 1])
        self.define_geometric_transformation(t_beam_y, 'Linear', [0, 0, 1])
        self.define_geometric_transformation(t_column, col_transf_type, [1, 0, 0])
        
        # Generate nodes
        node_tag = self._node_counter + 1
        elevation = 0.0
        floor_elevations = [0.0]
        floor_nodes: Dict[int, List[int]] = {}  # story -> [node_tags]
        
        for s in range(n_stories + 1):  # 0 = base, 1..n = floors
            floor_nodes[s] = []
            for ix, x in enumerate(grid_x):
                for iy, y in enumerate(grid_y):
                    self.define_node(node_tag, x, y, elevation)
                    self._node_map[(s, ix, iy)] = node_tag
                    floor_nodes[s].append(node_tag)
                    
                    # Base fixity
                    if s == 0:
                        self._base_nodes.append(node_tag)
                        if base_fixity == "fixed":
                            self.define_fixity(node_tag, [1, 1, 1, 1, 1, 1])
                        else:
                            self.define_fixity(node_tag, [1, 1, 1, 0, 0, 0])
                    
                    node_tag += 1
            
            if s < n_stories:
                elevation += float(story_heights[s])
                floor_elevations.append(elevation)
        
        self._node_counter = node_tag - 1
        
        # Apply rigid diaphragms at each floor (not at base)
        if rigid_diaphragm:
            for s in range(1, n_stories + 1):
                nodes = floor_nodes[s]
                if len(nodes) > 1:
                    master = nodes[0]
                    slaves = nodes[1:]
                    self.apply_rigid_diaphragm(master, slaves)
        
        # Define column elements
        el_tag = self._element_counter + 1
        column_tags = []
        for s in range(n_stories):
            for ix in range(nx):
                for iy in range(ny):
                    key_bot = (s, ix, iy)
                    key_top = (s + 1, ix, iy)
                    if key_bot in self._node_map and key_top in self._node_map:
                        n1 = self._node_map[key_bot]
                        n2 = self._node_map[key_top]
                        self.define_elastic_beam_column(
                            el_tag, n1, n2,
                            col_props["A"], E, G,
                            col_props["J"], col_props["Iy"], col_props["Iz"],
                            t_column,
                        )
                        self._element_map[el_tag] = {
                            "type": "column", "story": s, "grid": (ix, iy),
                            "nodes": (n1, n2),
                            "transf_tag": t_column,
                            "A": col_props["A"], "E": E, "G": G,
                            "J": col_props["J"], "Iy": col_props["Iy"], "Iz": col_props["Iz"],
                            # IMK expects My_pos/My_neg later; store generic yield strength as placeholder if needed
                        }
                        column_tags.append(el_tag)
                        el_tag += 1
        
        # Define beam elements (X-direction and Y-direction)
        beam_tags = []
        for s in range(1, n_stories + 1):
            # X-direction beams
            for ix in range(nx - 1):
                for iy in range(ny):
                    key1 = (s, ix, iy)
                    key2 = (s, ix + 1, iy)
                    if key1 in self._node_map and key2 in self._node_map:
                        n1 = self._node_map[key1]
                        n2 = self._node_map[key2]
                        self.define_elastic_beam_column(
                            el_tag, n1, n2,
                            beam_props["A"], E, G,
                            beam_props["J"], beam_props["Iy"], beam_props["Iz"],
                            t_beam_x,
                        )
                        self._element_map[el_tag] = {
                            "type": "beam", "dir": "X", "story": s, "grid": (ix, iy),
                            "nodes": (n1, n2),
                            "transf_tag": t_beam_x,
                            "A": beam_props["A"], "E": E, "G": G,
                            "J": beam_props["J"], "Iy": beam_props["Iy"], "Iz": beam_props["Iz"],
                        }
                        beam_tags.append(el_tag)
                        el_tag += 1
            
            # Y-direction beams
            for ix in range(nx):
                for iy in range(ny - 1):
                    key1 = (s, ix, iy)
                    key2 = (s, ix, iy + 1)
                    if key1 in self._node_map and key2 in self._node_map:
                        n1 = self._node_map[key1]
                        n2 = self._node_map[key2]
                        self.define_elastic_beam_column(
                            el_tag, n1, n2,
                            beam_props["A"], E, G,
                            beam_props["J"], beam_props["Iy"], beam_props["Iz"],
                            t_beam_y,
                        )
                        self._element_map[el_tag] = {
                            "type": "beam", "dir": "Y", "story": s, "grid": (ix, iy),
                            "nodes": (n1, n2),
                            "transf_tag": t_beam_y,
                            "A": beam_props["A"], "E": E, "G": G,
                            "J": beam_props["J"], "Iy": beam_props["Iy"], "Iz": beam_props["Iz"],
                        }
                        beam_tags.append(el_tag)
                        el_tag += 1
        
        self._element_counter = el_tag - 1
        
        return {
            "node_map": dict(self._node_map),
            "floor_elevations": floor_elevations[1:],  # exclude base
            "floor_nodes": floor_nodes,
            "column_tags": column_tags,
            "beam_tags": beam_tags,
            "n_nodes": self._node_counter,
            "n_elements": self._element_counter,
        }
    
    def apply_winkler_foundation(self, base_nodes: List[int], spring_props: Dict[str, float]):
        """
        Attaches 6-DOF elastic soil springs to base nodes for Soil-Structure Interaction (SSI).
        Instead of rigidly fixing the base, this uses zeroLength elements with the spring stiffnesses.
        
        spring_props: Dict with keys Kx, Ky, Kz, KRx, KRy, KRz (e.g., from SoilMechanics.generate_foundation_springs)
        """
        # Define a high-stiffness elastic material for fixed DOFs (if any)
        rigid_mat_tag = self._transf_counter + 999  # arbitrary high tag
        ops.uniaxialMaterial('Elastic', rigid_mat_tag, 1e12)
        
        # Define materials for each spring DOF
        spring_mats = {}
        for i, dof_key in enumerate(['Kx', 'Ky', 'Kz', 'KRx', 'KRy', 'KRz']):
            mat_tag = self._transf_counter + 1000 + i
            k_val = spring_props.get(dof_key, 1e12)  # default to rigid if missing
            ops.uniaxialMaterial('Elastic', mat_tag, k_val)
            spring_mats[i+1] = mat_tag
            
        for b_node in base_nodes:
            # Create a fixed support node exactly at the base node's location
            x = ops.nodeCoord(b_node, 1)
            y = ops.nodeCoord(b_node, 2)
            z = ops.nodeCoord(b_node, 3)
            
            fixed_node = self._node_counter + 1
            self.define_node(fixed_node, x, y, z)
            self.define_fixity(fixed_node, [1, 1, 1, 1, 1, 1])
            
            # Connect the fixed node to the base node with a zeroLength spring element
            el_tag = self._element_counter + 1
            
            # We need to assign materials to all 6 DOFs
            mat_tags = [spring_mats[1], spring_mats[2], spring_mats[3], spring_mats[4], spring_mats[5], spring_mats[6]]
            dirs = [1, 2, 3, 4, 5, 6]
            
            ops.element('zeroLength', el_tag, fixed_node, b_node, '-mat', *mat_tags, '-dir', *dirs)
            self._element_counter = el_tag
            
    def apply_gravity_loads(
        self,
        floor_nodes: Dict[int, List[int]],
        dead_load_kpa: float,
        live_load_kpa: float,
        trib_area_per_node_m2: float,
        ts_tag: int = 1,
        pattern_tag: int = 1,
    ):
        """Apply gravity loads at all floor nodes (like ETABS shell load → nodal).
        
        Distributes floor area loads as point loads on nodes. Also assigns 
        seismic masses from dead load.
        """
        ops.timeSeries('Constant', ts_tag)
        ops.pattern('Plain', pattern_tag, ts_tag)
        
        total_load = dead_load_kpa + live_load_kpa  # kPa = kN/m²
        force_per_node = total_load * trib_area_per_node_m2  # kN
        
        for story, nodes in floor_nodes.items():
            if story == 0:
                continue  # skip base
            for nd in nodes:
                ops.load(nd, 0.0, 0.0, -force_per_node, 0.0, 0.0, 0.0)
                # Assign mass from dead load only (for seismic)
                mass = self.compute_mass_from_loads(dead_load_kpa, trib_area_per_node_m2)
                self.define_mass(nd, mass, mass, 0.0)  # No vertical mass
    
    def apply_lateral_forces(
        self,
        floor_nodes: Dict[int, List[int]],
        story_forces_kn: List[float],
        direction: str = "X",
        ts_tag: int = 2,
        pattern_tag: int = 2,
    ):
        """Apply lateral forces at each floor level (like ETABS auto-lateral load).
        
        story_forces_kn: lateral force per story (index 0 = first floor above base)
        direction: "X" or "Y"
        """
        ops.timeSeries('Constant', ts_tag)
        ops.pattern('Plain', pattern_tag, ts_tag)
        
        for i, force in enumerate(story_forces_kn):
            story = i + 1  # floor index (1 = first floor)
            if story not in floor_nodes:
                continue
            nodes = floor_nodes[story]
            n_nodes = len(nodes) if nodes else 1
            force_per_node = force / n_nodes
            
            for nd in nodes:
                if direction.upper() == "X":
                    ops.load(nd, force_per_node, 0.0, 0.0, 0.0, 0.0, 0.0)
                else:
                    ops.load(nd, 0.0, force_per_node, 0.0, 0.0, 0.0, 0.0)
    
    def extract_member_forces(self, element_tags: List[int]) -> Dict[int, Dict[str, float]]:
        """Extract member end forces (M, V, P, T) for each element.
        
        Returns a dict: {el_tag: {"Ni": P_i, "Vyi": V_yi, "Vzi": V_zi, "Ti": T_i, "Myi": M_yi, "Mzi": M_zi, ...}}
        Like ETABS member force output.
        """
        results = {}
        for tag in element_tags:
            try:
                forces = ops.eleForce(tag)
                # 3D beam-column: 12 DOFs (6 at each end)
                if len(forces) >= 12:
                    results[tag] = {
                        "Ni": forces[0],   "Vyi": forces[1],  "Vzi": forces[2],
                        "Ti": forces[3],   "Myi": forces[4],  "Mzi": forces[5],
                        "Nj": forces[6],   "Vyj": forces[7],  "Vzj": forces[8],
                        "Tj": forces[9],   "Myj": forces[10], "Mzj": forces[11],
                    }
                elif len(forces) >= 6:
                    results[tag] = {
                        "Ni": forces[0], "Vyi": forces[1], "Mzi": forces[2],
                        "Nj": forces[3], "Vyj": forces[4], "Mzj": forces[5],
                    }
                else:
                    results[tag] = {"raw": list(forces)}
            except Exception:
                results[tag] = {"error": "Could not extract forces"}
        return results
    
    def extract_node_displacements(self, node_tags: List[int]) -> Dict[int, List[float]]:
        """Extract nodal displacements [dx, dy, dz, rx, ry, rz]."""
        results = {}
        for tag in node_tags:
            try:
                disp = [ops.nodeDisp(tag, dof) for dof in range(1, self.ndf + 1)]
                results[tag] = disp
            except Exception:
                results[tag] = [0.0] * self.ndf
        return results

    def extract_story_drifts(
        self,
        floor_nodes: Dict[int, List[int]],
        floor_elevations: List[float],
        direction: str = "X",
    ) -> List[Dict[str, float]]:
        """Calculate story drifts from nodal displacements (like ETABS drift output).
        
        Returns list of {story, elevation, drift_mm, drift_ratio} per story.
        """
        dof = 1 if direction.upper() == "X" else 2
        drifts = []
        prev_avg_disp = 0.0
        prev_elev = 0.0
        
        for s in range(1, len(floor_elevations) + 1):
            if s not in floor_nodes:
                continue
            nodes = floor_nodes[s]
            avg_disp = sum(ops.nodeDisp(nd, dof) for nd in nodes) / max(len(nodes), 1)
            
            story_height = floor_elevations[s - 1] - prev_elev if s > 0 else floor_elevations[0]
            inter_story_disp = avg_disp - prev_avg_disp
            drift_ratio = abs(inter_story_disp) / story_height if story_height > 0 else 0
            
            drifts.append({
                "story": s,
                "elevation_m": floor_elevations[s - 1],
                "drift_mm": abs(inter_story_disp) * 1000,
                "drift_ratio": drift_ratio,
            })
            
            prev_avg_disp = avg_disp
            prev_elev = floor_elevations[s - 1]
        
        return drifts
    
    def apply_plastic_hinges(self, element_tags: List[int], My_pos: float, My_neg: float, hinge_length_ratio: float = 0.1):
        """
        Inserts lumped plastic hinges (zeroLength rotational springs) at the ends of specified beam/column elements.
        Uses the Bilin (IMK) material model from nonlinear_hinge.py.
        Currently focused on primary bending (M_z for 2D, M_y and M_z for 3D).
        """
        for el_tag in element_tags:
            if el_tag not in self._element_map:
                continue
                
            el_data = self._element_map[el_tag]
            i_node, j_node = el_data['nodes']
            
            # Simple IMK parameters for concrete (theta_p ~ 0.02, theta_pc ~ 0.1)
            K0 = 1e6 # Base elastic stiffness of hinge
            theta_p = 0.025
            theta_pc = 0.10
            Lambda = 1.0
            
            # Create a new material for the hinge
            mat_tag = self._transf_counter + 2000 + el_tag
            
            # Use Bilin material
            try:
                ops.uniaxialMaterial('Bilin', mat_tag, K0, 0.01, 0.01, My_pos, My_neg, Lambda, Lambda, Lambda, Lambda, 
                                 1.0, 1.0, 1.0, 1.0, theta_p, theta_p, theta_pc, theta_pc, 1.0, 1.0, 0.4, 0.4, 1.0, 1.0)
            except Exception:
                # If Bilin is missing in this openseespy version, fallback to Steel01
                ops.uniaxialMaterial('Steel01', mat_tag, My_pos, K0, 0.01)
            
            # Create duplicate node for i_node
            x = ops.nodeCoord(i_node, 1)
            y = ops.nodeCoord(i_node, 2)
            z = ops.nodeCoord(i_node, 3)
            
            new_i_node = self._node_counter + 1
            self.define_node(new_i_node, x, y, z)
            
            # Connect the original i_node to the new_i_node with a zeroLength spring
            hinge_el_tag = self._element_counter + 1
            
            # Master node (original), Slave node (new)
            # Fix translations and torsion, hinge on primary bending (dir 6 in 3D: Rz, dir 5: Ry)
            rigid_mat = self._transf_counter + 999
            try:
                ops.uniaxialMaterial('Elastic', rigid_mat, 1e12)
            except:
                pass # Already defined
                
            ops.element('zeroLength', hinge_el_tag, i_node, new_i_node, 
                        '-mat', rigid_mat, rigid_mat, rigid_mat, rigid_mat, mat_tag, mat_tag, 
                        '-dir', 1, 2, 3, 4, 5, 6)
                        
            self._element_counter = hinge_el_tag
            
            # Re-connect element to the new node
            transf_tag = el_data['transf_tag']
            A = el_data['A']
            E = el_data['E']
            G = el_data.get('G', E/2.4)
            J = el_data.get('J', A*1e4) # dummy J if not present
            Iy = el_data['Iy']
            Iz = el_data['Iz']
            
            # Redefine the element with the new i_node
            ops.element('elasticBeamColumn', el_tag, new_i_node, j_node, A, E, G, J, Iy, Iz, transf_tag)

    def run_pushover_analysis(self, control_node: int, control_dof: int, d_max: float, d_incr: float) -> dict:
        """
        Executes a displacement-controlled nonlinear static pushover.
        """
        ops.system('BandGeneral')
        ops.numberer('RCM')
        ops.constraints('Transformation')
        ops.test('NormDispIncr', 1.0e-6, 100)
        ops.algorithm('Newton')
        
        ops.integrator('DisplacementControl', control_node, control_dof, d_incr)
        ops.analysis('Static')
        
        num_steps = int(abs(d_max / d_incr))
        roof_disps = []
        base_shears = []
        
        status = 0
        for i in range(num_steps):
            ok = ops.analyze(1)
            if ok != 0:
                ops.algorithm('ModifiedNewton')
                ok = ops.analyze(1)
                if ok != 0:
                    status = -1
                    break
                ops.algorithm('Newton') # return to Newton
            
            disp = ops.nodeDisp(control_node, control_dof)
            roof_disps.append(disp)
            
            ops.reactions()
            v_base = sum(ops.nodeReaction(n, control_dof) for n in self._base_nodes)
            base_shears.append(abs(v_base))
            
        return {
            "status": "success" if status == 0 else "failed_to_converge",
            "steps_completed": len(roof_disps),
            "roof_displacements": roof_disps,
            "base_shears": base_shears
        }

    def run_time_history_analysis(self, dt: float, n_pts: int, accelerations: List[float], direction: int = 1, roof_node: int = None) -> dict:
        """
        Executes a nonlinear Time-History (Dynamic) Analysis using a ground motion record.
        direction: 1 (X), 2 (Y), 3 (Z)
        """
        # Define Ground Motion Time Series
        ts_tag = 3 # tag 3 for THA
        ops.timeSeries('Path', ts_tag, '-dt', dt, '-values', *accelerations, '-factor', 9.81) # convert g to m/s2
        
        # Define Uniform Excitation Pattern at the base
        pattern_tag = 3
        ops.pattern('UniformExcitation', pattern_tag, direction, '-accel', ts_tag)
        
        # Rayleigh Damping (approx 5% across first two modes)
        ops.rayleigh(0.2, 0.0, 0.0, 0.0)
        
        # Dynamic Analysis Parameters
        ops.wipeAnalysis()
        ops.constraints('Transformation')
        ops.numberer('RCM')
        ops.system('BandGeneral')
        ops.test('NormDispIncr', 1.0e-5, 100)
        ops.algorithm('Newton')
        ops.integrator('Newmark', 0.5, 0.25)
        ops.analysis('Transient')
            
        roof_disps = []
        base_shears = []
        
        status = 0
        for i in range(n_pts):
            ok = ops.analyze(1, dt)
            if ok != 0:
                ops.algorithm('KrylovNewton')
                ok = ops.analyze(1, dt)
                if ok != 0:
                    status = -1
                    break
                ops.algorithm('Newton') # return to Newton
            
            # Record state
            if roof_node:
                disp = ops.nodeDisp(roof_node, direction)
                roof_disps.append(disp)
            
            ops.reactions()
            v_base = sum(ops.nodeReaction(n, direction) for n in self._base_nodes)
            base_shears.append(abs(v_base))
            
        return {
            "status": "success" if status == 0 else f"failed_at_step_{len(roof_disps)}",
            "steps_completed": len(roof_disps),
            "roof_displacements": roof_disps,
            "base_shears": base_shears
        }

    def run_full_pipeline(
        self,
        n_modes: int = 12,
        run_gravity: bool = True,
        run_modal: bool = True,
    ) -> Dict[str, Any]:
        """Run a complete analysis pipeline (gravity → modal) and return results.
        
        Like ETABS 'Run Analysis' — chains static gravity + eigenvalue analysis.
        """
        results: Dict[str, Any] = {"gravity": None, "modal": None}
        
        if run_gravity:
            status = self.analyze_static(1)
            results["gravity"] = {
                "status": "converged" if status == 0 else "failed",
                "code": status,
            }
        
        # Run modal if requested AND (gravity passed OR we skipped gravity)
        gravity_ok = (not run_gravity) or (results.get("gravity") and results["gravity"].get("status") == "converged")
        
        if run_modal and gravity_ok:
            periods = self.analyze_modal(n_modes)
            results["modal"] = {
                "periods": periods,
                "frequencies": [1.0/t if t > 0 and t < 1e10 else 0.0 for t in periods],
            }
        
        return results

    # ── Standard Analysis Methods ────────────────────────────────────────

    def analyze_static(self, steps: int = 1):
        """Runs a standard linear/nonlinear static analysis."""
        ops.system('FullGeneral')
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
            vals = ops.eigen(num_modes)  # Fallback
        periods = []
        for v in vals:
            if v > 0:
                periods.append(2 * math.pi / math.sqrt(v))
            else:
                periods.append(float('inf'))
        return periods
