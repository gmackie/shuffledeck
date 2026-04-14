from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD_ROOT = ROOT / "cad"
sys.path.insert(0, str(CAD_ROOT))

from bin_bank import BIN_SPACING, build_bin_bank, bin_bank_info
from feeder.candidate_a_friction_retard import build_feeder_candidate_a
from selector.selector import CARRIAGE_LENGTH, build_selector


def test_bin_bank_opens_every_bin_cavity() -> None:
    part = build_bin_bank()
    info = bin_bank_info()

    xs = [
        -info["bank_total_width"] / 2 + info["cell_width"] / 2 + i * (info["cell_width"] + BIN_SPACING)
        for i in range(info["bin_count"])
    ]

    blocked_bins = [i for i, x in enumerate(xs) if part.is_inside((x, 0.0, 10.0))]

    assert blocked_bins == [], f"expected all bin centers to be open cavities, but bins {blocked_bins} are solid"


def test_selector_includes_end_motor_mount_geometry() -> None:
    part = build_selector()
    bbox = part.bounding_box()

    assert bbox.size.X > CARRIAGE_LENGTH + 10.0, (
        "selector bbox never grows beyond the carriage block, "
        "so the end motor mount is not being positioned into the assembly"
    )


def test_feeder_candidate_a_builds_as_one_solid() -> None:
    part = build_feeder_candidate_a()

    assert len(part.solids()) == 1, "feeder candidate A should export as one printable solid"


def test_cad_sources_do_not_leave_noop_location_or_rotation_calls() -> None:
    offenders: list[str] = []

    for path in CAD_ROOT.rglob("*.py"):
        if path.name == "__init__.py":
            continue

        text = path.read_text()
        if "bd.Location(" in text or "bd.Rotation(" in text:
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == [], f"found no-op Build123d placement calls in: {offenders}"


def test_render_images_can_measure_projected_shape_lists() -> None:
    from render_images import projected_max_dim

    part = build_feeder_candidate_a()
    visible, _hidden = part.project_to_viewport((100, -100, 80), viewport_up=(0, 0, 1))

    max_dim = projected_max_dim(visible)

    assert max_dim > 0


def test_render_assembly_modules_do_not_overlap_each_other() -> None:
    from render_images import build_render_parts

    parts = build_render_parts()
    boxes = {name: part.moved(loc).bounding_box() for name, (part, loc) in parts.items()}

    def overlaps(a, b) -> bool:
        return (
            a.min.X < b.max.X and b.min.X < a.max.X and
            a.min.Y < b.max.Y and b.min.Y < a.max.Y and
            a.min.Z < b.max.Z and b.min.Z < a.max.Z
        )

    offenders: list[tuple[str, str]] = []
    names = [name for name in boxes if name != "chassis"]
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            if overlaps(boxes[left], boxes[right]):
                offenders.append((left, right))

    assert offenders == [], f"render assembly still has overlapping modules: {offenders}"


def test_site_hero_uses_stylized_scene_instead_of_raw_engineering_assembly() -> None:
    from render_hero import build_hero_parts

    parts = build_hero_parts()
    names = {name for name, *_rest in parts}

    assert len(parts) >= 10, "site hero should be a richer stylized scene than the 6-part engineering assembly"
    assert "chassis" not in names, "site hero should not expose the engineering chassis block"
    assert {"base", "bins", "feeder", "output", "selector"}.issubset(names)


def test_site_viewer_cache_busts_assembly_glb() -> None:
    site_index = (ROOT / "site" / "index.html").read_text()

    assert "assembly.glb?v=" in site_index, "site viewer should version the GLB URL so browsers fetch fresh exports"
