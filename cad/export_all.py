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

    # ── Selector ─────────────────────────────────────────────────────
    print("[selector]")
    from selector.selector import build_selector
    selector_part = build_selector()
    export_part(selector_part, "selector", CAD_DIR / "selector")

    # ── Recombine ────────────────────────────────────────────────────
    print("[recombine]")
    from recombine.recombine import build_recombine
    recombine_part = build_recombine()
    export_part(recombine_part, "recombine", CAD_DIR / "recombine")

    # ── Output tray ──────────────────────────────────────────────────
    print("[output]")
    from output.output import build_output_tray
    output_part = build_output_tray()
    export_part(output_part, "output", CAD_DIR / "output")

    # ── Chassis ───────────────────────────────────────────────────────
    print("[chassis]")
    from chassis.chassis import build_chassis, build_chassis_section
    chassis_part = build_chassis()
    export_part(chassis_part, "chassis_full", CAD_DIR / "chassis")
    # Also export printable sections (3 pieces, each fits on a standard bed)
    for i in range(3):
        section = build_chassis_section(i)
        export_part(section, f"chassis_section_{i}", CAD_DIR / "chassis")

    # ── Feeder Candidate A (friction+retard baseline) ────────────────
    print("[feeder_candidate_a]")
    from feeder.candidate_a_friction_retard import build_feeder_candidate_a
    feeder_a_part = build_feeder_candidate_a()
    export_part(feeder_a_part, "feeder_candidate_a", CAD_DIR / "feeder")

    print("\nDone. All modules exported.")


if __name__ == "__main__":
    main()
