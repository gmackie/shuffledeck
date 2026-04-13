# render_setup.py — Export assembled card shuffler CAD models for marketing renders.
# Requires: pip install build123d
#
# Run:  cd cad && python render_setup.py
#
# Exports STEP files into cad/renders/:
#   assembly_full.step       — complete assembly, all parts positioned
#   assembly_exploded.step   — exploded view (parts offset along Z)
#   feeder_detail.step       — feeder + Candidate A singulation
#   bin_bank_detail.step     — bin bank standalone

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the cad/ directory is on the path for imports
CAD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CAD_DIR))

import build123d as bd
from build123d import (
    Compound,
    Location,
    Pos,
    Rot,
    export_step,
)

# ---------------------------------------------------------------------------
# Import all build functions
# ---------------------------------------------------------------------------
from chassis.chassis import build_chassis, chassis_info
from feeder.feeder import build_feeder
from feeder.candidate_a_friction_retard import build_feeder_candidate_a
from bin_bank import build_bin_bank, bin_bank_info
from selector.selector import build_selector
from recombine.recombine import build_recombine
from output.output import build_output_tray
from chassis.chassis import PLATE_THICKNESS

# ---------------------------------------------------------------------------
# Assembly positions — based on chassis zone layout
# ---------------------------------------------------------------------------
# The chassis defines zones along X. We use chassis_info() to get the actual
# computed values, but also define the Datum A Z offset (top of base plate)
# so modules sit on top of the chassis.

_ci = chassis_info()
_bb = bin_bank_info()

DATUM_A_Z = _ci["datum_a_z"]  # top of base plate (Z where modules sit)

# Module positions (X, Y, Z) — X is the long axis of the machine
# Y=0 is Datum B (left side rail inner face). Most modules align near Y=0.
POSITIONS = {
    "chassis":   (0, 0, 0),
    "feeder":    (_ci["feeder_zone"][0] + 50.0, 0, DATUM_A_Z),
    "feeder_a":  (_ci["feeder_zone"][0] + 50.0, 0, DATUM_A_Z),
    "bin_bank":  (_ci["bin_bank_zone"][0], 0, DATUM_A_Z),
    "selector":  (_ci["bin_bank_zone"][0], 0, DATUM_A_Z + _bb["bank_height"]),
    "recombine": (_ci["bin_bank_zone"][0], _bb["bank_depth"] + 5.0, DATUM_A_Z),
    "output":    (_ci["output_zone"][0], 0, DATUM_A_Z),
}

# Exploded view Z offsets — layered for visual clarity
EXPLODE_Z_OFFSETS = {
    "chassis":   0,
    "feeder":    70,
    "feeder_a":  70,
    "bin_bank":  140,
    "selector":  220,
    "recombine": 140,
    "output":    70,
}


# ---------------------------------------------------------------------------
# Build all parts
# ---------------------------------------------------------------------------

def build_all_parts() -> dict[str, bd.Shape]:
    """Build every module and return as a name->Part dict."""
    print("Building all parts...")

    print("  chassis...")
    chassis = build_chassis()

    print("  feeder...")
    feeder = build_feeder()

    print("  feeder candidate A...")
    feeder_a = build_feeder_candidate_a()

    print("  bin bank...")
    bin_bank = build_bin_bank()

    print("  selector...")
    selector = build_selector()

    print("  recombine...")
    recombine = build_recombine()

    print("  output tray...")
    output = build_output_tray()

    return {
        "chassis": chassis,
        "feeder": feeder,
        "feeder_a": feeder_a,
        "bin_bank": bin_bank,
        "selector": selector,
        "recombine": recombine,
        "output": output,
    }


def position_part(part: bd.Shape, name: str, explode: bool = False) -> bd.Shape:
    """Move a part to its assembly position, optionally with exploded Z offset."""
    x, y, z = POSITIONS[name]
    if explode:
        z += EXPLODE_Z_OFFSETS.get(name, 0)
    return part.moved(Location((x, y, z)))


def make_assembly(parts: dict, explode: bool = False) -> bd.Compound:
    """Position all parts and combine into a single Compound."""
    positioned = []
    for name, part in parts.items():
        positioned.append(position_part(part, name, explode=explode))
    return Compound(children=positioned)


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

RENDERS_DIR = CAD_DIR / "renders"


def export_render(shape, filename: str) -> Path:
    """Export a shape to STEP in the renders directory."""
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RENDERS_DIR / filename
    export_step(shape, str(out_path))
    print(f"  Exported: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Card Shuffler — Render Setup\n")
    print(f"Chassis info:")
    for k, v in _ci.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.1f} mm")
        elif isinstance(v, tuple):
            print(f"  {k}: {v}")
        else:
            print(f"  {k}: {v}")
    print()

    parts = build_all_parts()
    print()

    # 1. Full assembly
    print("[assembly_full]")
    assembly = make_assembly(parts, explode=False)
    export_render(assembly, "assembly_full.step")

    # 2. Exploded view
    print("[assembly_exploded]")
    exploded = make_assembly(parts, explode=True)
    export_render(exploded, "assembly_exploded.step")

    # 3. Feeder detail — feeder + candidate A singulation together
    print("[feeder_detail]")
    feeder_detail = Compound(children=[
        parts["feeder"],
        parts["feeder_a"].moved(Location((0, 0, 0))),
    ])
    export_render(feeder_detail, "feeder_detail.step")

    # 4. Bin bank detail — standalone
    print("[bin_bank_detail]")
    export_render(parts["bin_bank"], "bin_bank_detail.step")

    # 5. Print rendering instructions
    print()
    print("=" * 72)
    print("RENDERING INSTRUCTIONS")
    print("=" * 72)
    print("""
All STEP files are in: cad/renders/

--- FreeCAD (Raytracing / Render Workbench) ---
1. Open FreeCAD >= 0.21
2. File > Import > select the .step file
3. Switch to the Render workbench (install via Addon Manager if needed)
4. Create a new render project (Cycles, LuxCore, or Appleseed)
5. Add all visible shapes to the project
6. Assign materials: light gray for chassis, darker gray for bins,
   accent color for feeder/selector mechanisms
7. Set up a 3-point lighting rig and render at 2048x2048 or higher

--- Blender (via CAD Sketcher or STEP importer) ---
1. Install the "CAD Sketcher" addon or "Import STEP" addon from
   https://github.com/30350n/blender_step_importer
2. File > Import > STEP (.step) > select the file
3. The assembly will import as separate mesh objects
4. Assign materials in the Shader Editor:
   - Chassis: matte light aluminum
   - Bin bank: semi-gloss dark gray
   - Feeder/selector: accent blue or orange
   - Output tray: same as chassis
5. Use an HDRI environment for realistic lighting
6. Set camera and render with Cycles at 2048x2048+

--- CadQuery Jupyter Viewer (quick preview) ---
1. pip install cadquery jupyter-cadquery
2. In a Jupyter notebook:
     import cadquery as cq
     from jupyter_cadquery import show
     result = cq.importers.importStep("cad/renders/assembly_full.step")
     show(result)
3. Use mouse to orbit, zoom, and inspect the assembly

--- OCP CAD Viewer (Build123d native, recommended for quick checks) ---
1. pip install ocp-vscode   (if using VS Code)
   or: pip install ocp-cad-viewer
2. In a Python script or notebook:
     from ocp_vscode import show
     # ... build parts as in this script ...
     show(assembly)

--- Recommended Camera Angles for Marketing ---

  3/4 Hero Shot (primary marketing image):
    Camera position: (1200, -800, 600) mm
    Look-at: center of bin bank (~(400, 50, 30))
    This shows the full machine from a high front-right angle,
    revealing the feeder, bin bank, and output tray in one frame.

  Top-Down Overview:
    Camera position: (400, 50, 1000) mm
    Look-at: (400, 50, 0)
    Orthographic or long-focal-length perspective.
    Great for showing the card flow path from feeder to output.

  Feeder Detail (close-up):
    Camera position: (80, -120, 100) mm
    Look-at: (50, 0, 30)
    Tight shot on the singulation mechanism and feed rollers.

  Bin Bank Detail:
    Camera position: (400, -200, 200) mm
    Look-at: center of bin bank
    Shows the 8-bin array with funnel entries visible.

  Exploded View (technical illustration):
    Use assembly_exploded.step
    Camera position: (1200, -1000, 800) mm
    Look-at: center of assembly
    Shows layered construction: chassis -> modules -> selector on top.
""")

    print("Done. Render STEP files are ready in cad/renders/\n")


if __name__ == "__main__":
    main()
