# Selector module — linear carriage that routes singulated cards to 8 bins.
# Requires: pip install build123d
#
# Architecture: A NEMA17 stepper drives a GT2 belt (or leadscrew) that
# positions a card-guide carriage over one of 8 bins along the X axis.
# A singulated card enters the guide channel from the feeder exit throat,
# slides down the channel, and drops through the bin's entry funnel.
#
# The carriage rides on a single MGN12H linear rail mounted parallel to
# the bin bank. Travel range covers all 8 bin positions (~570 mm bank).
#
# Parametric on: bin count, card clearance, rail geometry, belt attachment.
#
# Run standalone:  python selector.py
# Outputs:         selector.step

from __future__ import annotations

import sys
from pathlib import Path

# Allow importing shared constants when run standalone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import (
    BuildPart,
    Box,
    Cylinder,
    Location,
    Align,
    Axis,
    Mode,
    Plane,
    export_step,
    export_stl,
    Pos,
    Rot,
    chamfer,
    fillet,
)
import build123d as bd

from constants import (
    CARD_WIDTH,
    CARD_HEIGHT,
    CARD_THICKNESS,
    CARD_CLEARANCE_WIDTH,
    CARD_CLEARANCE_HEIGHT,
    BIN_COUNT,
    BIN_WALL_THICKNESS,
    BIN_SPACING,
    BIN_INTERNAL_HEIGHT,
    BIN_FLOOR_THICKNESS,
    BIN_ENTRY_FUNNEL_CHAMFER,
    NEMA17_FACE,
    NEMA17_HOLE_SPACING,
    NEMA17_HOLE_DIAMETER,
    NEMA17_PILOT_DIAMETER,
    NEMA17_PILOT_DEPTH,
    NEMA17_SHAFT_DIAMETER,
    PRINT_TOL_DEFAULT,
    PRINT_TOL_TIGHT,
    M3_CLEARANCE_HOLE,
    M3_HEATSET_BORE,
    M3_HEATSET_LENGTH,
)

# ---------------------------------------------------------------------------
# Selector parameters
# ---------------------------------------------------------------------------

# MGN12H linear rail reference dimensions
RAIL_WIDTH = 12.0                # mm — rail extrusion width
RAIL_HEIGHT = 8.0                # mm — rail extrusion height
MGN12H_BLOCK_WIDTH = 27.0       # mm — carriage block width
MGN12H_BLOCK_LENGTH = 39.8      # mm — carriage block length along rail
MGN12H_BLOCK_HEIGHT = 13.0      # mm — carriage block height (above rail)
MGN12H_HOLE_SPACING_X = 20.0    # mm — mounting hole spacing along rail
MGN12H_HOLE_SPACING_Y = 12.0    # mm — mounting hole spacing across rail (given as 27 between outer, but actual M3 pattern is 12mm across for MGN12H... we use the spec)
MGN12H_MOUNT_HOLE_DIA = 3.0     # mm — M3 mounting holes

# Card guide channel dimensions
GUIDE_WALL = 2.5                 # mm — guide channel wall thickness
GUIDE_CARD_CLEARANCE = 1.0      # mm per side — clearance around card in guide
GUIDE_ENTRY_FLARE = 3.0         # mm — flared opening at top for card entry

# Guide internal dimensions (card slides through in portrait orientation)
GUIDE_INT_WIDTH = CARD_WIDTH + 2 * GUIDE_CARD_CLEARANCE    # ~65.5 mm
GUIDE_INT_DEPTH = CARD_THICKNESS + 1.0                     # ~1.3 mm — sized for one card with clearance
GUIDE_HEIGHT = 30.0             # mm — vertical extent of card guide channel

# Carriage body
CARRIAGE_WALL = 4.0             # mm — structural wall thickness
CARRIAGE_LENGTH = 50.0          # mm — along X (rail direction), must clear one bin cell
CARRIAGE_DEPTH = GUIDE_INT_WIDTH + 2 * GUIDE_WALL + 2 * CARRIAGE_WALL  # mm — along Y
CARRIAGE_HEIGHT = 12.0          # mm — base plate height (above rail block)

# Belt attachment
BELT_CLAMP_WIDTH = 12.0         # mm
BELT_CLAMP_HEIGHT = 8.0         # mm
BELT_CLAMP_DEPTH = 20.0         # mm
BELT_SLOT_WIDTH = 7.0           # mm — GT2 6mm belt + clearance
BELT_SLOT_HEIGHT = 2.0          # mm — belt thickness + clearance

# Motor mount plate
MOTOR_MOUNT_THICKNESS = 5.0     # mm
MOTOR_MOUNT_STANDOFF = 10.0     # mm — clearance between motor face and rail end

# Bin bank geometry (derived, for travel calculation)
BIN_CELL_WIDTH = CARD_WIDTH + 2 * CARD_CLEARANCE_WIDTH + 2 * BIN_WALL_THICKNESS  # 69.5 mm
BIN_PITCH = BIN_CELL_WIDTH + BIN_SPACING  # 71.5 mm center-to-center
BANK_TOTAL_WIDTH = BIN_COUNT * BIN_CELL_WIDTH + (BIN_COUNT - 1) * BIN_SPACING  # 570 mm
SELECTOR_TRAVEL = (BIN_COUNT - 1) * BIN_PITCH  # ~500.5 mm — carriage travel from bin 0 to bin 7

# Rail length (travel + carriage length + motor mount clearance at each end)
RAIL_LENGTH = SELECTOR_TRAVEL + CARRIAGE_LENGTH + 2 * MOTOR_MOUNT_STANDOFF


def build_selector() -> bd.Part:
    """
    Build the selector module as a single part comprising:
      1. Card guide channel (open bottom for gravity drop)
      2. Carriage body with rail mounting features
      3. Belt/pulley clamp on carriage
      4. NEMA17 motor mount at the -X end of the rail
      5. Card entry slot at the top of the guide

    The carriage is built at the X=0 position (centered over bin 0).
    The motor mount is placed at the -X end of the rail.

    Coordinate convention (matches bin_bank.py):
      X — along the bin row (selector travel axis)
      Y — card depth direction (perpendicular to bin row)
      Z — vertical (gravity axis, cards drop in -Z)
    """

    # ── Derived positions ──────────────────────────────────────────
    # Rail sits above the bin bank; the carriage rides on top of the rail.
    # We build everything relative to the carriage center at Z=0.

    guide_ext_width = GUIDE_INT_WIDTH + 2 * GUIDE_WALL
    guide_ext_depth = GUIDE_INT_DEPTH + 2 * GUIDE_WALL

    with BuildPart() as selector:

        # ══════════════════════════════════════════════════════════════
        # 1. CARRIAGE BASE PLATE
        # ══════════════════════════════════════════════════════════════
        # Flat plate that bolts onto the MGN12H carriage block.
        Box(CARRIAGE_LENGTH, CARRIAGE_DEPTH, CARRIAGE_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

        # ── MGN12H mounting holes (4x M3 in rectangular pattern) ───
        for dx in (-MGN12H_HOLE_SPACING_X / 2, MGN12H_HOLE_SPACING_X / 2):
            for dy in (-MGN12H_HOLE_SPACING_Y / 2, MGN12H_HOLE_SPACING_Y / 2):
                with BuildPart(mode=Mode.SUBTRACT):
                    Cylinder(
                        radius=M3_CLEARANCE_HOLE / 2,
                        height=CARRIAGE_HEIGHT + 2.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    bd.Location((dx, dy, -1.0))

        # ══════════════════════════════════════════════════════════════
        # 2. CARD GUIDE CHANNEL
        # ══════════════════════════════════════════════════════════════
        # Vertical channel rising above the carriage. The card enters at
        # the top and drops out the open bottom into the bin below.
        # The guide is centered on the carriage in Y, with the narrow
        # (card-thickness) dimension along X.

        guide_base_z = CARRIAGE_HEIGHT  # sits on top of carriage plate
        guide_center_y = 0.0

        # Outer shell of the guide channel
        with BuildPart():
            Box(guide_ext_depth, guide_ext_width, GUIDE_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, guide_center_y, guide_base_z))

        # Inner cavity — the card slot (open at bottom by cutting through
        # into the carriage plate)
        with BuildPart(mode=Mode.SUBTRACT):
            Box(GUIDE_INT_DEPTH, GUIDE_INT_WIDTH, GUIDE_HEIGHT + CARRIAGE_HEIGHT + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, guide_center_y, -1.0))

        # ══════════════════════════════════════════════════════════════
        # 3. CARD ENTRY SLOT (flared top opening)
        # ══════════════════════════════════════════════════════════════
        # A wider funnel at the top of the guide to accept cards from
        # the feeder exit path. Flare widens both the card-thickness
        # and card-width dimensions for easier insertion.

        entry_flare_height = GUIDE_ENTRY_FLARE
        entry_flare_width = GUIDE_INT_WIDTH + 2 * GUIDE_ENTRY_FLARE
        entry_flare_depth = GUIDE_INT_DEPTH + 2 * GUIDE_ENTRY_FLARE
        entry_top_z = guide_base_z + GUIDE_HEIGHT

        with BuildPart(mode=Mode.SUBTRACT):
            Box(entry_flare_depth, entry_flare_width, entry_flare_height,
                align=(Align.CENTER, Align.CENTER, Align.MAX))
            bd.Location((0, guide_center_y, entry_top_z))

        # ══════════════════════════════════════════════════════════════
        # 4. BELT CLAMP ATTACHMENT
        # ══════════════════════════════════════════════════════════════
        # A block on the back (-Y side) of the carriage for clamping
        # the GT2 timing belt. The belt runs parallel to the rail (X axis).
        # A horizontal slot through the clamp accepts the belt; a pair of
        # M3 bolts clamp it from above.

        belt_clamp_y = -(CARRIAGE_DEPTH / 2 + BELT_CLAMP_DEPTH / 2)

        with BuildPart():
            Box(BELT_CLAMP_WIDTH, BELT_CLAMP_DEPTH, BELT_CLAMP_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, belt_clamp_y, 0))

        # Belt slot through the clamp (horizontal, along X)
        with BuildPart(mode=Mode.SUBTRACT):
            Box(BELT_CLAMP_WIDTH + 2.0, BELT_SLOT_WIDTH, BELT_SLOT_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, belt_clamp_y, BELT_CLAMP_HEIGHT / 2 - BELT_SLOT_HEIGHT / 2))

        # Belt clamp bolt holes (2x M3, spaced along X)
        belt_bolt_spacing = BELT_CLAMP_WIDTH - 4.0  # inset from edges
        for dx in (-belt_bolt_spacing / 2, belt_bolt_spacing / 2):
            with BuildPart(mode=Mode.SUBTRACT):
                Cylinder(
                    radius=M3_CLEARANCE_HOLE / 2,
                    height=BELT_CLAMP_HEIGHT + 2.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                bd.Location((dx, belt_clamp_y, -1.0))

        # ══════════════════════════════════════════════════════════════
        # 5. NEMA17 MOTOR MOUNT (at -X end of travel)
        # ══════════════════════════════════════════════════════════════
        # A vertical plate at the end of the rail for mounting the drive
        # motor. The motor shaft points along +X toward the carriage.
        # The plate stands on the same mounting plane as the rail.

        motor_mount_x = -(CARRIAGE_LENGTH / 2 + MOTOR_MOUNT_STANDOFF
                          + MOTOR_MOUNT_THICKNESS / 2)
        motor_plate_width = NEMA17_FACE + 12.0   # mm — plate width (Y)
        motor_plate_height = NEMA17_FACE + 12.0  # mm — plate height (Z)

        # Motor mount plate (vertical, facing +X)
        with BuildPart():
            Box(MOTOR_MOUNT_THICKNESS, motor_plate_width, motor_plate_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((motor_mount_x, 0, -MGN12H_BLOCK_HEIGHT))

        # NEMA17 mounting holes (4x M3, 31mm diagonal pattern)
        # Holes go through the plate along X axis
        motor_face_center_z = -MGN12H_BLOCK_HEIGHT + motor_plate_height / 2
        half_spacing = NEMA17_HOLE_SPACING / 2
        for dy in (-half_spacing, half_spacing):
            for dz in (-half_spacing, half_spacing):
                with BuildPart(mode=Mode.SUBTRACT):
                    Cylinder(
                        radius=M3_CLEARANCE_HOLE / 2,
                        height=MOTOR_MOUNT_THICKNESS + 2.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    # Rotate cylinder to point along X axis
                    bd.Location((motor_mount_x - MOTOR_MOUNT_THICKNESS / 2 - 1.0,
                                 dy, motor_face_center_z + dz))
                    bd.Rotation((0, 90, 0))

        # NEMA17 pilot recess (circular pocket on the +X face of the mount)
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(
                radius=(NEMA17_PILOT_DIAMETER / 2) + PRINT_TOL_TIGHT,
                height=NEMA17_PILOT_DEPTH + 0.5,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((motor_mount_x + MOTOR_MOUNT_THICKNESS / 2 - NEMA17_PILOT_DEPTH,
                         0, motor_face_center_z))
            bd.Rotation((0, 90, 0))

        # Shaft through-hole
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(
                radius=(NEMA17_SHAFT_DIAMETER / 2) + PRINT_TOL_TIGHT,
                height=MOTOR_MOUNT_THICKNESS + 4.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((motor_mount_x - MOTOR_MOUNT_THICKNESS / 2 - 1.0,
                         0, motor_face_center_z))
            bd.Rotation((0, 90, 0))

        # ── Motor mount base feet ──────────────────────────────────
        # Triangular gussets would be ideal but for scaffold simplicity
        # we add a base flange with M3 mounting holes for chassis attach.
        motor_base_width = motor_plate_width
        motor_base_depth = 20.0  # mm — extends in +X direction for stability
        motor_base_height = 4.0  # mm

        with BuildPart():
            Box(motor_base_depth, motor_base_width, motor_base_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((motor_mount_x + motor_base_depth / 2,
                         0, -MGN12H_BLOCK_HEIGHT))

        # Base mounting holes (4x M3 at corners of the flange)
        base_hole_inset_x = 5.0
        base_hole_inset_y = 8.0
        for dx_off in (-motor_base_depth / 2 + base_hole_inset_x,
                       motor_base_depth / 2 - base_hole_inset_x):
            for dy_off in (-motor_base_width / 2 + base_hole_inset_y,
                           motor_base_width / 2 - base_hole_inset_y):
                with BuildPart(mode=Mode.SUBTRACT):
                    Cylinder(
                        radius=M3_CLEARANCE_HOLE / 2,
                        height=motor_base_height + 2.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    bd.Location((motor_mount_x + motor_base_depth / 2 + dx_off,
                                 dy_off,
                                 -MGN12H_BLOCK_HEIGHT - 1.0))

    return selector.part


def selector_info() -> dict:
    """Return a summary dict of selector dimensions for other modules."""
    return {
        "carriage_length": CARRIAGE_LENGTH,
        "carriage_depth": CARRIAGE_DEPTH,
        "carriage_height": CARRIAGE_HEIGHT,
        "guide_int_width": GUIDE_INT_WIDTH,
        "guide_int_depth": GUIDE_INT_DEPTH,
        "guide_height": GUIDE_HEIGHT,
        "travel": SELECTOR_TRAVEL,
        "rail_length": RAIL_LENGTH,
        "bank_total_width": BANK_TOTAL_WIDTH,
        "bin_pitch": BIN_PITCH,
        "bin_count": BIN_COUNT,
    }


# -- Main --------------------------------------------------------------------
if __name__ == "__main__":
    part = build_selector()
    out_dir = Path(__file__).resolve().parent
    out_dir.mkdir(exist_ok=True)

    step_path = out_dir / "selector.step"
    export_step(part, str(step_path))
    print(f"Exported selector STEP to {step_path}")

    info = selector_info()
    print(f"\nSelector summary:")
    for k, v in info.items():
        unit = "mm" if isinstance(v, float) else ""
        print(f"  {k}: {v} {unit}")
