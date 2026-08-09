# pyre-ignore-all-errors
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# ---------------------------------------------------------
# Base / Common Core
# ---------------------------------------------------------
class MaterialProps(BaseModel):
    fc: float = Field(25.0, gt=0, description="Concrete compressive strength in MPa")
    fy: float = Field(500.0, gt=0, description="Main steel yield strength in MPa")
    fy_v: float = Field(500.0, gt=0, description="Shear/transverse steel yield strength in MPa")

# ---------------------------------------------------------
# Beam Schemas
# ---------------------------------------------------------
class BeamDesignInput(BaseModel):
    width: float = Field(..., gt=0, description="Beam width (b) in mm")
    depth: float = Field(..., gt=0, description="Beam total depth (h) in mm")
    cover: float = Field(60.0, description="Distance from extreme tension fiber to centroid of tension reinforcement in mm")
    material: MaterialProps = Field(default_factory=lambda: MaterialProps(fc=25.0, fy=500.0, fy_v=500.0))

class BeamDesignForces(BaseModel):
    Mu: float = Field(0.0, description="Factored bending moment in kN-m")
    Vu: float = Field(0.0, description="Factored shear force in kN")

class BeamFlexureResult(BaseModel):
    As_req_mm2: float
    rho: float
    tension_controlled: bool
    compression_reinforcement_needed: bool
    status: str

class BeamShearResult(BaseModel):
    phi_Vc_kN: float = 0.0
    Vs_req_kN: float = 0.0
    Av_over_s_req: float = 0.0
    status: str

class BeamDesignResult(BaseModel):
    flexure: BeamFlexureResult
    shear: BeamShearResult
    detailing: Dict[str, Any]

# ---------------------------------------------------------
# Column Schemas
# ---------------------------------------------------------
class RebarLayer(BaseModel):
    depth: float = Field(..., description="Depth to layer from compression face in mm")
    As: float = Field(..., description="Area of steel in this layer in mm^2")

class ColumnDesignInput(BaseModel):
    width: float = Field(..., gt=0, description="Column width (b) in mm")
    depth: float = Field(..., gt=0, description="Column depth (h) in mm")
    material: MaterialProps = Field(
        default_factory=lambda: MaterialProps(fc=28.0, fy=420.0, fy_v=420.0)
    )
    rebar_layers: List[RebarLayer] = Field(
        default_factory=lambda: [
            RebarLayer(depth=50, As=800), # pyre-ignore[6]
            RebarLayer(depth=550, As=800) # pyre-ignore[6]
        ]
    )
    is_sway: bool = Field(True, description="Whether the frame is a sway frame")
    klu_over_r: float = Field(10.0, description="Slenderness ratio")

class ColumnDesignForces(BaseModel):
    Pu: float = Field(0.0, description="Factored axial load in kN")
    Mux: float = Field(0.0, description="Factored major axis moment in kN-m")
    Muy: float = Field(0.0, description="Factored minor axis moment in kN-m")
    Vu: float = Field(0.0, description="Factored shear force in kN")

class PMPoint(BaseModel):
    P: float
    M: float

class ColumnInteractionResult(BaseModel):
    points: List[PMPoint]

class BiaxialCheckResult(BaseModel):
    status: str
    ratio: float
    Mrx: float
    Mry: float

class ColumnShearResult(BaseModel):
    Vc: float
    Vs: float
    phiVn: float
    status: str

class ColumnDesignResult(BaseModel):
    interaction_diagram: ColumnInteractionResult
    shear: ColumnShearResult
    biaxial_check: BiaxialCheckResult
    detailing: Dict[str, Any]

# ---------------------------------------------------------
# Slab Schemas
# ---------------------------------------------------------
class SlabDesignInput(BaseModel):
    thickness: float = Field(..., gt=0, description="Slab thickness (t) or (h) in mm")
    cover: float = Field(20.0, description="Clear cover in mm")
    bar_dia: float = Field(10.0, description="Assumed bar diameter in mm")
    material: MaterialProps = Field(default_factory=lambda: MaterialProps(fc=25.0, fy=500.0, fy_v=500.0))

class OneWaySlabForces(BaseModel):
    Mu: float = Field(0.0, description="Factored bending moment in kN-m/m")

class OneWaySlabResult(BaseModel):
    As_req_mm2_m: float
    As_flexure_mm2_m: float
    As_temp_mm2_m: float
    s_max_mm: float
    d_effective_mm: float
    status: str

class TwoWaySlabForces(BaseModel):
    Mu_x: float = Field(0.0, description="Factored bending moment along X in kN-m/m")
    Mu_y: float = Field(0.0, description="Factored bending moment along Y in kN-m/m")

class TwoWaySlabResult(BaseModel):
    As_x_req_mm2_m: float
    As_y_req_mm2_m: float

class PunchingShearInput(BaseModel):
    Vu: float = Field(..., description="Factored shear force in kN")
    Mu_unbalanced: float = Field(0.0, description="Unbalanced moment in kN-m")
    c1: float = Field(..., description="Column dimension 1 in mm")
    c2: float = Field(..., description="Column dimension 2 in mm")
    location: str = Field("interior", description="Column location: interior, edge, or corner")

class PunchingShearResult(BaseModel):
    status: str
    b0_mm: float
    phi_Vc_kN: float
    Vu_kN: float

class PTSlabInput(BaseModel):
    P_eff: float
    sag: float
    span: float
    dead_load: float

class PTLoadResult(BaseModel):
    w_up: float
    net_load: float

class StripStressInput(BaseModel):
    P: float
    M: float
    A: float
    Z: float

class StripStressResult(BaseModel):
    f_top: float
    f_bot: float
    status: str

# ---------------------------------------------------------
# Wall Schemas
# ---------------------------------------------------------
class ShearWallInput(BaseModel):
    lw: float = Field(..., description="Wall length in mm")
    hw: float = Field(..., description="Wall height in mm")
    tw: float = Field(..., description="Wall thickness in mm")
    material: MaterialProps = Field(default_factory=lambda: MaterialProps(fc=25.0, fy=500.0, fy_v=500.0))

class ShearWallForces(BaseModel):
    Vu: float = Field(0.0, description="Factored shear force in kN")
    Pu: float = Field(0.0, description="Factored axial load in kN")
    Mu: float = Field(0.0, description="Factored moment in kN-m")

class ShearWallShearResult(BaseModel):
    status: str
    phi_Vc_kN: float
    req_rho_t: float
    req_rho_l: float

class SlenderWallInput(BaseModel):
    lw: float
    hw: float
    tw: float
    As: float = Field(..., description="Area of vertical steel in mm^2")
    material: MaterialProps = Field(default_factory=lambda: MaterialProps(fc=25.0, fy=500.0, fy_v=500.0))

class SlenderWallResult(BaseModel):
    phiMn_kNm: float
    status: str

class RetainingWallInput(BaseModel):
    height_m: float = 3.0
    soil_gamma: float = 18.0
    soil_phi: float = 30.0
    surcharge_kpa: float = 0.0
    water_table_depth_m: Optional[float] = None

class LateralPressurePoint(BaseModel):
    depth: float
    pressure_kpa: float

class RetainingWallResult(BaseModel):
    pressures: List[LateralPressurePoint]

# ---------------------------------------------------------
# Footing Schemas
# ---------------------------------------------------------
class IsolatedFootingInput(BaseModel):
    q_allow: float = Field(..., description="Allowable soil pressure in kPa")
    cover: float = Field(75.0, description="Clear cover in mm")
    material: MaterialProps = Field(default_factory=lambda: MaterialProps(fc=25.0, fy=500.0, fy_v=500.0))

class IsolatedFootingForces(BaseModel):
    P: float = Field(0.0, description="Unfactored axial load in kN")
    Mx: float = Field(0.0, description="Unfactored moment about X in kN-m")
    My: float = Field(0.0, description="Unfactored moment about Y in kN-m")

class IsolatedFootingResult(BaseModel):
    status: str
    L_m: float
    B_m: float
    t_mm: float
    q_max_kPa: float
    As_req_mm2: float

class CombinedFootingInput(BaseModel):
    c_c_dist: float = Field(..., description="Center-to-center distance between columns in m")
    q_allow: float = Field(..., description="Allowable soil pressure in kPa")
    material: MaterialProps = Field(default_factory=lambda: MaterialProps(fc=25.0, fy=500.0, fy_v=500.0))

class CombinedFootingForces(BaseModel):
    P1: float = Field(0.0, description="Load on column 1 in kN")
    P2: float = Field(0.0, description="Load on column 2 in kN")

class CombinedFootingResult(BaseModel):
    L_m: float
    B_m: float
    qu_kPa: float
    Mu_top_kNm: float

class RaftFoundationInput(BaseModel):
    thickness: float = Field(..., description="Raft thickness in mm")
    cover: float = Field(75.0, description="Clear cover in mm")
    material: MaterialProps = Field(default_factory=lambda: MaterialProps(fc=25.0, fy=500.0, fy_v=500.0))

class RaftFoundationForces(BaseModel):
    Mu_x: float = Field(0.0, description="Factored moment along X in kN-m/m")
    Mu_y: float = Field(0.0, description="Factored moment along Y in kN-m/m")

# ---------------------------------------------------------
# Miscellaneous Schemas
# ---------------------------------------------------------
class StaircaseInput(BaseModel):
    going: float = Field(..., description="Stair going in m")
    rise: float = Field(..., description="Stair rise in m")
    tread: float = Field(..., description="Stair tread in m")
    width: float = Field(..., description="Stair width in m")
    material: MaterialProps = Field(default_factory=lambda: MaterialProps(fc=25.0, fy=500.0, fy_v=500.0))

class StaircaseForces(BaseModel):
    LL: float = Field(0.0, description="Live Load in kPa")

class StaircaseResult(BaseModel):
    waist_slab_t_mm: float
    design_load_wu_kPa: float
    Mu_kNm_m: float
    As_req_mm2_m: float

class DomeInput(BaseModel):
    radius: float = Field(..., description="Dome radius in m")
    thickness: float = Field(..., description="Dome thickness in mm")
    theta_edge_deg: float = Field(..., description="Edge angle in degrees")

class DomeForces(BaseModel):
    DL: float = Field(0.0, description="Dead load in kPa")
    LL: float = Field(0.0, description="Live load in kPa")

class DomeResult(BaseModel):
    meridional_force_N_phi_kN_m: float
    hoop_force_N_theta_kN_m: float
    ring_beam_tension_kN: float
    As_ring_beam_mm2: float

class PileInput(BaseModel):
    diameter: float = Field(..., description="Pile diameter in m")
    length: float = Field(..., description="Pile length in m")
    soil_type: str = Field(..., description="Soil type: clay or sand")
    cu: float = Field(50.0, description="Undrained shear strength in kPa")
    phi: float = Field(30.0, description="Friction angle in degrees")
    gamma: float = Field(18.0, description="Soil unit weight")
    
class PileCapacityResult(BaseModel):
    Qs: float
    Qb: float
    Qu: float
    Q_allowable: float

class PileCapInput(BaseModel):
    pile_capacity: float
    total_load: float
    B: float
    H: float
    material: MaterialProps = Field(default_factory=lambda: MaterialProps(fc=25.0, fy=500.0, fy_v=500.0))

class PileCapResult(BaseModel):
    required_piles: int
    actual_piles: int
    status: str
    shear_status: str
    V_u_kN: float
    phi_Vn_kN: float

class CFSWidthInput(BaseModel):
    w: float
    t: float
    f: float
    E: float = 203000.0

class CFSColumnInput(BaseModel):
    A: float
    r: float
    L: float
    fy: float
    E: float = 203000.0
