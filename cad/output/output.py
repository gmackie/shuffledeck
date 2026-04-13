# Output module — receiving tray for the final shuffled deck.
# Requires: pip install build123d
#
# Simple tray that receives the fully shuffled 52-card deck after pass 2.
# Features:
#   - Pocket sized for a full deck with side guides
#   - Funnel entry chamfer to square cards as they land
#   - M3 mounting holes for chassis attachment
#   - Spring-loaded rear backstop (slot for compression spring)
#   - Open front for the dealer to pick up the deck
#
# Run standalone:  python output.py
# Outputs:         output.step

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
    CARD_CLEARANCE_WIDTH,
    CARD_CLEARANCE_HEIGHT,
    PRINT_TOL_DEFAULT,
    M3_CLEARANCE_HOLE,
    M3_HEATSET_BORE,
    M3_HEATSET_LENGTH,
    BIN_WALL_THICKNESS,
)

# ── Output tray parameters ────────────────────────────────────────────
TRAY_WALL = 2.5                  # mm — side wall thickness
TRAY_FLOOR = 2.0                 # mm — floor thickness
TRAY_SIDE_CLEARANCE = 1.5       # mm per side beyond card width
TRAY_END_CLEARANCE = 1.5        # mm beyond card height at rear

# Internal pocket dimensions
POCKET_WIDTH = CARD_WIDTH + 2 * TRAY_SIDE_CLEARANCE
POCKET_DEPTH = CARD_HEIGHT + TRAY_END_CLEARANCE  # open front, backstop at rear
POCKET_HEIGHT = DECK_STACK_HEIGHT_MAX + 5.0  # mm — full deck + finger clearance

# Outer shell dimensions
TRAY_EXT_WIDTH = POCKET_WIDTH + 2 * TRAY_WALL
TRAY_EXT_DEPTH = POCKET_DEPTH + TRAY_WALL  # one wall at rear, open front
TRAY_EXT_HEIGHT = POCKET_HEIGHT + TRAY_FLOOR

# Funnel entry — chamfered top edges guide cards into alignment
FUNNEL_CHAMFER = 3.0             # mm — 45-deg chamfer at top inner edges

# Guide rail height (raised side walls above pocket floor)
GUIDE_HEIGHT = POCKET_HEIGHT

# Spring-loaded rear backstop
BACKSTOP_WALL = 2.0             # mm — backstop plate thickness
BACKSTOP_TRAVEL = 5.0           # mm — spring compression travel
BACKSTOP_SLOT_WIDTH = POCKET_WIDTH - 4.0  # mm — slot slightly narrower than pocket
BACKSTOP_SLOT_HEIGHT = POCKET_HEIGHT - 2.0  # mm
SPRING_BORE_DIA = 6.0           # mm — fits standard 6mm OD compression spring
SPRING_BORE_DEPTH = 12.0        # mm — spring pocket depth into rear wall
SPRING_COUNT = 2                # two springs, symmetric

# Open front — cutout through front wall for dealer access
FRONT_OPENING_WIDTH = POCKET_WIDTH  # full pocket width
FRONT_OPENING_HEIGHT = POCKET_HEIGHT  # full height — no front wall above floor

# Chassis mounting
MOUNT_INSET = 8.0               # mm from tray edges


def build_output_tray() -> bd.Part:
    """Build the output tray for receiving the final shuffled deck."""

    with BuildPart() as tray:

        # ── 1. Solid base block ────────────────────────────────────────
        Box(TRAY_EXT_WIDTH, TRAY_EXT_DEPTH, TRAY_EXT_HEIGHT,
            align=(Align.CENTER, Align.MAX, Align.MIN))

        # ── 2. Hollow out the card pocket ──────────────────────────────
        with BuildPart(mode=Mode.SUBTRACT):
            Box(POCKET_WIDTH, POCKET_DEPTH, POCKET_HEIGHT,
                align=(Align.CENTER, Align.MAX, Align.MIN))
            bd.Location((0, 0, TRAY_FLOOR))

        # ── 3. Open front — remove the front wall for dealer pickup ───
        # The front face is at Y=0 (Align.MAX places rear at Y=0,
        # so front is at Y=-TRAY_EXT_DEPTH).
        with BuildPart(mode=Mode.SUBTRACT):
            Box(FRONT_OPENING_WIDTH, TRAY_WALL + 2.0, FRONT_OPENING_HEIGHT,
                align=(Align.CENTER, Align.MIN, Align.MIN))
            bd.Location((0, -TRAY_EXT_DEPTH + TRAY_WALL - 1.0, TRAY_FLOOR))

        # ── 4. Funnel entry chamfer ────────────────────────────────────
        # Wider opening at the top of the side guides to square cards.
        # Cut as a tapered pocket at the top of the walls.
        funnel_w = POCKET_WIDTH + 2 * FUNNEL_CHAMFER
        funnel_d = POCKET_DEPTH + FUNNEL_CHAMFER  # rear only, front is open
        funnel_h = FUNNEL_CHAMFER

        with BuildPart(mode=Mode.SUBTRACT):
            Box(funnel_w, funnel_d, funnel_h,
                align=(Align.CENTER, Align.MAX, Align.MAX))
            bd.Location((0, 0, TRAY_EXT_HEIGHT))

        # ── 5. Rear backstop spring pockets ────────────────────────────
        # Two cylindrical bores into the rear wall for compression springs.
        # The springs push a backstop plate forward to snug cards.
        rear_wall_y = -TRAY_WALL / 2  # center of rear wall

        spring_spacing = BACKSTOP_SLOT_WIDTH / 2  # symmetric placement
        for dx in (-spring_spacing / 2, spring_spacing / 2):
            with BuildPart(mode=Mode.SUBTRACT):
                Cylinder(
                    radius=SPRING_BORE_DIA / 2,
                    height=SPRING_BORE_DEPTH,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                # Bore goes into the rear wall along Y axis
                bd.Location((dx, 0, TRAY_FLOOR + POCKET_HEIGHT / 2))
                bd.Rotation((90, 0, 0))

        # Backstop travel slot — vertical slot in rear wall for backstop
        # plate to slide through
        with BuildPart(mode=Mode.SUBTRACT):
            Box(BACKSTOP_SLOT_WIDTH, TRAY_WALL + BACKSTOP_TRAVEL,
                BACKSTOP_SLOT_HEIGHT,
                align=(Align.CENTER, Align.MAX, Align.MIN))
            bd.Location((0, 0, TRAY_FLOOR + 1.0))

        # ── 6. Chassis mounting holes ──────────────────────────────────
        # Four M3 heat-set insert bores at the base corners.
        mount_positions = [
            (-TRAY_EXT_WIDTH / 2 + MOUNT_INSET,
             -TRAY_EXT_DEPTH + MOUNT_INSET),
            (-TRAY_EXT_WIDTH / 2 + MOUNT_INSET,
             -MOUNT_INSET),
            (TRAY_EXT_WIDTH / 2 - MOUNT_INSET,
             -TRAY_EXT_DEPTH + MOUNT_INSET),
            (TRAY_EXT_WIDTH / 2 - MOUNT_INSET,
             -MOUNT_INSET),
        ]
        for mx, my in mount_positions:
            with BuildPart(mode=Mode.SUBTRACT):
                Cylinder(
                    radius=M3_HEATSET_BORE / 2,
                    height=M3_HEATSET_LENGTH + 1.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                bd.Location((mx, my, 0))

    return tray.part


# ── Main ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    part = build_output_tray()
    out_path = Path(__file__).resolve().parent / "output.step"
    export_step(part, str(out_path))
    print(f"Exported output tray to {out_path}")
