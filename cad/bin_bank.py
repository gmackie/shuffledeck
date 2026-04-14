# Bin bank module — 8-bin FIFO storage for the 2-pass card shuffler.
# Requires: pip install build123d
#
# Architecture-locked: 2-pass, 8-bin random FIFO (validated at ~9.2
# riffle-equivalents by sim). This module is more complete than the
# feeder skeleton since the bin geometry is settled.
#
# Each bin: vertical slot accepting cards from above via funnel entry,
# holding up to 10 cards in a stack, with smooth walls and chamfered
# entries for tolerance.
#
# Parametric on: bin_count, card clearance, wall thickness, funnel chamfer.
#
# Run standalone:  python bin_bank.py
# Outputs:         bin_bank.step

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build123d import (
    BuildPart,
    Box,
    Align,
    Mode,
    export_step,
    export_stl,
    chamfer,
)
import build123d as bd

from constants import (
    CARD_WIDTH,
    CARD_HEIGHT,
    CARD_CLEARANCE_WIDTH,
    CARD_CLEARANCE_HEIGHT,
    BIN_COUNT,
    BIN_MAX_CARDS,
    BIN_WALL_THICKNESS,
    BIN_FLOOR_THICKNESS,
    BIN_INTERNAL_HEIGHT,
    BIN_ENTRY_FUNNEL_CHAMFER,
    BIN_SPACING,
    CARD_THICKNESS,
    PRINT_TOL_DEFAULT,
)


def build_bin_bank(
    bin_count: int = BIN_COUNT,
    card_clearance_w: float = CARD_CLEARANCE_WIDTH,
    card_clearance_h: float = CARD_CLEARANCE_HEIGHT,
    wall: float = BIN_WALL_THICKNESS,
    floor: float = BIN_FLOOR_THICKNESS,
    internal_height: float = BIN_INTERNAL_HEIGHT,
    funnel_chamfer: float = BIN_ENTRY_FUNNEL_CHAMFER,
    spacing: float = BIN_SPACING,
) -> bd.Part:
    """
    Build the bin bank as a single monolithic part (printable as one piece
    or split along bin boundaries for separate printing).

    Bins are arranged in a linear row along the X axis. Cards enter from
    the top (Z+) and stack vertically.
    """

    # Internal cavity per bin
    int_w = CARD_WIDTH + 2 * card_clearance_w
    int_d = CARD_HEIGHT + 2 * card_clearance_h
    int_h = internal_height

    # External dimensions per bin cell
    cell_w = int_w + 2 * wall
    cell_d = int_d + 2 * wall
    cell_h = int_h + floor  # no top wall (open top for card entry)

    # Total bank dimensions
    bank_w = bin_count * cell_w + (bin_count - 1) * spacing
    bank_d = cell_d
    bank_h = cell_h

    # Funnel entry dimensions (wider opening at top that tapers to bin cavity)
    funnel_extra = funnel_chamfer  # how much wider the top opening is per side
    funnel_h = funnel_chamfer      # height of the funnel taper zone
    funnel_w = int_w + 2 * funnel_extra
    funnel_d = int_d + 2 * funnel_extra

    with BuildPart() as bank:

        # ── Solid base block ────────────────────────────────────────
        Box(bank_w, bank_d, bank_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

        # ── Cut bin cavities ────────────────────────────────────────
        for i in range(bin_count):
            # Center X of this bin cell
            cx = -bank_w / 2 + cell_w / 2 + i * (cell_w + spacing)

            # Main cavity (card stack volume)
            with BuildPart(mode=Mode.SUBTRACT):
                with bd.Locations([(cx, 0, floor)]):
                    Box(
                        int_w,
                        int_d,
                        int_h,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )

            # Funnel entry — a wider box at the top that creates the
            # chamfered lead-in. We cut a tapered shape by stacking two
            # subtractions: the funnel opening box at the very top, and
            # letting the main cavity handle the rest. For a proper
            # chamfer we cut the funnel as a slightly wider pocket at
            # the top of the bin.
            with BuildPart(mode=Mode.SUBTRACT):
                with bd.Locations([(cx, 0, cell_h)]):
                    Box(
                        funnel_w,
                        funnel_d,
                        funnel_h,
                        align=(Align.CENTER, Align.CENTER, Align.MAX),
                    )

        # ── Chamfer top edges of the entire bank ────────────────────
        # (Build123d chamfer on specific edges would be ideal, but for
        #  scaffold simplicity we rely on the funnel cuts above to create
        #  the lead-in geometry. A proper chamfer pass can refine this
        #  once the part is validated in slicer.)

        # ── Mounting features ───────────────────────────────────────
        # Four M3 heat-set insert holes at the corners of the base for
        # attaching the bin bank to the chassis. Implemented as simple
        # cylindrical bores.
        from constants import M3_HEATSET_BORE, M3_HEATSET_LENGTH
        from build123d import Cylinder

        mount_inset_x = 8.0  # mm from edge
        mount_inset_y = 8.0
        mount_positions = [
            (-bank_w / 2 + mount_inset_x, -bank_d / 2 + mount_inset_y),
            (-bank_w / 2 + mount_inset_x,  bank_d / 2 - mount_inset_y),
            ( bank_w / 2 - mount_inset_x, -bank_d / 2 + mount_inset_y),
            ( bank_w / 2 - mount_inset_x,  bank_d / 2 - mount_inset_y),
        ]
        for mx, my in mount_positions:
            with BuildPart(mode=Mode.SUBTRACT):
                with bd.Locations([(mx, my, 0)]):
                    Cylinder(
                        radius=M3_HEATSET_BORE / 2,
                        height=M3_HEATSET_LENGTH + 1.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )

    return bank.part


def bin_bank_info(bin_count: int = BIN_COUNT) -> dict:
    """Return a summary dict of bin bank dimensions for other modules."""
    int_w = CARD_WIDTH + 2 * CARD_CLEARANCE_WIDTH
    int_d = CARD_HEIGHT + 2 * CARD_CLEARANCE_HEIGHT
    cell_w = int_w + 2 * BIN_WALL_THICKNESS
    cell_d = int_d + 2 * BIN_WALL_THICKNESS
    bank_w = bin_count * cell_w + (bin_count - 1) * BIN_SPACING
    return {
        "bin_count": bin_count,
        "internal_width": int_w,
        "internal_depth": int_d,
        "cell_width": cell_w,
        "cell_depth": cell_d,
        "bank_total_width": bank_w,
        "bank_depth": cell_d,
        "bank_height": BIN_INTERNAL_HEIGHT + BIN_FLOOR_THICKNESS,
    }


# ── Main ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    part = build_bin_bank()
    out_dir = Path(__file__).resolve().parent / "bin-bank"
    out_dir.mkdir(exist_ok=True)

    step_path = out_dir / "bin_bank.step"
    export_step(part, str(step_path))
    print(f"Exported bin bank STEP to {step_path}")

    stl_path = out_dir / "bin_bank.stl"
    export_stl(part, str(stl_path))
    print(f"Exported bin bank STL to {stl_path}")

    info = bin_bank_info()
    print(f"\nBin bank summary:")
    for k, v in info.items():
        unit = "mm" if isinstance(v, float) else ""
        print(f"  {k}: {v} {unit}")
