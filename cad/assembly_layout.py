from __future__ import annotations

from build123d import Location

from bin_bank import bin_bank_info
from chassis.chassis import chassis_info


def align_bbox_min(part, *, x_min: float | None = None, y_min: float | None = None, z_min: float | None = None) -> Location:
    """Return a translation that places the part's bbox min at the requested coordinates."""
    bb = part.bounding_box()
    dx = (x_min - bb.min.X) if x_min is not None else 0.0
    dy = (y_min - bb.min.Y) if y_min is not None else 0.0
    dz = (z_min - bb.min.Z) if z_min is not None else 0.0
    return Location((dx, dy, dz))


def render_locations(parts: dict[str, object]) -> dict[str, Location]:
    """
    Position parts by their actual extents instead of assuming their local origins
    already match the chassis datums.
    """
    ci = chassis_info()
    bb = bin_bank_info()
    datum_a_z = ci["datum_a_z"]

    locations: dict[str, Location] = {}

    if "chassis" in parts:
        locations["chassis"] = Location((0, 0, 0))
    if "feeder" in parts:
        locations["feeder"] = align_bbox_min(parts["feeder"], x_min=ci["feeder_zone"][0], y_min=0.0, z_min=datum_a_z)
    if "feeder_a" in parts:
        locations["feeder_a"] = align_bbox_min(parts["feeder_a"], x_min=ci["feeder_zone"][0], y_min=0.0, z_min=datum_a_z)
    if "bin_bank" in parts:
        locations["bin_bank"] = align_bbox_min(parts["bin_bank"], x_min=ci["bin_bank_zone"][0], y_min=0.0, z_min=datum_a_z)
    if "selector" in parts:
        locations["selector"] = align_bbox_min(
            parts["selector"],
            x_min=ci["bin_bank_zone"][0],
            y_min=0.0,
            z_min=datum_a_z + bb["bank_height"],
        )
    if "recombine" in parts:
        locations["recombine"] = align_bbox_min(
            parts["recombine"],
            x_min=ci["bin_bank_zone"][0],
            y_min=bb["bank_depth"] + 5.0,
            z_min=datum_a_z,
        )
    if "output" in parts:
        locations["output"] = align_bbox_min(parts["output"], x_min=ci["output_zone"][0], y_min=0.0, z_min=datum_a_z)
    if "output_tray" in parts:
        locations["output_tray"] = align_bbox_min(parts["output_tray"], x_min=ci["output_zone"][0], y_min=0.0, z_min=datum_a_z)

    return locations
