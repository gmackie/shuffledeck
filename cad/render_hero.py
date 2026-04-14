# render_hero.py — Export a visually coherent assembly GLB for the landing page.
# Includes bought hardware (motors, rails, belts) and per-part colors.
#
# Run: source .venv/bin/activate && cd cad && python render_hero.py

from __future__ import annotations

import sys
from pathlib import Path

CAD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CAD_DIR))

from build123d import *
import build123d as bd

from chassis.chassis import build_chassis, chassis_info, PLATE_THICKNESS
from feeder.candidate_a_friction_retard import build_feeder_candidate_a
from bin_bank import build_bin_bank, bin_bank_info
from selector.selector import build_selector
from recombine.recombine import build_recombine
from output.output import build_output_tray
from hardware import (
    build_nema17,
    build_mgn12h_rail,
    build_gt2_pulley,
    build_belt_segment,
)
from constants import NEMA17_BODY_LENGTH_STANDARD, NEMA17_FACE

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
_ci = chassis_info()
_bb = bin_bank_info()
DATUM_A = _ci["datum_a_z"]          # top of base plate (Z=5)
FEEDER_X = 50.0                     # feeder center X
BIN_BANK_X = _ci["bin_bank_zone"][0]  # 105
BIN_BANK_CENTER_X = BIN_BANK_X + _bb["bank_total_width"] / 2  # ~390
OUTPUT_X = _ci["output_zone"][0]    # 680

# Y positioning: modules center on the chassis depth
CHASSIS_DEPTH = _ci["chassis_depth"]  # 140
MODULE_Y = CHASSIS_DEPTH / 2 - _bb["bank_depth"] / 2  # center bins in chassis

# Rail Z heights
SELECTOR_RAIL_Z = DATUM_A + _bb["bank_height"] + 5  # above bin bank top
RECOMBINE_RAIL_Z = DATUM_A  # at base plate level, behind the bin bank
RECOMBINE_Y = MODULE_Y + _bb["bank_depth"] + 10  # behind the bin bank

# Motor positions — at the ends of each rail
MOTOR_LEN = NEMA17_BODY_LENGTH_STANDARD  # 40mm

print("Building all parts...\n")

# ---------------------------------------------------------------------------
# Build printed parts
# ---------------------------------------------------------------------------
print("  Printed parts...")
chassis = build_chassis()
feeder = build_feeder_candidate_a()
bin_bank = build_bin_bank()
selector_carriage = build_selector()
recombine = build_recombine()
output_tray = build_output_tray()

# ---------------------------------------------------------------------------
# Build hardware
# ---------------------------------------------------------------------------
print("  Hardware (motors, rails, pulleys)...")

# Selector rail — runs along X above the bin bank
sel_rail_length = _bb["bank_total_width"] + 60  # 630mm, some overhang
sel_rail = build_mgn12h_rail(sel_rail_length)

# Recombine rail — runs along X below/behind the bin bank
rec_rail_length = _bb["bank_total_width"] + 60
rec_rail = build_mgn12h_rail(rec_rail_length)

# NEMA17 motors (4 total)
feeder_motor = build_nema17()
selector_motor = build_nema17()
recombine_x_motor = build_nema17()
recombine_z_motor = build_nema17(body_length=34)  # pancake for Z

# GT2 pulleys
sel_drive_pulley = build_gt2_pulley()
sel_idler_pulley = build_gt2_pulley()
rec_drive_pulley = build_gt2_pulley()
rec_idler_pulley = build_gt2_pulley()

print("  Belt segments...")
# Belt paths (simple straight segments, top and bottom runs)
sel_belt_z = SELECTOR_RAIL_Z + 14  # belt height on selector
sel_motor_x = BIN_BANK_X - 30
sel_idler_x = BIN_BANK_X + _bb["bank_total_width"] + 30
sel_belt_y = MODULE_Y + _bb["bank_depth"] / 2

sel_belt_top = build_belt_segment(
    (sel_motor_x, sel_belt_y, sel_belt_z),
    (sel_idler_x, sel_belt_y, sel_belt_z),
)
sel_belt_bot = build_belt_segment(
    (sel_motor_x, sel_belt_y, sel_belt_z - 8),
    (sel_idler_x, sel_belt_y, sel_belt_z - 8),
)

rec_belt_z = RECOMBINE_RAIL_Z + 14
rec_motor_x = sel_motor_x
rec_idler_x = sel_idler_x
rec_belt_y = RECOMBINE_Y + 6

rec_belt_top = build_belt_segment(
    (rec_motor_x, rec_belt_y, rec_belt_z),
    (rec_idler_x, rec_belt_y, rec_belt_z),
)
rec_belt_bot = build_belt_segment(
    (rec_motor_x, rec_belt_y, rec_belt_z - 8),
    (rec_idler_x, rec_belt_y, rec_belt_z - 8),
)

# ---------------------------------------------------------------------------
# Position everything
# ---------------------------------------------------------------------------
print("\nPositioning assembly...\n")

# Helper: orient motor with shaft pointing +Z, then rotate/translate to mounting face
def place_motor_x_end(motor, x, y, z, facing_positive_x=True):
    """Place a motor at the end of an X-axis rail, shaft pointing along X."""
    if facing_positive_x:
        return motor.moved(Location((x, y, z), (0, 90, 0)))
    else:
        return motor.moved(Location((x, y, z), (0, -90, 0)))


assembly_parts = []

# --- Chassis (base) ---
assembly_parts.append(("chassis", chassis.moved(Location((0, 0, 0)))))

# --- Bin bank (centered in bin zone) ---
assembly_parts.append(("bin_bank", bin_bank.moved(
    Location((BIN_BANK_CENTER_X, MODULE_Y + _bb["bank_depth"] / 2, DATUM_A))
)))

# --- Feeder (at feeder zone) ---
assembly_parts.append(("feeder", feeder.moved(
    Location((FEEDER_X, MODULE_Y + _bb["bank_depth"] / 2, DATUM_A))
)))

# --- Output tray ---
assembly_parts.append(("output", output_tray.moved(
    Location((OUTPUT_X + 50, MODULE_Y + _bb["bank_depth"] / 2, DATUM_A))
)))

# --- Selector rail (above bin bank, along X) ---
assembly_parts.append(("sel_rail", sel_rail.moved(
    Location((BIN_BANK_CENTER_X, MODULE_Y + _bb["bank_depth"] / 2, SELECTOR_RAIL_Z))
)))

# --- Selector carriage (on the rail, positioned at bin 3 for visual interest) ---
sel_carriage_x = BIN_BANK_X + 3 * _bb["cell_width"] + _bb["cell_width"] / 2
assembly_parts.append(("selector", selector_carriage.moved(
    Location((sel_carriage_x, MODULE_Y + _bb["bank_depth"] / 2, SELECTOR_RAIL_Z + 18))
)))

# --- Selector motor (at -X end of rail) ---
assembly_parts.append(("sel_motor", selector_motor.moved(
    Location((sel_motor_x - 5, MODULE_Y + _bb["bank_depth"] / 2, SELECTOR_RAIL_Z + 10),
             (0, 90, 0))
)))

# --- Selector pulleys ---
assembly_parts.append(("sel_drive_pulley", sel_drive_pulley.moved(
    Location((sel_motor_x, sel_belt_y, sel_belt_z - 4))
)))
assembly_parts.append(("sel_idler_pulley", sel_idler_pulley.moved(
    Location((sel_idler_x, sel_belt_y, sel_belt_z - 4))
)))

# --- Selector belts ---
assembly_parts.append(("sel_belt_top", sel_belt_top))
assembly_parts.append(("sel_belt_bot", sel_belt_bot))

# --- Recombine rail (behind bin bank, along X) ---
assembly_parts.append(("rec_rail", rec_rail.moved(
    Location((BIN_BANK_CENTER_X, RECOMBINE_Y, RECOMBINE_RAIL_Z))
)))

# --- Recombine carriage (on the rail, at bin 5) ---
rec_carriage_x = BIN_BANK_X + 5 * _bb["cell_width"] + _bb["cell_width"] / 2
assembly_parts.append(("recombine", recombine.moved(
    Location((rec_carriage_x, RECOMBINE_Y, RECOMBINE_RAIL_Z + 18))
)))

# --- Recombine X motor (at -X end of rail) ---
assembly_parts.append(("rec_x_motor", recombine_x_motor.moved(
    Location((rec_motor_x - 5, RECOMBINE_Y, RECOMBINE_RAIL_Z + 10),
             (0, 90, 0))
)))

# --- Recombine Z motor (on the carriage, vertical) ---
assembly_parts.append(("rec_z_motor", recombine_z_motor.moved(
    Location((rec_carriage_x + 30, RECOMBINE_Y, RECOMBINE_RAIL_Z + 25))
)))

# --- Recombine pulleys ---
assembly_parts.append(("rec_drive_pulley", rec_drive_pulley.moved(
    Location((rec_motor_x, rec_belt_y, rec_belt_z - 4))
)))
assembly_parts.append(("rec_idler_pulley", rec_idler_pulley.moved(
    Location((rec_idler_x, rec_belt_y, rec_belt_z - 4))
)))

# --- Recombine belts ---
assembly_parts.append(("rec_belt_top", rec_belt_top))
assembly_parts.append(("rec_belt_bot", rec_belt_bot))

# --- Feeder motor (below feeder, shaft pointing up) ---
assembly_parts.append(("feed_motor", feeder_motor.moved(
    Location((FEEDER_X, MODULE_Y + _bb["bank_depth"] / 2, DATUM_A - MOTOR_LEN),
             (180, 0, 0))
)))

# ---------------------------------------------------------------------------
# Color map — part name prefix -> hex color
# ---------------------------------------------------------------------------
COLOR_MAP = {
    "chassis":      (0.15, 0.15, 0.17),      # dark charcoal
    "bin_bank":     (0.22, 0.24, 0.22),       # dark gray-green
    "feeder":       (0.06, 0.45, 0.32),       # emerald green (accent)
    "selector":     (0.06, 0.45, 0.32),       # emerald green (accent)
    "output":       (0.06, 0.45, 0.32),       # emerald green (accent)
    "recombine":    (0.06, 0.45, 0.32),       # emerald green (accent)
    "sel_rail":     (0.55, 0.56, 0.58),       # steel/silver
    "rec_rail":     (0.55, 0.56, 0.58),       # steel/silver
    "sel_motor":    (0.12, 0.12, 0.14),       # near-black (motor body)
    "rec_x_motor":  (0.12, 0.12, 0.14),       # near-black
    "rec_z_motor":  (0.12, 0.12, 0.14),       # near-black
    "feed_motor":   (0.12, 0.12, 0.14),       # near-black
    "sel_belt":     (0.95, 0.62, 0.07),       # orange (GT2 belt)
    "rec_belt":     (0.95, 0.62, 0.07),       # orange
    "sel_drive":    (0.7, 0.7, 0.72),         # light silver (pulley)
    "sel_idler":    (0.7, 0.7, 0.72),
    "rec_drive":    (0.7, 0.7, 0.72),
    "rec_idler":    (0.7, 0.7, 0.72),
}

def get_color(name: str) -> tuple:
    """Look up color by prefix match."""
    for prefix, color in COLOR_MAP.items():
        if name.startswith(prefix):
            return color
    return (0.5, 0.5, 0.5)  # default gray

# ---------------------------------------------------------------------------
# Export as colored GLTF (binary GLB)
# ---------------------------------------------------------------------------
print("Exporting colored GLB...\n")

# Build123d export_gltf doesn't support per-part colors directly.
# We export each part as a separate GLTF node via the names parameter.
# The three.js viewer will apply colors based on node names.

# For now, export the full assembly as one GLB and let the viewer colorize.
# We'll embed color info in the node names.

all_shapes = []
for name, shape in assembly_parts:
    all_shapes.append(shape)

assembly = Compound(children=all_shapes)

out_path = CAD_DIR.parent / "site" / "assembly.glb"
export_gltf(assembly, str(out_path), binary=True)
print(f"Exported: {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")

# Also export a name map as JSON for the viewer to use for coloring
import json
name_map = {i: name for i, (name, _) in enumerate(assembly_parts)}
color_data = {name: list(get_color(name)) for name, _ in assembly_parts}
meta_path = CAD_DIR.parent / "site" / "assembly-colors.json"
with open(meta_path, "w") as f:
    json.dump({
        "parts": [name for name, _ in assembly_parts],
        "colors": color_data,
    }, f, indent=2)
print(f"Color map: {meta_path}")

print(f"\nAssembly: {len(assembly_parts)} parts")
bb = assembly.bounding_box()
print(f"Bounding box: {bb.size.X:.0f} × {bb.size.Y:.0f} × {bb.size.Z:.0f} mm")
print(f"Center: ({bb.center().X:.0f}, {bb.center().Y:.0f}, {bb.center().Z:.0f})")
print("\nDone.")
