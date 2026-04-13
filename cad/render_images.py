# render_images.py — Export assembly as GLTF for browser-based 3D viewing
# and generate SVG technical views for the landing page.
#
# Requires: pip install build123d
# Run: cd cad && python render_images.py

from __future__ import annotations

import sys
from pathlib import Path

CAD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CAD_DIR))

from build123d import *
import build123d as bd

# Import all build functions
from chassis.chassis import build_chassis, chassis_info, PLATE_THICKNESS
from feeder.candidate_a_friction_retard import build_feeder_candidate_a
from bin_bank import build_bin_bank, bin_bank_info
from selector.selector import build_selector
from recombine.recombine import build_recombine
from output.output import build_output_tray

RENDER_DIR = CAD_DIR / "renders"
RENDER_DIR.mkdir(exist_ok=True)

_ci = chassis_info()
_bb = bin_bank_info()
DATUM_A_Z = _ci["datum_a_z"]

print("Building parts for GLTF export...\n")

# Build all parts
chassis = build_chassis()
feeder = build_feeder_candidate_a()
bin_bank = build_bin_bank()
selector = build_selector()
recombine = build_recombine()
output_tray = build_output_tray()

# Position parts in assembly layout
feeder_x = 50.0
bin_bank_x = _ci["bin_bank_zone"][0]
selector_x = bin_bank_x
recombine_x = bin_bank_x
output_x = _ci["output_zone"][0]

parts = {
    "chassis": (chassis, Location((0, 0, 0))),
    "feeder": (feeder, Location((feeder_x, 20, DATUM_A_Z))),
    "bin_bank": (bin_bank, Location((bin_bank_x, 20, DATUM_A_Z))),
    "selector": (selector, Location((selector_x, 20, DATUM_A_Z + 25))),
    "recombine": (recombine, Location((recombine_x, 20, DATUM_A_Z))),
    "output_tray": (output_tray, Location((output_x, 20, DATUM_A_Z))),
}

# Export each part as individual GLTF
for name, (part, loc) in parts.items():
    moved = part.moved(loc)
    path = RENDER_DIR / f"{name}.glb"
    try:
        export_gltf(moved, str(path))
        print(f"  {name}.glb exported")
    except Exception as e:
        print(f"  {name}.glb FAILED: {e}")

# Export full assembly as one GLTF
print("\nExporting full assembly GLTF...")
try:
    moved_parts = [part.moved(loc) for part, loc in parts.values()]
    assembly = Compound(children=moved_parts)
    assembly_path = RENDER_DIR / "assembly.glb"
    export_gltf(assembly, str(assembly_path))
    print(f"  assembly.glb exported ({assembly_path})")
except Exception as e:
    print(f"  assembly.glb FAILED: {e}")

# Export SVG views (top and front projections)
print("\nExporting SVG views...")
for name, (part, loc) in [("feeder", (feeder, Location())), ("bin_bank", (bin_bank, Location()))]:
    try:
        visible, hidden = part.project_to_viewport((100, -100, 80), viewport_up=(0, 0, 1))
        svg_path = RENDER_DIR / f"{name}_view.svg"
        max_dim = max(visible.bounding_box().size.X, visible.bounding_box().size.Y)
        exporter = ExportSVG(scale=200.0 / max_dim if max_dim > 0 else 1.0)
        exporter.add_layer("visible", line_weight=0.5)
        exporter.add_layer("hidden", line_weight=0.2, line_type=LineType.ISO_DOT)
        exporter.add_shape(visible, layer="visible")
        exporter.add_shape(hidden, layer="hidden")
        exporter.write(str(svg_path))
        print(f"  {name}_view.svg exported")
    except Exception as e:
        print(f"  {name}_view.svg FAILED: {e}")

print(f"\nAll renders in: {RENDER_DIR}/")
print("Use assembly.glb in a three.js viewer for interactive 3D on the landing page.")
