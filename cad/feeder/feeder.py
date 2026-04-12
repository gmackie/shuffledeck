# Feeder module — parametric skeleton for the card shuffler.
# Requires: pip install build123d
#
# This is SCAFFOLDING, not a finished design. The singulation mechanism
# depends on the feeder bakeoff results (see docs/tests/feeder-bakeoff.md).
# Bakeoff candidates: friction+retard, escapement gate, vacuum pickup,
# kicker+weight. This file builds only the hopper envelope, exit throat,
# and NEMA17 mount. The winning singulation geometry plugs in at the
# marked placeholder locations.
#
# Run standalone:  python feeder.py
# Outputs:         feeder.step

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
    BIN_WALL_THICKNESS,
)

# ── Feeder parameters ──────────────────────────────────────────────────
HOPPER_ANGLE_DEG = 15.0       # incline angle (tunable 5-25 deg)
HOPPER_WALL = 3.0             # mm wall thickness
HOPPER_SIDE_CLEARANCE = 2.0   # mm per side beyond card width
HOPPER_END_CLEARANCE = 2.0    # mm beyond card height at rear
HOPPER_DEPTH = DECK_STACK_HEIGHT_MAX + 10.0  # mm — room for full deck + finger
EXIT_THROAT_GAP = CARD_THICKNESS + 0.5  # mm — sized for ONE card + clearance
MOUNTING_PLATE_THICKNESS = 5.0  # mm

# Derived hopper internal dims
HOPPER_INT_W = CARD_WIDTH + 2 * HOPPER_SIDE_CLEARANCE
HOPPER_INT_L = CARD_HEIGHT + HOPPER_END_CLEARANCE
HOPPER_EXT_W = HOPPER_INT_W + 2 * HOPPER_WALL
HOPPER_EXT_L = HOPPER_INT_L + 2 * HOPPER_WALL


def build_feeder() -> bd.Part:
    """Build the feeder module skeleton."""

    with BuildPart() as feeder:

        # ── Hopper body (open-top box) ──────────────────────────────
        # Outer shell
        Box(HOPPER_EXT_W, HOPPER_EXT_L, HOPPER_DEPTH + HOPPER_WALL,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Hollow interior (subtract)
        with BuildPart(mode=Mode.SUBTRACT):
            Box(HOPPER_INT_W, HOPPER_INT_L, HOPPER_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Shift up by floor thickness
            bd.Location((0, 0, HOPPER_WALL))

        # ── Exit throat slot at the bottom-front face ───────────────
        # A horizontal slot through the front wall, sized for one card.
        throat_width = CARD_WIDTH + 2 * PRINT_TOL_DEFAULT
        throat_y = -(HOPPER_EXT_L / 2)  # front face
        with BuildPart(mode=Mode.SUBTRACT):
            Box(throat_width, HOPPER_WALL + 2.0, EXIT_THROAT_GAP,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, throat_y, HOPPER_WALL))

        # ── NEMA17 mounting boss ────────────────────────────────────
        # Flat plate on the underside of the hopper for the drive motor.
        motor_plate_z = -MOUNTING_PLATE_THICKNESS
        with BuildPart() as _motor_plate:
            Box(NEMA17_FACE + 10.0, NEMA17_FACE + 10.0, MOUNTING_PLATE_THICKNESS,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            bd.Location((0, 0, motor_plate_z))

        # NEMA17 mounting holes (4x M3 on 31 mm diagonal pattern)
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

        # Central pilot hole for NEMA17 boss
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

        # ────────────────────────────────────────────────────────────
        # BAKEOFF PLACEHOLDER: Singulation mechanism geometry
        #
        # The winning candidate from the feeder bakeoff plugs in here.
        # Depending on the winner, this region will contain one of:
        #
        #   Candidate A (friction + retard):
        #     - Driven roller pocket in the floor, O-ring groove
        #     - Retard pad slot on the opposite side of the throat
        #     - Spring-loaded pressure adjustment geometry
        #
        #   Candidate B (escapement gate):
        #     - Reciprocating finger slot through the floor
        #     - Return spring pocket
        #     - Dwell-stop geometry
        #
        #   Candidate C (vacuum pickup):
        #     - Suction head recess in the floor
        #     - Pneumatic fitting port
        #     - Transport belt channel
        #
        #   Candidate D (kicker + weight):
        #     - Kicker wheel pocket (side access)
        #     - Weight guide channel
        #     - Side rail adjustment slots
        #
        # Each candidate will define a function:
        #   add_singulation_geometry(feeder_part, constants) -> Part
        # that cuts/adds the required features to this base.
        # ────────────────────────────────────────────────────────────

        # ── Sensor mount bosses (2x, at exit throat) ───────────────
        # Placeholder posts for IR break-beam sensors (TCRT5000 or similar)
        sensor_boss_height = 8.0
        sensor_boss_radius = 3.0
        for i, x_offset in enumerate([-throat_width / 2 - 5.0, throat_width / 2 + 5.0]):
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
    part = build_feeder()
    out_path = Path(__file__).resolve().parent / "feeder.step"
    export_step(part, str(out_path))
    print(f"Exported feeder to {out_path}")
