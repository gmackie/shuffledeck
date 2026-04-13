# Recombine module — pusher/elevator mechanism for collecting partial stacks
# from the 8-bin bank and assembling them into a single deck.
# Requires: pip install build123d
#
# After pass 1, cards are distributed across 8 bins. The recombine module
# traverses the bin bank along the X axis, lifts each partial stack with a
# pusher plate rising through the bin floor, captures it onto a collection
# tray, and accumulates all stacks into a single deck. The combined deck
# then routes back to the feeder (pass 2) or to the output tray (final).
#
# Mechanism:
#   - Linear rail (MGN12H) for X travel along bin bank
#   - Vertical elevator (small stepper/servo) lifts pusher plate through bin floor
#   - Collection tray with side guides holds the growing stack
#   - NEMA17 drives the X axis via belt or leadscrew
#
# Run standalone:  python recombine.py
# Outputs:         recombine.step

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
    CARD_THICKNESS,
    DECK_COUNT,
    DECK_STACK_HEIGHT_MAX,
    BIN_COUNT,
    BIN_INTERNAL_WIDTH,
    BIN_INTERNAL_DEPTH,
    BIN_INTERNAL_HEIGHT,
    BIN_WALL_THICKNESS,
    BIN_FLOOR_THICKNESS,
    BIN_SPACING,
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
    CARD_CLEARANCE_WIDTH,
    CARD_CLEARANCE_HEIGHT,
)

# ── Recombine parameters ──────────────────────────────────────────────
# Pusher plate
PUSHER_CLEARANCE = 0.5           # mm per side — plate must fit inside bin cavity
PUSHER_PLATE_THICKNESS = 2.0     # mm
PUSHER_PLATE_WIDTH = CARD_WIDTH + 2 * CARD_CLEARANCE_WIDTH - 2 * PUSHER_CLEARANCE
PUSHER_PLATE_DEPTH = CARD_HEIGHT + 2 * CARD_CLEARANCE_HEIGHT - 2 * PUSHER_CLEARANCE

# Elevator
ELEVATOR_TRAVEL = BIN_INTERNAL_HEIGHT + 5.0   # mm — enough to clear bin top
ELEVATOR_FRAME_WALL = 3.0        # mm
ELEVATOR_FRAME_WIDTH = PUSHER_PLATE_WIDTH + 2 * ELEVATOR_FRAME_WALL
ELEVATOR_FRAME_DEPTH = 30.0      # mm — compact frame behind pusher
ELEVATOR_FRAME_HEIGHT = ELEVATOR_TRAVEL + 20.0  # mm — room for travel + mount

# Collection tray
TRAY_WALL = 2.5                  # mm
TRAY_GUIDE_HEIGHT = DECK_STACK_HEIGHT_MAX + 5.0  # mm — holds full deck + margin
TRAY_INT_WIDTH = CARD_WIDTH + 2 * CARD_CLEARANCE_WIDTH
TRAY_INT_DEPTH = CARD_HEIGHT + 2 * CARD_CLEARANCE_HEIGHT
TRAY_FLOOR_THICKNESS = 2.0      # mm
TRAY_FUNNEL_CHAMFER = 2.0       # mm — entry chamfer for card alignment

# Linear rail (MGN12H)
MGN12_RAIL_WIDTH = 12.0          # mm
MGN12_RAIL_HEIGHT = 8.0          # mm
MGN12_CARRIAGE_WIDTH = 27.0      # mm
MGN12_CARRIAGE_LENGTH = 34.7     # mm
MGN12_CARRIAGE_HEIGHT = 13.0     # mm
MGN12_MOUNT_HOLE_SPACING_X = 20.0  # mm
MGN12_MOUNT_HOLE_SPACING_Y = 15.0  # mm

# X-axis travel — must span all bin positions
BIN_CELL_WIDTH = BIN_INTERNAL_WIDTH + 2 * BIN_WALL_THICKNESS
BANK_TOTAL_WIDTH = BIN_COUNT * BIN_CELL_WIDTH + (BIN_COUNT - 1) * BIN_SPACING

# Motor mount plate
MOTOR_PLATE_THICKNESS = 5.0      # mm
MOTOR_PLATE_WIDTH = NEMA17_FACE + 10.0
MOTOR_PLATE_HEIGHT = NEMA17_FACE + 10.0

# Z-axis small stepper mount (NEMA14 or micro servo — using 28BYJ-48 envelope)
Z_MOTOR_FACE = 28.0             # mm (28BYJ-48 diameter approximation)
Z_MOTOR_MOUNT_WIDTH = 35.0      # mm
Z_MOTOR_MOUNT_HEIGHT = 20.0     # mm
Z_MOTOR_MOUNT_THICKNESS = 3.0   # mm
Z_MOTOR_HOLE_SPACING = 35.0     # mm (28BYJ-48 mounting tab spacing)
Z_MOTOR_HOLE_DIA = 4.2          # mm (M4 clearance for 28BYJ mounting)

# Rail mount plate
RAIL_MOUNT_PLATE_THICKNESS = 4.0  # mm
RAIL_MOUNT_PLATE_WIDTH = BANK_TOTAL_WIDTH + 40.0  # mm — extends past bank ends
RAIL_MOUNT_PLATE_HEIGHT = MGN12_CARRIAGE_WIDTH + 16.0  # mm

# Chassis mounting
CHASSIS_MOUNT_INSET = 10.0       # mm from plate edges


def build_recombine() -> bd.Part:
    """Build the recombine module assembly as a single part."""

    with BuildPart() as recombine:

        # ── 1. Pusher plate ────────────────────────────────────────────
        # Flat plate that rises through the bin floor slot to lift cards.
        # Positioned at origin; the full assembly is composed in-place.
        with BuildPart() as _pusher:
            Box(PUSHER_PLATE_WIDTH, PUSHER_PLATE_DEPTH, PUSHER_PLATE_THICKNESS,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Slight chamfer on top edges to avoid snagging cards
            # (represented as a thinner rim around the perimeter)

        # ── 2. Collection / accumulator tray ───────────────────────────
        # Positioned above the pusher mechanism, offset in Z.
        tray_z_offset = ELEVATOR_FRAME_HEIGHT + 5.0

        # Outer shell
        tray_ext_w = TRAY_INT_WIDTH + 2 * TRAY_WALL
        tray_ext_d = TRAY_INT_DEPTH + 2 * TRAY_WALL
        tray_ext_h = TRAY_GUIDE_HEIGHT + TRAY_FLOOR_THICKNESS

        with BuildPart():
            Box(tray_ext_w, tray_ext_d, tray_ext_h,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, 0, tray_z_offset))

        # Hollow interior
        with BuildPart(mode=Mode.SUBTRACT):
            Box(TRAY_INT_WIDTH, TRAY_INT_DEPTH, TRAY_GUIDE_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, 0, tray_z_offset + TRAY_FLOOR_THICKNESS))

        # Funnel chamfer — wider opening at the top for card alignment
        funnel_w = TRAY_INT_WIDTH + 2 * TRAY_FUNNEL_CHAMFER
        funnel_d = TRAY_INT_DEPTH + 2 * TRAY_FUNNEL_CHAMFER
        funnel_h = TRAY_FUNNEL_CHAMFER
        with BuildPart(mode=Mode.SUBTRACT):
            Box(funnel_w, funnel_d, funnel_h,
                align=(Align.CENTER, Align.CENTER, Align.MAX))
            bd.Location((0, 0, tray_z_offset + tray_ext_h))

        # Floor slot — through-hole for pusher plate to rise into tray
        with BuildPart(mode=Mode.SUBTRACT):
            Box(PUSHER_PLATE_WIDTH + 2 * PRINT_TOL_DEFAULT,
                PUSHER_PLATE_DEPTH + 2 * PRINT_TOL_DEFAULT,
                TRAY_FLOOR_THICKNESS + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, 0, tray_z_offset - 1.0))

        # ── 3. Elevator frame ─────────────────────────────────────────
        # Vertical frame that guides the pusher plate up and down.
        # Positioned below the tray.
        elev_z = 0.0

        # Main frame body (C-channel shape around the pusher travel)
        with BuildPart():
            Box(ELEVATOR_FRAME_WIDTH, ELEVATOR_FRAME_DEPTH, ELEVATOR_FRAME_HEIGHT,
                align=(Align.CENTER, Align.MAX, Align.MIN))
            bd.Location((0, -TRAY_INT_DEPTH / 2, elev_z))

        # Hollow out the travel channel for the pusher plate
        channel_w = PUSHER_PLATE_WIDTH + 2 * PRINT_TOL_DEFAULT
        channel_d = ELEVATOR_FRAME_DEPTH - ELEVATOR_FRAME_WALL
        channel_h = ELEVATOR_TRAVEL + 2.0
        with BuildPart(mode=Mode.SUBTRACT):
            Box(channel_w, channel_d, channel_h,
                align=(Align.CENTER, Align.MAX, Align.MIN))
            bd.Location((0, -TRAY_INT_DEPTH / 2 + ELEVATOR_FRAME_WALL,
                         elev_z + ELEVATOR_FRAME_WALL))

        # Vertical guide slots (two slots for linear rod or rail guidance)
        guide_slot_width = 8.0
        guide_slot_depth = ELEVATOR_FRAME_DEPTH + 2.0
        for x_sign in (-1, 1):
            gx = x_sign * (PUSHER_PLATE_WIDTH / 2 + ELEVATOR_FRAME_WALL / 2)
            with BuildPart(mode=Mode.SUBTRACT):
                Box(guide_slot_width, guide_slot_depth, ELEVATOR_TRAVEL,
                    align=(Align.CENTER, Align.MAX, Align.MIN))
                bd.Location((gx, -TRAY_INT_DEPTH / 2 + 1.0,
                             elev_z + ELEVATOR_FRAME_WALL))

        # ── 4. Z-axis motor mount (28BYJ-48 or micro servo) ──────────
        z_motor_z = elev_z + ELEVATOR_FRAME_HEIGHT / 2
        z_motor_y = -TRAY_INT_DEPTH / 2 - ELEVATOR_FRAME_DEPTH

        # Mount bracket
        with BuildPart():
            Box(Z_MOTOR_MOUNT_WIDTH, Z_MOTOR_MOUNT_THICKNESS, Z_MOTOR_MOUNT_HEIGHT,
                align=(Align.CENTER, Align.MAX, Align.CENTER))
            bd.Location((0, z_motor_y, z_motor_z))

        # Motor shaft through-hole
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(
                radius=Z_MOTOR_FACE / 2 + PRINT_TOL_DEFAULT,
                height=Z_MOTOR_MOUNT_THICKNESS + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((0, z_motor_y + 1.0, z_motor_z))
            bd.Rotation((90, 0, 0))

        # Motor mounting holes (2x for 28BYJ-48 tab pattern)
        for dx in (-Z_MOTOR_HOLE_SPACING / 2, Z_MOTOR_HOLE_SPACING / 2):
            with BuildPart(mode=Mode.SUBTRACT):
                Cylinder(
                    radius=Z_MOTOR_HOLE_DIA / 2,
                    height=Z_MOTOR_MOUNT_THICKNESS + 2.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                bd.Location((dx, z_motor_y + 1.0, z_motor_z))
                bd.Rotation((90, 0, 0))

        # ── 5. Linear rail mount plate (MGN12H, X axis) ──────────────
        # Horizontal plate that the rail screws onto, spans the bin bank.
        rail_plate_z = -RAIL_MOUNT_PLATE_THICKNESS

        with BuildPart():
            Box(RAIL_MOUNT_PLATE_WIDTH, RAIL_MOUNT_PLATE_HEIGHT,
                RAIL_MOUNT_PLATE_THICKNESS,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, 0, rail_plate_z))

        # Rail mounting holes — M3, spaced every 20 mm along rail length
        import math
        rail_hole_count = int(RAIL_MOUNT_PLATE_WIDTH / 20.0)
        rail_start_x = -(rail_hole_count - 1) * 20.0 / 2
        for i in range(rail_hole_count):
            hx = rail_start_x + i * 20.0
            with BuildPart(mode=Mode.SUBTRACT):
                Cylinder(
                    radius=M3_CLEARANCE_HOLE / 2,
                    height=RAIL_MOUNT_PLATE_THICKNESS + 2.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                bd.Location((hx, 0, rail_plate_z - 1.0))

        # Chassis mounting holes — M3 heat-set inserts at plate corners
        for cx in (-RAIL_MOUNT_PLATE_WIDTH / 2 + CHASSIS_MOUNT_INSET,
                    RAIL_MOUNT_PLATE_WIDTH / 2 - CHASSIS_MOUNT_INSET):
            for cy in (-RAIL_MOUNT_PLATE_HEIGHT / 2 + CHASSIS_MOUNT_INSET,
                        RAIL_MOUNT_PLATE_HEIGHT / 2 - CHASSIS_MOUNT_INSET):
                with BuildPart(mode=Mode.SUBTRACT):
                    Cylinder(
                        radius=M3_HEATSET_BORE / 2,
                        height=M3_HEATSET_LENGTH + 1.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    bd.Location((cx, cy, rail_plate_z - 0.5))

        # ── 6. NEMA17 mount for X-axis drive ──────────────────────────
        # Motor bracket at one end of the rail plate.
        motor_x = RAIL_MOUNT_PLATE_WIDTH / 2 + MOTOR_PLATE_THICKNESS / 2
        motor_z = rail_plate_z + RAIL_MOUNT_PLATE_THICKNESS / 2

        with BuildPart():
            Box(MOTOR_PLATE_THICKNESS, MOTOR_PLATE_HEIGHT, MOTOR_PLATE_WIDTH,
                align=(Align.CENTER, Align.CENTER, Align.CENTER))
            bd.Location((motor_x, 0, motor_z + MOTOR_PLATE_WIDTH / 2))

        # NEMA17 mounting holes (4x M3 on 31 mm diagonal pattern)
        half_spacing = NEMA17_HOLE_SPACING / 2
        for dz in (-half_spacing, half_spacing):
            for dy in (-half_spacing, half_spacing):
                with BuildPart(mode=Mode.SUBTRACT):
                    Cylinder(
                        radius=M3_CLEARANCE_HOLE / 2,
                        height=MOTOR_PLATE_THICKNESS + 2.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    bd.Location((motor_x - MOTOR_PLATE_THICKNESS / 2 - 1.0,
                                 dy, motor_z + MOTOR_PLATE_WIDTH / 2 + dz))
                    bd.Rotation((0, 90, 0))

        # Central pilot hole for NEMA17
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(
                radius=(NEMA17_PILOT_DIAMETER / 2) + PRINT_TOL_TIGHT,
                height=MOTOR_PLATE_THICKNESS + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((motor_x - MOTOR_PLATE_THICKNESS / 2 - 1.0,
                         0, motor_z + MOTOR_PLATE_WIDTH / 2))
            bd.Rotation((0, 90, 0))

        # Shaft through-hole
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(
                radius=(NEMA17_SHAFT_DIAMETER / 2) + PRINT_TOL_TIGHT,
                height=MOTOR_PLATE_THICKNESS + 4.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((motor_x - MOTOR_PLATE_THICKNESS / 2 - 2.0,
                         0, motor_z + MOTOR_PLATE_WIDTH / 2))
            bd.Rotation((0, 90, 0))

    return recombine.part


# ── Main ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    part = build_recombine()
    out_path = Path(__file__).resolve().parent / "recombine.step"
    export_step(part, str(out_path))
    print(f"Exported recombine module to {out_path}")
