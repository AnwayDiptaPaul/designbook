import sys
import os

# Add the project root to sys.path so we can import core modules
sys.path.insert(0, os.path.abspath('.'))

from core.design.beam import BeamDesign
from core.design.slab_oneway import OneWaySlabDesign
from core.design.column import ColumnDesign
from core.design.shear_wall import ShearWallDesign

print("==================================")
print("TESTING BEAM DESIGN (Flexure)")
print("==================================")
res = BeamDesign.design_flexure(Mu=350.0, b=300.0, d=500.0, fc=28.0, fy=420.0)
print(f"Results (Mu=350): As_req = {res['As_req_mm2']:.2f} mm^2, Tension Controlled: {res['tension_controlled']}")

print("\n==================================")
print("TESTING ONE-WAY SLAB DESIGN")
print("==================================")
res_slab = OneWaySlabDesign.design_flexure(Mu=25.0, t=150.0, fc=28.0, fy=420.0, cover=20.0, bar_dia=10.0)
print(f"Results (Mu=25): As_req = {res_slab['As_req_mm2_m']:.2f} mm^2/m")

print("\n==================================")
print("TESTING COLUMN DESIGN (P-M Interaction)")
print("==================================")
# 400x400 Column, fc=28, fy=420
# Rebar: 8-20dia (4 on top, 4 on bottom for simplicity in test)
# Layer 1: d=60, As=1256 (4x314)
# Layer 2: d=340, As=1256 (4x314)
rebar = [
    {"depth": 60.0, "As": 1256.0},
    {"depth": 340.0, "As": 1256.0}
]
res_col = ColumnDesign.generate_interaction_diagram(b=400.0, h=400.0, fc=28.0, fy=420.0, rebar_layers=rebar)
print(f"Column 400x400 with 8-20 dia results:")
print(f"Pure Compression (phi_Pn_max): {res_col['points'][0]['P']:.2f} kN")
print(f"Pure Tension: {res_col['points'][-1]['P']:.2f} kN")
# Find approximate balanced point (max M)
balanced = max(res_col['points'], key=lambda x: x['M'])
print(f"Approx Balanced Point: P = {balanced['P']:.2f} kN, M = {balanced['M']:.2f} kN-m")

print("\n==================================")
print("TESTING SHEAR WALL DESIGN")
print("==================================")
# 3000mm long, 250mm thick wall. Vu = 1500 kN
res_sw = ShearWallDesign.design_shear(Vu=1500.0, Pu=2000.0, lw=3000.0, hw=9000.0, tw=250.0, fc=28.0, fy=420.0)
print(f"Shear Wall (Vu=1500kN) results:")
print(f"Status: {res_sw['status']}")
print(f"Req Horizontal Rho: {res_sw['req_rho_t']:.5f}")
print(f"Req Vertical Rho: {res_sw['req_rho_l']:.5f}")
