# Candidate A — Friction roller + retard pad singulation mechanism.
# Baseline candidate for the feeder bakeoff.
#
# Builds a COMPLETE feeder (hopper + singulation geometry) as one Part.
# Build123d parts are immutable after construction, so we recreate the
# full hopper here with singulation features integrated.
#
# Run standalone:  python candidate_a_friction_retard.py
# Outputs:         feeder_candidate_a.step

from __future__ import annotations

import sys
from pathlib import Path

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
)
import build123d as bd

from constants import (
    CARD_WIDTH,
    CARD_HEIGHT,
    CARD_THICKNESS,
    DECK_STACK_HEIGHT_MAX,
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
    M3_TAP_HOLE,
    BIN_WALL_THICKNESS,
)

# ── Feeder parameters (duplicated from feeder.py skeleton) ─────────────
HOPPER_ANGLE_DEG = 15.0
HOPPER_WALL = 3.0
HOPPER_SIDE_CLEARANCE = 2.0
HOPPER_END_CLEARANCE = 2.0
HOPPER_DEPTH = DECK_STACK_HEIGHT_MAX + 10.0
EXIT_THROAT_GAP = CARD_THICKNESS + 0.5
MOUNTING_PLATE_THICKNESS = 5.0

HOPPER_INT_W = CARD_WIDTH + 2 * HOPPER_SIDE_CLEARANCE
HOPPER_INT_L = CARD_HEIGHT + HOPPER_END_CLEARANCE
HOPPER_EXT_W = HOPPER_INT_W + 2 * HOPPER_WALL
HOPPER_EXT_L = HOPPER_INT_L + 2 * HOPPER_WALL

# ── Singulation parameters (Candidate A) ───────────────────────────────
# Drive roller — O-ring on NEMA17 shaft
ROLLER_OD = 20.0                     # mm — O-ring outer diameter
ROLLER_CROSS_SECTION = 3.0           # mm — O-ring cross-section diameter
ROLLER_ID = ROLLER_OD - 2 * ROLLER_CROSS_SECTION  # 14 mm
ROLLER_PROTRUSION = 1.0              # mm above hopper floor surface
ROLLER_SHAFT_DIA = NEMA17_SHAFT_DIAMETER  # 5 mm D-shaft

# 625ZZ bearing: 5 mm bore, 16 mm OD, 5 mm width
BEARING_BORE = 5.0
BEARING_OD = 16.0
BEARING_WIDTH = 5.0

# Roller pocket in hopper floor — centered on motor shaft (origin)
ROLLER_POCKET_LENGTH = ROLLER_OD + 2 * PRINT_TOL_DEFAULT  # along feed direction
ROLLER_POCKET_WIDTH = ROLLER_CROSS_SECTION + 2 * PRINT_TOL_DEFAULT
ROLLER_POCKET_DEPTH = (ROLLER_OD / 2) - ROLLER_PROTRUSION  # how deep below floor

# Bearing pocket in side walls
BEARING_POCKET_DEPTH = BEARING_WIDTH + PRINT_TOL_TIGHT  # press-fit depth into wall
BEARING_POCKET_RADIUS = (BEARING_OD / 2) + PRINT_TOL_TIGHT

# Retard pad
RETARD_PAD_WIDTH = 40.0              # mm — across card width
RETARD_PAD_LENGTH = 15.0             # mm — along feed direction
RETARD_PAD_THICKNESS = 3.0           # mm
RETARD_HOLDER_WALL = 2.0             # mm
RETARD_HOLDER_WIDTH = RETARD_PAD_WIDTH + 2 * RETARD_HOLDER_WALL
RETARD_HOLDER_LENGTH = RETARD_PAD_LENGTH + 2 * RETARD_HOLDER_WALL

# Spring pocket behind retard pad
SPRING_POCKET_DIA = 8.0              # mm — compression spring OD
SPRING_POCKET_DEPTH = 12.0           # mm
SET_SCREW_ACCESS_DIA = M3_TAP_HOLE   # M3 set screw for preload

# Shoulder bolt pivot for retard pad holder
SHOULDER_BOLT_DIA = 4.0              # mm shoulder
SHOULDER_BOLT_BORE = SHOULDER_BOLT_DIA + PRINT_TOL_DEFAULT

# Nip zone
NIP_GAP = CARD_THICKNESS + 0.05      # 0.35 mm nominal

# Exit guide channel
EXIT_GUIDE_LENGTH = 20.0             # mm after nip zone
EXIT_GUIDE_HEIGHT = CARD_THICKNESS + 1.0  # generous clearance for card
EXIT_GUIDE_WALL = 1.5                # mm

# Eccentric bushing (for roller height adjustment)
ECCENTRIC_BUSHING_OD = BEARING_OD + 4.0  # wraps around bearing OD
ECCENTRIC_BUSHING_BORE = BEARING_OD + PRINT_TOL_DEFAULT

# Dovetail retard pad removal
DOVETAIL_WIDTH = RETARD_HOLDER_WIDTH + 4.0
DOVETAIL_DEPTH = RETARD_PAD_THICKNESS + RETARD_HOLDER_WALL + 2.0


def build_feeder_candidate_a() -> bd.Part:
    """Build feeder with Candidate A friction-roller + retard-pad singulation."""

    with BuildPart() as feeder:

        # ══════════════════════════════════════════════════════════════
        # BASE HOPPER (reproduced from feeder.py skeleton)
        # ══════════════════════════════════════════════════════════════

        # Outer shell
        Box(HOPPER_EXT_W, HOPPER_EXT_L, HOPPER_DEPTH + HOPPER_WALL,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Hollow interior
        with BuildPart(mode=Mode.SUBTRACT):
            Box(HOPPER_INT_W, HOPPER_INT_L, HOPPER_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, 0, HOPPER_WALL))

        # Exit throat slot
        throat_width = CARD_WIDTH + 2 * PRINT_TOL_DEFAULT
        throat_y = -(HOPPER_EXT_L / 2)
        with BuildPart(mode=Mode.SUBTRACT):
            Box(throat_width, HOPPER_WALL + 2.0, EXIT_THROAT_GAP,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, throat_y, HOPPER_WALL))

        # NEMA17 mounting plate
        motor_plate_z = -MOUNTING_PLATE_THICKNESS
        with BuildPart():
            Box(NEMA17_FACE + 10.0, NEMA17_FACE + 10.0, MOUNTING_PLATE_THICKNESS,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, 0, motor_plate_z))

        # NEMA17 mounting holes
        half_spacing = NEMA17_HOLE_SPACING / 2
        for dx in (-half_spacing, half_spacing):
            for dy in (-half_spacing, half_spacing):
                with BuildPart(mode=Mode.SUBTRACT):
                    Cylinder(
                        radius=M3_CLEARANCE_HOLE / 2,
                        height=MOUNTING_PLATE_THICKNESS + 2.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    bd.Location((dx, dy, motor_plate_z - 1.0))

        # Pilot hole
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(
                radius=(NEMA17_PILOT_DIAMETER / 2) + PRINT_TOL_TIGHT,
                height=MOUNTING_PLATE_THICKNESS + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((0, 0, motor_plate_z - 1.0))

        # Shaft through-hole
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(
                radius=(NEMA17_SHAFT_DIAMETER / 2) + PRINT_TOL_TIGHT,
                height=HOPPER_WALL + MOUNTING_PLATE_THICKNESS + 4.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((0, 0, motor_plate_z - 1.0))

        # ══════════════════════════════════════════════════════════════
        # CANDIDATE A: FRICTION ROLLER + RETARD PAD SINGULATION
        # ══════════════════════════════════════════════════════════════

        # ── 1. Drive roller pocket ─────────────────────────────────────
        # Slot in the hopper floor centered on the motor shaft (origin).
        # The roller sits below the floor and protrudes ROLLER_PROTRUSION
        # above the floor surface to contact the bottom card.
        #
        # Pocket shape: elongated slot along the feed direction (Y axis)
        # so the O-ring can spin freely.
        roller_pocket_z = 0.0  # starts at bottom of hopper floor
        with BuildPart(mode=Mode.SUBTRACT):
            # Main roller pocket — cylindrical bore for the O-ring
            Cylinder(
                radius=(ROLLER_OD / 2) + PRINT_TOL_DEFAULT,
                height=HOPPER_WALL + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((0, 0, -0.5))  # cut through entire floor

        # ── 2. Bearing pockets in side walls ───────────────────────────
        # Two 625ZZ bearings support the roller shaft. They press into
        # bores in the left and right hopper walls, at floor level,
        # centered on the motor shaft axis.
        bearing_center_z = HOPPER_WALL / 2  # center of floor thickness
        for x_sign in (-1, +1):
            wall_center_x = x_sign * (HOPPER_INT_W / 2 + HOPPER_WALL / 2)
            with BuildPart(mode=Mode.SUBTRACT):
                # Bearing bore — cut into side wall from inside
                Cylinder(
                    radius=BEARING_POCKET_RADIUS,
                    height=BEARING_POCKET_DEPTH,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                # Orient horizontally (along X) into the wall
                bd.Location((
                    x_sign * (HOPPER_INT_W / 2 - BEARING_POCKET_DEPTH / 2),
                    0,
                    bearing_center_z,
                ))
                # Rotate to bore into the wall along X axis
            # Actually: use a horizontal cylinder subtraction.
            # Build123d Cylinder is along Z by default; we need it along X.
            with BuildPart(mode=Mode.SUBTRACT):
                with bd.BuildPart() as _brg:
                    Cylinder(
                        radius=BEARING_POCKET_RADIUS,
                        height=HOPPER_WALL + 2.0,
                        align=(Align.CENTER, Align.CENTER, Align.CENTER),
                        rotation=(0, 90, 0),  # rotate to lie along X
                    )
                bd.Location((wall_center_x, 0, bearing_center_z))

        # ── 3. Eccentric bushing bore (one side) ──────────────────────
        # The right-side bearing gets an oversized bore to accept an
        # eccentric bushing for roller height fine-tuning.
        eccentric_wall_x = +(HOPPER_INT_W / 2 + HOPPER_WALL / 2)
        with BuildPart(mode=Mode.SUBTRACT):
            with bd.BuildPart() as _ecc:
                Cylinder(
                    radius=(ECCENTRIC_BUSHING_OD / 2) + PRINT_TOL_TIGHT,
                    height=HOPPER_WALL + 2.0,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    rotation=(0, 90, 0),
                )
            bd.Location((eccentric_wall_x, 0, bearing_center_z))

        # ── 4. Retard pad cavity ───────────────────────────────────────
        # The retard pad sits above the roller, pressing down on the
        # card stack from inside the hopper. It is positioned directly
        # above the nip zone — just forward (negative Y) of center,
        # at the throat side.
        #
        # The pad holder slides in on a dovetail channel from the side
        # wall, pivoting on a shoulder bolt for self-alignment.

        # Retard pad cavity position: above roller, at floor level + just
        # above one card thickness (the nip gap).
        retard_cavity_z = HOPPER_WALL  # sits on top of the floor
        retard_cavity_y = 0.0          # centered on roller/shaft

        # Main cavity for the retard pad holder assembly
        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                RETARD_HOLDER_WIDTH,
                RETARD_HOLDER_LENGTH + SPRING_POCKET_DEPTH + 5.0,
                RETARD_PAD_THICKNESS + RETARD_HOLDER_WALL * 2 + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((
                0,
                retard_cavity_y,
                retard_cavity_z,
            ))

        # ── 5. Dovetail slide channel for retard pad removal ──────────
        # Runs along X from the right wall inward — the retard pad
        # holder slides out to the right for replacement.
        dovetail_entry_x = HOPPER_EXT_W / 2  # right outer wall
        with BuildPart(mode=Mode.SUBTRACT):
            # Simplified as a rectangular channel (true dovetail would
            # need a trapezoidal profile; this is printable as a slot
            # with slight draft).
            Box(
                HOPPER_WALL + 4.0,  # through the wall + clearance
                RETARD_HOLDER_LENGTH + 1.0,
                RETARD_PAD_THICKNESS + RETARD_HOLDER_WALL + 1.0,
                align=(Align.MAX, Align.CENTER, Align.MIN),
            )
            bd.Location((
                dovetail_entry_x + 1.0,
                retard_cavity_y,
                retard_cavity_z,
            ))

        # ── 6. Shoulder bolt pivot holes (retard pad holder) ──────────
        # Two holes through the side walls for the shoulder bolt that
        # the retard pad holder pivots on.
        pivot_z = retard_cavity_z + (RETARD_PAD_THICKNESS + RETARD_HOLDER_WALL * 2) / 2
        for x_sign in (-1, +1):
            wall_x = x_sign * (HOPPER_INT_W / 2 + HOPPER_WALL / 2)
            with BuildPart(mode=Mode.SUBTRACT):
                with bd.BuildPart() as _pivot:
                    Cylinder(
                        radius=SHOULDER_BOLT_BORE / 2,
                        height=HOPPER_WALL + 2.0,
                        align=(Align.CENTER, Align.CENTER, Align.CENTER),
                        rotation=(0, 90, 0),
                    )
                bd.Location((wall_x, retard_cavity_y, pivot_z))

        # ── 7. Spring pocket (behind retard pad) ──────────────────────
        # Cylindrical pocket in the hopper floor/wall behind the retard
        # pad (positive Y side) for the compression spring.
        spring_center_y = retard_cavity_y + RETARD_HOLDER_LENGTH / 2 + SPRING_POCKET_DIA / 2 + 2.0
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(
                radius=SPRING_POCKET_DIA / 2 + PRINT_TOL_DEFAULT,
                height=SPRING_POCKET_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((0, spring_center_y, retard_cavity_z))

        # ── 8. Set screw access hole (spring preload adjustment) ──────
        # M3 tapped hole from the outside rear wall into the spring
        # pocket, allowing a set screw to adjust spring preload.
        set_screw_y = HOPPER_EXT_L / 2  # rear outer wall
        with BuildPart(mode=Mode.SUBTRACT):
            with bd.BuildPart() as _ss:
                Cylinder(
                    radius=SET_SCREW_ACCESS_DIA / 2,
                    height=HOPPER_WALL + 4.0,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    rotation=(90, 0, 0),  # along Y axis into rear wall
                )
            bd.Location((
                0,
                set_screw_y,
                retard_cavity_z + SPRING_POCKET_DIA / 2,
            ))

        # ── 9. Exit guide channel ─────────────────────────────────────
        # After the nip zone, a short channel guides the singulated card
        # to the exit throat. Prevents curl and nose-dive.
        # Extends from the roller center toward the front (negative Y).
        exit_guide_start_y = -(ROLLER_OD / 2) - 1.0
        exit_guide_center_y = exit_guide_start_y - EXIT_GUIDE_LENGTH / 2

        # Guide channel — two walls with a slot between them
        guide_floor_z = HOPPER_WALL  # on top of the floor
        for x_sign in (-1, +1):
            rail_x = x_sign * (throat_width / 2 + EXIT_GUIDE_WALL / 2)
            with BuildPart():
                Box(
                    EXIT_GUIDE_WALL,
                    EXIT_GUIDE_LENGTH,
                    EXIT_GUIDE_HEIGHT + 2.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                bd.Location((rail_x, exit_guide_center_y, guide_floor_z))

        # Top cover of exit guide (prevents card from lifting)
        with BuildPart():
            Box(
                throat_width + 2 * EXIT_GUIDE_WALL,
                EXIT_GUIDE_LENGTH,
                EXIT_GUIDE_WALL,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            bd.Location((
                0,
                exit_guide_center_y,
                guide_floor_z + EXIT_GUIDE_HEIGHT + 2.0,
            ))

        # ── 10. Sensor mount bosses (from skeleton) ───────────────────
        sensor_boss_height = 8.0
        sensor_boss_radius = 3.0
        for x_offset in [-throat_width / 2 - 5.0, throat_width / 2 + 5.0]:
            with BuildPart():
                Cylinder(
                    radius=sensor_boss_radius,
                    height=sensor_boss_height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                bd.Location((x_offset, throat_y, HOPPER_WALL))

    return feeder.part


# ── Main ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    part = build_feeder_candidate_a()
    out_path = Path(__file__).resolve().parent / "feeder_candidate_a.step"
    export_step(part, str(out_path))
    print(f"Exported Candidate A feeder to {out_path}")
