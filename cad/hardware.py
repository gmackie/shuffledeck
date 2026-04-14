# hardware.py — Simplified visual models of bought components.
# These are NOT printable parts. They exist so the assembly
# render looks like an actual machine with motors, rails, and belts.

from __future__ import annotations
from build123d import *
from constants import *


def build_nema17(body_length: float = NEMA17_BODY_LENGTH_STANDARD) -> Compound:
    """NEMA17 stepper motor — visual model only."""
    face = NEMA17_FACE
    hl = NEMA17_HOLE_SPACING / 2  # half diagonal

    # Main body — box with chamfered vertical edges
    body = Box(face, face, body_length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = chamfer(body.edges().filter_by(Axis.Z), length=2.0)

    # Front face boss (pilot)
    pilot = Pos(0, 0, body_length) * Cylinder(
        NEMA17_PILOT_DIAMETER / 2, NEMA17_PILOT_DEPTH,
        align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    # Shaft
    shaft = Pos(0, 0, body_length) * Cylinder(
        NEMA17_SHAFT_DIAMETER / 2, 24,
        align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    # Mounting bolt heads (visual only — small cylinders on the face)
    bolts = []
    for dx, dy in [(-hl, -hl), (-hl, hl), (hl, -hl), (hl, hl)]:
        bolt = Pos(dx, dy, body_length) * Cylinder(
            M3_HEAD_DIAMETER / 2, 2,
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        bolts.append(bolt)

    # Rear shaft stub
    rear_shaft = Pos(0, 0, 0) * Cylinder(
        3, 3, align=(Align.CENTER, Align.CENTER, Align.MAX)
    )

    # Connector bump on back face
    connector = Pos(0, 0, 0) * Box(
        16, 7, 4, align=(Align.CENTER, Align.CENTER, Align.MAX)
    )

    motor = body + pilot + shaft + rear_shaft + connector
    for b in bolts:
        motor = motor + b
    return motor


def build_mgn12h_rail(length: float = 600.0) -> Compound:
    """MGN12H linear rail + carriage block — visual model."""
    # Rail profile: 12mm wide, 8mm tall, length along X
    rail = Box(length, 12, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Carriage block: 27mm long, 27mm wide, 10mm tall, centered on rail
    carriage = Pos(0, 0, 8) * Box(
        27, 27, 10, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    # Carriage mounting holes (4× M3 in 20×12mm pattern, visual only)
    holes = []
    for dx in [-10, 10]:
        for dy in [-6, 6]:
            hole = Pos(dx, dy, 18) * Cylinder(
                1.5, 3, align=(Align.CENTER, Align.CENTER, Align.MIN)
            )
            holes.append(hole)

    assembly = rail + carriage
    for h in holes:
        assembly = assembly + h
    return assembly


def build_gt2_pulley(teeth: int = 20) -> Part:
    """GT2 timing pulley — visual model."""
    # 20T GT2: ~12.73mm pitch diameter, we'll use 12.7mm OD
    od = teeth * 2.0 / 3.14159  # approximate
    pulley = Cylinder(od / 2, 7, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    # Flanges
    flange_top = Pos(0, 0, 3.5) * Cylinder(od / 2 + 1.5, 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    flange_bot = Pos(0, 0, -3.5) * Cylinder(od / 2 + 1.5, 1, align=(Align.CENTER, Align.CENTER, Align.MAX))
    # Bore
    bore = Cylinder(NEMA17_SHAFT_DIAMETER / 2, 10, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return pulley + flange_top + flange_bot - bore


def build_belt_segment(p1: tuple, p2: tuple, width: float = 6.0) -> Part:
    """Straight belt segment between two points — visual model.
    p1, p2 are (x, y, z) tuples."""
    from math import sqrt
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1:
        return Box(1, 1, 1)  # degenerate

    # Build belt as a thin box along X, then position
    belt = Box(length, width, 1.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    # Center between the two points
    cx = (p1[0] + p2[0]) / 2
    cy = (p1[1] + p2[1]) / 2
    cz = (p1[2] + p2[2]) / 2

    from math import atan2, degrees
    angle = degrees(atan2(dy, dx))

    return Pos(cx, cy, cz) * Rot(0, 0, angle) * belt


def build_608zz_bearing() -> Part:
    """608ZZ bearing — visual model. 8×22×7mm."""
    outer = Cylinder(11, 7, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    bore = Cylinder(4, 8, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return outer - bore


def build_625zz_bearing() -> Part:
    """625ZZ bearing — visual model. 5×16×5mm."""
    outer = Cylinder(8, 5, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    bore = Cylinder(2.5, 6, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return outer - bore
