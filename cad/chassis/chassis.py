# Chassis / enclosure module — base plate, datum walls, and module mounting
# zones for the single-deck card shuffler.
# Requires: pip install build123d
#
# Implements the datum scheme from datum-tolerance-budget.md:
#   Datum A — base plate top surface (Z = 0 reference)
#   Datum B — left side rail inner face (Y reference)
#   Datum C — feeder end stop inner face (X = 0 reference)
#
# The chassis is split into 3 printable sections that bolt together with
# alignment dowel pins at each joint. Section boundaries are along X:
#   Section 0 (feeder end):    X = 0  to  X = SPLIT_1
#   Section 1 (mid / bins):    X = SPLIT_1  to  X = SPLIT_2
#   Section 2 (output end):    X = SPLIT_2  to  X = CHASSIS_LENGTH
#
# Each section prints flat (base plate on build plate, side rails vertical).
#
# Run standalone:  python chassis.py
# Outputs:         chassis_section_0.step, chassis_section_1.step,
#                  chassis_section_2.step, chassis_full.step

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
    Pos,
    Rot,
    chamfer,
    fillet,
)
import build123d as bd

from constants import (
    CARD_WIDTH,
    CARD_HEIGHT,
    CARD_CLEARANCE_WIDTH,
    CARD_CLEARANCE_HEIGHT,
    BIN_COUNT,
    BIN_WALL_THICKNESS,
    BIN_SPACING,
    BIN_INTERNAL_HEIGHT,
    BIN_FLOOR_THICKNESS,
    NEMA17_FACE,
    NEMA17_HOLE_SPACING,
    ESP32_LENGTH,
    ESP32_WIDTH,
    TMC2209_LENGTH,
    TMC2209_WIDTH,
    PRINT_TOL_DEFAULT,
    MIN_WALL,
    M3_CLEARANCE_HOLE,
    M3_HEATSET_BORE,
    M3_HEATSET_LENGTH,
    M3_HEAD_DIAMETER,
    M4_CLEARANCE_HOLE,
    M4_HEATSET_BORE,
    M4_HEATSET_LENGTH,
)
from bin_bank import bin_bank_info

# ---------------------------------------------------------------------------
# Chassis parameters
# ---------------------------------------------------------------------------

# Base plate
PLATE_THICKNESS = 5.0            # mm — Datum A top surface is at Z = PLATE_THICKNESS
PLATE_WALL = MIN_WALL            # mm — minimum structural wall

# Side rail (Datum B) — continuous left wall
RAIL_HEIGHT = 22.0               # mm — above base plate top surface
RAIL_THICKNESS = 3.0             # mm — wall thickness (printable, 7.5 perimeters)

# Feeder end stop (Datum C) — transverse wall at X = 0
END_STOP_HEIGHT = 22.0           # mm — same as side rail
END_STOP_THICKNESS = 3.0         # mm

# Module zone layout along X (all from Datum C inner face = X = 0)
# Feeder mounts against Datum C directly.
_bb = bin_bank_info()
BIN_BANK_WIDTH = _bb["bank_total_width"]   # ~570 mm
BIN_BANK_DEPTH = _bb["bank_depth"]         # ~94.9 mm

# Feeder zone: hopper sits at the X = 0 end, extends in -Y from the side rail
# The feeder external length is ~96.9 mm along Y.
# We give the feeder zone X extent to accommodate the hopper + motor mount.
FEEDER_ZONE_X_START = 0.0
FEEDER_ZONE_X_END = 100.0       # mm — hopper length along X

# Bin bank zone: starts after a small gap past the feeder
BIN_BANK_ZONE_GAP = 5.0         # mm gap between feeder zone and bin bank
BIN_BANK_ZONE_X_START = FEEDER_ZONE_X_END + BIN_BANK_ZONE_GAP
# The selector and bin bank both span the bank width along X.
# But the bin bank's long dimension (570mm) runs along the X axis.
BIN_BANK_ZONE_X_END = BIN_BANK_ZONE_X_START + BIN_BANK_WIDTH

# Recombine zone: rail mount plate sits below the bin bank, same X span.
# No additional X extent needed — shares the bin bank zone.

# Output tray zone: at the far end
OUTPUT_ZONE_GAP = 5.0            # mm gap after bin bank
OUTPUT_ZONE_X_START = BIN_BANK_ZONE_X_END + OUTPUT_ZONE_GAP
OUTPUT_ZONE_X_END = OUTPUT_ZONE_X_START + 100.0  # mm — tray length along X

# Overall chassis dimensions
CHASSIS_LENGTH = OUTPUT_ZONE_X_END + END_STOP_THICKNESS  # X extent
CHASSIS_DEPTH = BIN_BANK_DEPTH + 30.0   # Y extent — bin depth + electronics bay margin
# Ensure depth accommodates feeder and recombine mechanisms
CHASSIS_DEPTH = max(CHASSIS_DEPTH, 140.0)

# Electronics bay — recessed area on the right side (far from Datum B)
ELECTRONICS_BAY_WIDTH = 80.0     # mm along X
ELECTRONICS_BAY_DEPTH = 60.0     # mm along Y
ELECTRONICS_BAY_RECESS = 2.0     # mm — shallow recess in base plate
ELECTRONICS_BAY_X = FEEDER_ZONE_X_END + 10.0  # starts near feeder end
ELECTRONICS_BAY_Y_OFFSET = CHASSIS_DEPTH - ELECTRONICS_BAY_DEPTH - RAIL_THICKNESS

# Section split points (approximately equal thirds for printability)
SPLIT_1 = CHASSIS_LENGTH / 3.0
SPLIT_2 = 2.0 * CHASSIS_LENGTH / 3.0

# Alignment dowel pins at section joints
DOWEL_PIN_DIAMETER = 4.0         # mm — M4 dowel pin
DOWEL_PIN_BORE = DOWEL_PIN_DIAMETER + PRINT_TOL_DEFAULT  # 4.2 mm bore
DOWEL_PIN_DEPTH = 8.0            # mm — insertion depth per side
DOWEL_PIN_INSET_Y = 15.0         # mm from each edge in Y

# Joint bolt pattern — M3 bolts joining sections
JOINT_BOLT_SPACING_Y = 40.0      # mm spacing along Y
JOINT_BOLT_COUNT_Y = 3           # bolts per joint

# Rubber foot mounting
FOOT_HOLE_DIAMETER = M3_CLEARANCE_HOLE
FOOT_INSET_X = 15.0             # mm from chassis X edges
FOOT_INSET_Y = 15.0             # mm from chassis Y edges

# Cable routing channels
CABLE_CHANNEL_WIDTH = 8.0        # mm
CABLE_CHANNEL_DEPTH = 3.0        # mm — grooves in top of base plate

# Mounting slot dimensions for adjustable modules
SLOT_LENGTH = 6.0                # mm — provides +/-2mm adjustment
SLOT_WIDTH = M3_CLEARANCE_HOLE   # mm — M3 bolt clearance

# ESP32 DevKit standoff pattern (51 x 28 mm board)
ESP32_STANDOFF_SPACING_X = 44.0  # mm — hole-to-hole along length
ESP32_STANDOFF_SPACING_Y = 22.0  # mm — hole-to-hole along width

# TMC2209 driver board standoff pattern
TMC2209_STANDOFF_SPACING_X = 14.0  # mm — hole-to-hole
TMC2209_STANDOFF_SPACING_Y = 10.0  # mm — hole-to-hole
TMC2209_COUNT = 4                   # 4 drivers
TMC2209_BOARD_PITCH_X = 22.0       # mm — spacing between boards along X


# ---------------------------------------------------------------------------
# Helper: mounting slot (elongated hole for adjustability)
# ---------------------------------------------------------------------------

def _add_slot(
    builder_mode,
    cx: float,
    cy: float,
    length: float,
    width: float,
    depth: float,
    along_x: bool = True,
):
    """
    Cut a slotted hole (stadium / oblong) approximated as a rectangular
    pocket.  For a proper slot, build123d SlotOverall could be used, but
    a rectangular cut is simpler and functionally equivalent for bolt
    clearance.

    Parameters:
        cx, cy: center of slot on the XY plane
        length: slot length (long dimension)
        width: slot width (short dimension, = bolt clearance)
        depth: cut depth in Z (through the plate)
        along_x: True = slot elongated along X, False = along Y
    """
    sx = length if along_x else width
    sy = width if along_x else length
    with BuildPart(mode=Mode.SUBTRACT):
        Box(sx, sy, depth,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        bd.Location((cx, cy, -0.5))


# ---------------------------------------------------------------------------
# Build functions
# ---------------------------------------------------------------------------

def _build_base_plate(
    x_start: float,
    x_end: float,
    depth: float,
    thickness: float,
) -> None:
    """Add a base plate section. Origin: Datum C face at X=0, Datum B face at Y=0."""
    length = x_end - x_start
    cx = x_start + length / 2.0
    cy = depth / 2.0
    Box(length, depth, thickness,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    bd.Location((cx, cy, 0))


def _build_side_rail(
    x_start: float,
    x_end: float,
    thickness: float,
    height: float,
    plate_thickness: float,
) -> None:
    """Add the left side rail (Datum B). Inner face at Y = 0."""
    length = x_end - x_start
    cx = x_start + length / 2.0
    # Rail sits on top of the base plate, inner face at Y = 0
    # So the rail center Y = -thickness / 2 (extends into negative Y from inner face)
    # But we want inner face at Y = 0, so rail body is at Y = [-thickness, 0]
    cy = -thickness / 2.0
    z_base = plate_thickness
    Box(length, thickness, height,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    bd.Location((cx, cy, z_base))


def _build_end_stop(
    depth: float,
    thickness: float,
    height: float,
    plate_thickness: float,
) -> None:
    """Add the feeder end stop (Datum C). Inner face at X = 0."""
    # End stop extends from X = -thickness to X = 0
    cx = -thickness / 2.0
    cy = depth / 2.0
    z_base = plate_thickness
    Box(thickness, depth, height,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    bd.Location((cx, cy, z_base))


def build_chassis() -> bd.Part:
    """
    Build the complete chassis as a single Part.

    Coordinate convention:
        X — card travel direction. Datum C (feeder end stop inner face) at X = 0.
            Positive X toward the output tray.
        Y — card width direction. Datum B (left side rail inner face) at Y = 0.
            Positive Y toward the right (away from datum).
        Z — vertical. Datum A (base plate top surface) at Z = PLATE_THICKNESS.
            Positive Z upward.

    The base plate bottom is at Z = 0 (sits on the table). Datum A is the
    top surface at Z = PLATE_THICKNESS.
    """

    with BuildPart() as chassis:

        # ==================================================================
        # 1. BASE PLATE
        # ==================================================================
        Box(CHASSIS_LENGTH, CHASSIS_DEPTH, PLATE_THICKNESS,
            align=(Align.MIN, Align.MIN, Align.MIN))
        # Plate spans X: [0, CHASSIS_LENGTH], Y: [0, CHASSIS_DEPTH], Z: [0, PLATE_THICKNESS]
        # Datum A = top surface at Z = PLATE_THICKNESS
        # Datum B inner face = Y = 0
        # Datum C inner face = X = 0
        # Note: we shift so Datum C is at X = 0; the end stop wall extends
        # into negative X. We will add the end stop separately.

        # ==================================================================
        # 2. LEFT SIDE RAIL (Datum B)
        # ==================================================================
        # Continuous wall along the full length at Y = 0.
        # Inner face is the datum; wall extends into negative Y.
        with BuildPart():
            Box(CHASSIS_LENGTH, RAIL_THICKNESS, RAIL_HEIGHT,
                align=(Align.MIN, Align.MAX, Align.MIN))
            bd.Location((0, 0, PLATE_THICKNESS))

        # ==================================================================
        # 3. FEEDER END STOP (Datum C)
        # ==================================================================
        # Transverse wall at X = 0. Inner face is datum; wall extends into
        # negative X.
        with BuildPart():
            Box(END_STOP_THICKNESS, CHASSIS_DEPTH + RAIL_THICKNESS, END_STOP_HEIGHT,
                align=(Align.MAX, Align.MIN, Align.MIN))
            bd.Location((0, -RAIL_THICKNESS, PLATE_THICKNESS))

        # ==================================================================
        # 4. FEEDER MODULE MOUNTING (fixed holes — references Datum C)
        # ==================================================================
        # 4x M3 heat-set inserts in a rectangular pattern.
        # The feeder bolts against the end stop, so these are FIXED holes
        # (not slotted) — the feeder references Datum C directly.
        feeder_mount_positions = [
            (20.0,  15.0),
            (20.0,  BIN_BANK_DEPTH - 15.0),
            (80.0,  15.0),
            (80.0,  BIN_BANK_DEPTH - 15.0),
        ]
        for mx, my in feeder_mount_positions:
            with BuildPart(mode=Mode.SUBTRACT):
                Cylinder(
                    radius=M3_HEATSET_BORE / 2,
                    height=M3_HEATSET_LENGTH + 1.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                bd.Location((mx, my, PLATE_THICKNESS - M3_HEATSET_LENGTH))

        # ==================================================================
        # 5. SELECTOR MODULE MOUNTING (slotted holes in X for adjustment)
        # ==================================================================
        # The selector rail mounts alongside the bin bank zone.
        # Slotted holes allow +/-2mm X adjustment per datum budget.
        selector_mount_y_positions = [12.0, BIN_BANK_DEPTH - 12.0]
        selector_mount_x_positions = [
            BIN_BANK_ZONE_X_START + 30.0,
            BIN_BANK_ZONE_X_START + BIN_BANK_WIDTH / 2.0,
            BIN_BANK_ZONE_X_END - 30.0,
        ]
        for sx in selector_mount_x_positions:
            for sy in selector_mount_y_positions:
                _add_slot(
                    Mode.SUBTRACT,
                    sx, sy,
                    length=SLOT_LENGTH,
                    width=SLOT_WIDTH,
                    depth=PLATE_THICKNESS + 2.0,
                    along_x=True,  # X adjustment
                )

        # ==================================================================
        # 6. BIN BANK MOUNTING (fixed lateral, slotted X)
        # ==================================================================
        # Bin bank references Datum B directly (side rail contact) so Y is
        # fixed. X uses slotted holes for position tuning relative to the
        # selector.
        bin_mount_y_positions = [10.0, BIN_BANK_DEPTH / 2.0, BIN_BANK_DEPTH - 10.0]
        bin_mount_x_positions = [
            BIN_BANK_ZONE_X_START + 40.0,
            BIN_BANK_ZONE_X_START + BIN_BANK_WIDTH / 3.0,
            BIN_BANK_ZONE_X_START + 2.0 * BIN_BANK_WIDTH / 3.0,
            BIN_BANK_ZONE_X_END - 40.0,
        ]
        for bx in bin_mount_x_positions:
            for by in bin_mount_y_positions:
                # Heat-set insert bores (the bin bank has clearance holes;
                # the chassis gets the inserts)
                with BuildPart(mode=Mode.SUBTRACT):
                    Cylinder(
                        radius=M3_HEATSET_BORE / 2,
                        height=M3_HEATSET_LENGTH + 1.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    bd.Location((bx, by, PLATE_THICKNESS - M3_HEATSET_LENGTH))

        # ==================================================================
        # 7. RECOMBINE MODULE MOUNTING (slotted X for adjustment)
        # ==================================================================
        # The recombine rail mount plate sits below the bin bank.
        # Mounting through the base plate with slotted holes for X adjust.
        recombine_mount_y = BIN_BANK_DEPTH + 15.0  # behind the bin bank in Y
        recombine_mount_x_positions = [
            BIN_BANK_ZONE_X_START + 50.0,
            BIN_BANK_ZONE_X_START + BIN_BANK_WIDTH / 2.0,
            BIN_BANK_ZONE_X_END - 50.0,
        ]
        for rx in recombine_mount_x_positions:
            _add_slot(
                Mode.SUBTRACT,
                rx, recombine_mount_y,
                length=SLOT_LENGTH,
                width=SLOT_WIDTH,
                depth=PLATE_THICKNESS + 2.0,
                along_x=True,
            )

        # ==================================================================
        # 8. OUTPUT TRAY MOUNTING (slotted X for adjustment)
        # ==================================================================
        output_mount_positions = [
            (OUTPUT_ZONE_X_START + 15.0, 15.0),
            (OUTPUT_ZONE_X_START + 15.0, BIN_BANK_DEPTH - 15.0),
            (OUTPUT_ZONE_X_END - 15.0,   15.0),
            (OUTPUT_ZONE_X_END - 15.0,   BIN_BANK_DEPTH - 15.0),
        ]
        for ox, oy in output_mount_positions:
            _add_slot(
                Mode.SUBTRACT,
                ox, oy,
                length=SLOT_LENGTH,
                width=SLOT_WIDTH,
                depth=PLATE_THICKNESS + 2.0,
                along_x=True,
            )

        # ==================================================================
        # 9. ELECTRONICS BAY (recessed area + standoffs)
        # ==================================================================
        # Shallow recess in the base plate on the right side (high Y)
        with BuildPart(mode=Mode.SUBTRACT):
            Box(ELECTRONICS_BAY_WIDTH, ELECTRONICS_BAY_DEPTH,
                ELECTRONICS_BAY_RECESS,
                align=(Align.MIN, Align.MIN, Align.MIN))
            bd.Location((ELECTRONICS_BAY_X,
                         ELECTRONICS_BAY_Y_OFFSET,
                         PLATE_THICKNESS - ELECTRONICS_BAY_RECESS))

        # ESP32 DevKit standoff holes (4x M3 heat-set)
        esp_cx = ELECTRONICS_BAY_X + ELECTRONICS_BAY_WIDTH / 2.0
        esp_cy = ELECTRONICS_BAY_Y_OFFSET + 15.0
        for dx in (-ESP32_STANDOFF_SPACING_X / 2, ESP32_STANDOFF_SPACING_X / 2):
            for dy in (-ESP32_STANDOFF_SPACING_Y / 2, ESP32_STANDOFF_SPACING_Y / 2):
                with BuildPart(mode=Mode.SUBTRACT):
                    Cylinder(
                        radius=M3_HEATSET_BORE / 2,
                        height=M3_HEATSET_LENGTH + 1.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    bd.Location((esp_cx + dx, esp_cy + dy,
                                 PLATE_THICKNESS - M3_HEATSET_LENGTH))

        # 4x TMC2209 driver board standoffs (2 holes each = 8 total)
        tmc_base_x = ELECTRONICS_BAY_X + 10.0
        tmc_base_y = esp_cy + ESP32_STANDOFF_SPACING_Y / 2 + 15.0
        for i in range(TMC2209_COUNT):
            board_cx = tmc_base_x + TMC2209_LENGTH / 2.0 + i * TMC2209_BOARD_PITCH_X
            for dx in (-TMC2209_STANDOFF_SPACING_X / 2,
                        TMC2209_STANDOFF_SPACING_X / 2):
                for dy in (-TMC2209_STANDOFF_SPACING_Y / 2,
                            TMC2209_STANDOFF_SPACING_Y / 2):
                    with BuildPart(mode=Mode.SUBTRACT):
                        Cylinder(
                            radius=M3_HEATSET_BORE / 2,
                            height=M3_HEATSET_LENGTH + 1.0,
                            align=(Align.CENTER, Align.CENTER, Align.MIN),
                        )
                        bd.Location((board_cx + dx, tmc_base_y + dy,
                                     PLATE_THICKNESS - M3_HEATSET_LENGTH))

        # ==================================================================
        # 10. CABLE ROUTING CHANNELS
        # ==================================================================
        # Longitudinal channel along the right side of the base plate
        # (high Y, near electronics bay) for motor and sensor cables.
        cable_y = CHASSIS_DEPTH - 20.0
        with BuildPart(mode=Mode.SUBTRACT):
            Box(CHASSIS_LENGTH - 40.0, CABLE_CHANNEL_WIDTH, CABLE_CHANNEL_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((CHASSIS_LENGTH / 2.0, cable_y,
                         PLATE_THICKNESS - CABLE_CHANNEL_DEPTH))

        # Transverse channels connecting each module zone to the main channel
        transverse_x_positions = [
            FEEDER_ZONE_X_END / 2.0,
            BIN_BANK_ZONE_X_START + BIN_BANK_WIDTH / 4.0,
            BIN_BANK_ZONE_X_START + 3.0 * BIN_BANK_WIDTH / 4.0,
            OUTPUT_ZONE_X_START + 50.0,
        ]
        for tx in transverse_x_positions:
            with BuildPart(mode=Mode.SUBTRACT):
                Box(CABLE_CHANNEL_WIDTH, CHASSIS_DEPTH / 2.0, CABLE_CHANNEL_DEPTH,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
                bd.Location((tx, CHASSIS_DEPTH * 0.75,
                             PLATE_THICKNESS - CABLE_CHANNEL_DEPTH))

        # ==================================================================
        # 11. RUBBER FOOT MOUNTING POINTS (4x corners)
        # ==================================================================
        foot_positions = [
            (FOOT_INSET_X, FOOT_INSET_Y),
            (FOOT_INSET_X, CHASSIS_DEPTH - FOOT_INSET_Y),
            (CHASSIS_LENGTH - FOOT_INSET_X, FOOT_INSET_Y),
            (CHASSIS_LENGTH - FOOT_INSET_X, CHASSIS_DEPTH - FOOT_INSET_Y),
        ]
        for fx, fy in foot_positions:
            # Through-hole for M3 screw + rubber foot
            with BuildPart(mode=Mode.SUBTRACT):
                Cylinder(
                    radius=M3_CLEARANCE_HOLE / 2,
                    height=PLATE_THICKNESS + 2.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                bd.Location((fx, fy, -1.0))
            # Counterbore on top surface for screw head clearance
            with BuildPart(mode=Mode.SUBTRACT):
                Cylinder(
                    radius=M3_HEAD_DIAMETER / 2 + 0.3,
                    height=2.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                bd.Location((fx, fy, PLATE_THICKNESS - 2.0))

        # ==================================================================
        # 12. SECTION SPLIT JOINT FEATURES
        # ==================================================================
        # At each split line, add:
        #   - 2x dowel pin holes for alignment
        #   - 3x M3 bolt holes for clamping

        for split_x in (SPLIT_1, SPLIT_2):
            # Dowel pin holes (through the full plate thickness + into rail)
            for dy in (DOWEL_PIN_INSET_Y, CHASSIS_DEPTH - DOWEL_PIN_INSET_Y):
                with BuildPart(mode=Mode.SUBTRACT):
                    Cylinder(
                        radius=DOWEL_PIN_BORE / 2,
                        height=PLATE_THICKNESS + RAIL_HEIGHT + 2.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    bd.Location((split_x, dy, -1.0))

            # Joint bolt holes — spaced along Y
            bolt_y_start = 30.0
            bolt_y_step = (CHASSIS_DEPTH - 2 * bolt_y_start) / (JOINT_BOLT_COUNT_Y - 1)
            for i in range(JOINT_BOLT_COUNT_Y):
                by = bolt_y_start + i * bolt_y_step
                with BuildPart(mode=Mode.SUBTRACT):
                    Cylinder(
                        radius=M3_CLEARANCE_HOLE / 2,
                        height=PLATE_THICKNESS + 2.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    bd.Location((split_x, by, -1.0))

        # ==================================================================
        # 13. RIGHT SIDE STIFFENING RIB (optional low wall)
        # ==================================================================
        # A short rib along the right edge for torsional stiffness.
        # Not a datum — just structural. 10mm tall.
        rib_height = 10.0
        with BuildPart():
            Box(CHASSIS_LENGTH, RAIL_THICKNESS, rib_height,
                align=(Align.MIN, Align.MIN, Align.MIN))
            bd.Location((0, CHASSIS_DEPTH, PLATE_THICKNESS))

    return chassis.part


def chassis_info() -> dict:
    """Return a summary dict of chassis dimensions for other modules."""
    return {
        "chassis_length": CHASSIS_LENGTH,
        "chassis_depth": CHASSIS_DEPTH,
        "plate_thickness": PLATE_THICKNESS,
        "rail_height": RAIL_HEIGHT,
        "rail_thickness": RAIL_THICKNESS,
        "end_stop_thickness": END_STOP_THICKNESS,
        "datum_a_z": PLATE_THICKNESS,
        "datum_b_y": 0.0,
        "datum_c_x": 0.0,
        "feeder_zone": (FEEDER_ZONE_X_START, FEEDER_ZONE_X_END),
        "bin_bank_zone": (BIN_BANK_ZONE_X_START, BIN_BANK_ZONE_X_END),
        "output_zone": (OUTPUT_ZONE_X_START, OUTPUT_ZONE_X_END),
        "split_1": SPLIT_1,
        "split_2": SPLIT_2,
        "electronics_bay_origin": (ELECTRONICS_BAY_X, ELECTRONICS_BAY_Y_OFFSET),
        "electronics_bay_size": (ELECTRONICS_BAY_WIDTH, ELECTRONICS_BAY_DEPTH),
    }


def build_chassis_section(section: int) -> bd.Part:
    """
    Build a single printable section of the chassis.

    section: 0 = feeder end, 1 = middle, 2 = output end.

    Each section is the full chassis clipped to its X range, so it can be
    printed independently and bolted together with dowel alignment.
    """
    full = build_chassis()

    # Define X bounds for each section
    bounds = {
        0: (0.0 - END_STOP_THICKNESS - 1.0, SPLIT_1),
        1: (SPLIT_1, SPLIT_2),
        2: (SPLIT_2, CHASSIS_LENGTH + 1.0),
    }
    if section not in bounds:
        raise ValueError(f"section must be 0, 1, or 2, got {section}")

    x_min, x_max = bounds[section]

    # Use a boolean intersection with a bounding box to clip
    clip_length = x_max - x_min + 2.0
    clip_cx = (x_min + x_max) / 2.0
    # The clip box must be tall and deep enough to contain the full chassis
    clip_height = PLATE_THICKNESS + RAIL_HEIGHT + 10.0
    clip_depth = CHASSIS_DEPTH + RAIL_THICKNESS + 10.0

    with BuildPart() as section_part:
        # Start with a clip box
        Box(clip_length, clip_depth, clip_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        bd.Location((clip_cx, CHASSIS_DEPTH / 2.0 - RAIL_THICKNESS / 2.0, -2.0))

    # Boolean intersect: section = full AND clip_box
    result = full.intersect(section_part.part)
    return result


# -- Main --------------------------------------------------------------------
if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    out_dir.mkdir(exist_ok=True)

    # Export full chassis
    full = build_chassis()
    full_path = out_dir / "chassis_full.step"
    export_step(full, str(full_path))
    print(f"Exported full chassis to {full_path}")

    # Export individual sections
    for i in range(3):
        try:
            section = build_chassis_section(i)
            sec_path = out_dir / f"chassis_section_{i}.step"
            export_step(section, str(sec_path))
            print(f"Exported chassis section {i} to {sec_path}")
        except Exception as e:
            print(f"Warning: could not export section {i}: {e}")

    # Print summary
    info = chassis_info()
    print(f"\nChassis summary:")
    for k, v in info.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.1f} mm")
        elif isinstance(v, tuple) and all(isinstance(x, float) for x in v):
            print(f"  {k}: ({', '.join(f'{x:.1f}' for x in v)}) mm")
        else:
            print(f"  {k}: {v}")
