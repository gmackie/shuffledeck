from __future__ import annotations

import sys
from pathlib import Path

from build123d import Compound, ExportSVG, LineType, Location, export_gltf

CAD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CAD_DIR))

from assembly_layout import render_locations
from bin_bank import build_bin_bank, bin_bank_info
from chassis.chassis import build_chassis, chassis_info
from feeder.candidate_a_friction_retard import build_feeder_candidate_a
from output.output import build_output_tray
from recombine.recombine import build_recombine
from selector.selector import build_selector


RENDER_DIR = CAD_DIR / "renders"


def projected_max_dim(shapes) -> float:
    """Return the larger XY span for a projected ShapeList or Shape."""
    shape = Compound(children=list(shapes)) if hasattr(shapes, "__iter__") and not hasattr(shapes, "bounding_box") else shapes
    bb = shape.bounding_box()
    return max(bb.size.X, bb.size.Y)


def build_render_parts() -> dict[str, tuple[object, Location]]:
    print("Building parts for GLTF export...\n")

    parts = {
        "chassis": build_chassis(),
        "feeder": build_feeder_candidate_a(),
        "bin_bank": build_bin_bank(),
        "selector": build_selector(),
        "recombine": build_recombine(),
        "output_tray": build_output_tray(),
    }
    locations = render_locations(parts)
    return {name: (part, locations[name]) for name, part in parts.items()}


def export_glbs(parts: dict[str, tuple[object, Location]]) -> None:
    for name, (part, loc) in parts.items():
        moved = part.moved(loc)
        path = RENDER_DIR / f"{name}.glb"
        try:
            export_gltf(moved, str(path))
            print(f"  {name}.glb exported")
        except Exception as exc:
            print(f"  {name}.glb FAILED: {exc}")

    print("\nExporting full assembly GLTF...")
    try:
        moved_parts = [part.moved(loc) for part, loc in parts.values()]
        assembly = Compound(children=moved_parts)
        assembly_path = RENDER_DIR / "assembly.glb"
        export_gltf(assembly, str(assembly_path))
        print(f"  assembly.glb exported ({assembly_path})")
    except Exception as exc:
        print(f"  assembly.glb FAILED: {exc}")


def export_svgs(parts: dict[str, tuple[object, Location]]) -> None:
    print("\nExporting SVG views...")
    for name in ("feeder", "bin_bank"):
        part, _loc = parts[name]
        try:
            visible, hidden = part.project_to_viewport((100, -100, 80), viewport_up=(0, 0, 1))
            svg_path = RENDER_DIR / f"{name}_view.svg"
            max_dim = projected_max_dim(visible)
            exporter = ExportSVG(scale=200.0 / max_dim if max_dim > 0 else 1.0)
            exporter.add_layer("visible", line_weight=0.5)
            exporter.add_layer("hidden", line_weight=0.2, line_type=LineType.ISO_DOT)
            exporter.add_shape(visible, layer="visible")
            exporter.add_shape(hidden, layer="hidden")
            exporter.write(str(svg_path))
            print(f"  {name}_view.svg exported")
        except Exception as exc:
            print(f"  {name}_view.svg FAILED: {exc}")


def main() -> None:
    RENDER_DIR.mkdir(exist_ok=True)
    parts = build_render_parts()
    export_glbs(parts)
    export_svgs(parts)
    print(f"\nAll renders in: {RENDER_DIR}/")
    print("Use assembly.glb in a three.js viewer for interactive 3D on the landing page.")


if __name__ == "__main__":
    main()
