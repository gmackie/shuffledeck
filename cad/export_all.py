# Export all modules to STEP + STL for the full card shuffler assembly.
# Requires: pip install build123d
#
# Run:  python export_all.py
# Outputs STEP and STL files into each module's directory.

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the cad/ directory is on the path for imports
CAD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CAD_DIR))

from build123d import export_step, export_stl


def export_part(part, name: str, out_dir: Path) -> None:
    """Export a part to both STEP and STL in the given directory."""
    out_dir.mkdir(parents=True, exist_ok=True)
    step_path = out_dir / f"{name}.step"
    stl_path = out_dir / f"{name}.stl"
    export_step(part, str(step_path))
    export_stl(part, str(stl_path))
    print(f"  {name}: {step_path}")
    print(f"  {name}: {stl_path}")


def main() -> None:
    print("Card Shuffler — exporting all modules\n")

    # ── Feeder ──────────────────────────────────────────────────────
    print("[feeder]")
    from feeder.feeder import build_feeder
    feeder_part = build_feeder()
    export_part(feeder_part, "feeder", CAD_DIR / "feeder")

    # ── Bin Bank ────────────────────────────────────────────────────
    print("[bin_bank]")
    from bin_bank import build_bin_bank
    bin_bank_part = build_bin_bank()
    export_part(bin_bank_part, "bin_bank", CAD_DIR / "bin-bank")

    # ── Selector (placeholder) ──────────────────────────────────────
    # TODO: implement cad/selector/selector.py with build_selector()
    # print("[selector]")
    # from selector.selector import build_selector
    # selector_part = build_selector()
    # export_part(selector_part, "selector", CAD_DIR / "selector")

    # ── Recombine (placeholder) ─────────────────────────────────────
    # TODO: implement cad/recombine/recombine.py with build_recombine()
    # print("[recombine]")
    # from recombine.recombine import build_recombine
    # recombine_part = build_recombine()
    # export_part(recombine_part, "recombine", CAD_DIR / "recombine")

    # ── Output tray (placeholder) ───────────────────────────────────
    # TODO: implement cad/output/output.py with build_output_tray()
    # print("[output]")
    # from output.output import build_output_tray
    # output_part = build_output_tray()
    # export_part(output_part, "output", CAD_DIR / "output")

    # ── Chassis (placeholder) ───────────────────────────────────────
    # TODO: implement cad/chassis/chassis.py with build_chassis()
    # print("[chassis]")
    # from chassis.chassis import build_chassis
    # chassis_part = build_chassis()
    # export_part(chassis_part, "chassis", CAD_DIR / "chassis")

    print("\nDone. Implemented modules exported; see TODO comments for remaining.")


if __name__ == "__main__":
    main()
