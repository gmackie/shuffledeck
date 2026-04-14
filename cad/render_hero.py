# render_hero.py — Marketing hero model for the landing page.
#
# This is NOT the engineering model. It's a stylized representation
# that reads as "card shuffler" at a glance. The chassis is removed
# (it's just a flat plate that dominates the view). Parts are
# built from scratch for visual clarity.
#
# Run: source .venv/bin/activate && cd cad && python render_hero.py

from __future__ import annotations
import sys, json, struct, tempfile
from pathlib import Path
from math import pi

CAD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CAD_DIR))

from build123d import *
import build123d as bd


# ---------------------------------------------------------------------------
# Dimensions — visually proportioned, not engineering-accurate
# ---------------------------------------------------------------------------
CARD_W = 63.5   # card width (short edge)
CARD_H = 89.0   # card height (long edge)

BIN_COUNT = 8
BIN_WALL = 2.5
BIN_INTERNAL_W = CARD_W + 3  # loose fit for visibility
BIN_INTERNAL_D = CARD_H + 3
BIN_HEIGHT = 40.0            # exaggerated from 22mm for visual weight
BIN_FLOOR = 2.0
BIN_CELL_W = BIN_INTERNAL_W + BIN_WALL
BIN_TOTAL_W = BIN_COUNT * BIN_CELL_W + BIN_WALL  # ~534

# Overall layout along X axis
FEEDER_W = 80.0
GAP = 10.0
OUTPUT_W = 75.0
TOTAL_X = FEEDER_W + GAP + BIN_TOTAL_W + GAP + OUTPUT_W

# Heights
BASE_Z = 0
BIN_TOP_Z = BIN_FLOOR + BIN_HEIGHT
RAIL_Z = BIN_TOP_Z + 12
CARRIAGE_Z = RAIL_Z + 10

MOTOR_FACE = 42.3
MOTOR_LEN = 40.0
MOTOR_SHAFT_D = 5.0

RAIL_W = 12.0
RAIL_H = 8.0


# ---------------------------------------------------------------------------
# Build functions — simple, clean shapes
# ---------------------------------------------------------------------------

def build_bin_bank_hero():
    """8 open-top bins in a row. Visually chunky."""
    with BuildPart() as bp:
        # Outer shell
        Box(BIN_TOTAL_W, BIN_INTERNAL_D + 2 * BIN_WALL, BIN_HEIGHT + BIN_FLOOR,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Cut out each bin cavity
        for i in range(BIN_COUNT):
            x = -BIN_TOTAL_W / 2 + BIN_WALL + i * BIN_CELL_W + BIN_INTERNAL_W / 2
            with Locations([(x, 0, BIN_FLOOR)]):
                Box(BIN_INTERNAL_W, BIN_INTERNAL_D, BIN_HEIGHT + 1,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT)
    return bp.part


def build_feeder_hopper():
    """Simplified hopper — angled walls, open top, slot at bottom."""
    with BuildPart() as bp:
        # Main body
        Box(FEEDER_W, CARD_H + 10, BIN_HEIGHT + 20,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Interior cavity — slightly tapered
        with Locations([(0, 0, 3)]):
            Box(CARD_W + 4, CARD_H + 4, BIN_HEIGHT + 20,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)
        # Exit slot at bottom
        with Locations([(FEEDER_W / 2 - 2, 0, 3)]):
            Box(8, CARD_W + 4, 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)
    return bp.part


def build_output_tray():
    """Simple open tray."""
    with BuildPart() as bp:
        Box(OUTPUT_W, CARD_H + 10, 30,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, 3)]):
            Box(CARD_W + 4, CARD_H + 4, 30,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)
    return bp.part


def build_selector_carriage():
    """Card guide on a carriage plate."""
    with BuildPart() as bp:
        # Carriage base plate
        Box(50, 50, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Card guide tower
        with Locations([(0, 0, 6)]):
            Box(CARD_W + 8, 10, 35,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Card slot through the tower
        with Locations([(0, 0, 6)]):
            Box(CARD_W + 2, 12, 36,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)
    return bp.part


def build_nema17():
    """Simplified NEMA17 motor body."""
    with BuildPart() as bp:
        Box(MOTOR_FACE, MOTOR_FACE, MOTOR_LEN,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Pilot boss
        with Locations([(0, 0, MOTOR_LEN)]):
            Cylinder(11, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Shaft
        with Locations([(0, 0, MOTOR_LEN)]):
            Cylinder(MOTOR_SHAFT_D / 2, 22,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Rear connector
        with Locations([(0, 0, 0)]):
            Box(16, 7, 4, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return bp.part


def build_linear_rail(length):
    """MGN12H rail + carriage."""
    with BuildPart() as bp:
        # Rail
        Box(length, RAIL_W, RAIL_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Carriage block at center
        with Locations([(0, 0, RAIL_H)]):
            Box(27, 27, 10,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
    return bp.part


def build_belt(length):
    """Thin belt strip."""
    return Box(length, 6, 1.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))


def build_base_plate():
    """Minimal base plate — just enough to ground the assembly."""
    with BuildPart() as bp:
        Box(TOTAL_X + 40, BIN_INTERNAL_D + 2 * BIN_WALL + 30, 4,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Slight chamfer on edges
        chamfer(bp.part.edges().filter_by(Axis.Z), length=1.5)
    return bp.part


# ---------------------------------------------------------------------------
# Build everything
# ---------------------------------------------------------------------------
print("Building hero model parts...\n")

bin_bank = build_bin_bank_hero()
feeder = build_feeder_hopper()
output_tray = build_output_tray()
selector = build_selector_carriage()
motor_feed = build_nema17()
motor_sel = build_nema17()
motor_rec = build_nema17()
rail_sel = build_linear_rail(BIN_TOTAL_W + 80)
rail_rec = build_linear_rail(BIN_TOTAL_W + 80)
belt_sel = build_belt(BIN_TOTAL_W + 60)
belt_sel2 = build_belt(BIN_TOTAL_W + 60)
belt_rec = build_belt(BIN_TOTAL_W + 60)
belt_rec2 = build_belt(BIN_TOTAL_W + 60)
base = build_base_plate()

# ---------------------------------------------------------------------------
# Position parts — all centered on Y=0, laid out along X
# ---------------------------------------------------------------------------
feeder_x = -TOTAL_X / 2 + FEEDER_W / 2
bin_x = feeder_x + FEEDER_W / 2 + GAP + BIN_TOTAL_W / 2
output_x = bin_x + BIN_TOTAL_W / 2 + GAP + OUTPUT_W / 2
rail_x = bin_x

# Recombine rail is behind (Y offset) the bin bank
rec_y_offset = BIN_INTERNAL_D / 2 + BIN_WALL + 25

parts = [
    # (name, shape, location, (r, g, b, a, metallic, roughness))

    # Base plate
    ("base", base,
     Location((bin_x, 0, -4)),
     (0.18, 0.19, 0.21, 1, 0.15, 0.85)),

    # Bin bank — the star of the show
    ("bins", bin_bank,
     Location((bin_x, 0, 0)),
     (0.08, 0.58, 0.42, 1, 0.08, 0.5)),   # bright teal

    # Feeder hopper
    ("feeder", feeder,
     Location((feeder_x, 0, 0)),
     (0.08, 0.58, 0.42, 1, 0.08, 0.5)),   # teal

    # Output tray
    ("output", output_tray,
     Location((output_x, 0, 0)),
     (0.08, 0.58, 0.42, 1, 0.08, 0.5)),   # teal

    # Selector rail — above bin bank
    ("sel_rail", rail_sel,
     Location((rail_x, 0, RAIL_Z)),
     (0.60, 0.62, 0.65, 1, 0.75, 0.2)),   # steel

    # Selector carriage — on the rail, positioned at bin 2
    ("selector", selector,
     Location((bin_x - BIN_TOTAL_W / 2 + 2.5 * BIN_CELL_W, 0, CARRIAGE_Z)),
     (0.10, 0.68, 0.48, 1, 0.1, 0.45)),   # lighter teal

    # Selector motor — left end of selector rail
    ("sel_motor", motor_sel,
     Location((rail_x - BIN_TOTAL_W / 2 - 45, 0, RAIL_Z + 4), (0, -90, 0)),
     (0.14, 0.14, 0.16, 1, 0.35, 0.55)),  # motor dark

    # Selector belts (top + bottom run)
    ("sel_belt_t", belt_sel,
     Location((rail_x, 0, RAIL_Z + RAIL_H + 2)),
     (0.96, 0.62, 0.08, 1, 0.0, 0.5)),    # orange

    ("sel_belt_b", belt_sel2,
     Location((rail_x, 0, RAIL_Z - 2)),
     (0.96, 0.62, 0.08, 1, 0.0, 0.5)),    # orange

    # Recombine rail — behind the bin bank
    ("rec_rail", rail_rec,
     Location((rail_x, rec_y_offset, 0)),
     (0.60, 0.62, 0.65, 1, 0.75, 0.2)),   # steel

    # Recombine motor — left end
    ("rec_motor", motor_rec,
     Location((rail_x - BIN_TOTAL_W / 2 - 45, rec_y_offset, 4), (0, -90, 0)),
     (0.14, 0.14, 0.16, 1, 0.35, 0.55)),  # motor dark

    # Recombine belts
    ("rec_belt_t", belt_rec,
     Location((rail_x, rec_y_offset, RAIL_H + 2)),
     (0.96, 0.62, 0.08, 1, 0.0, 0.5)),    # orange

    ("rec_belt_b", belt_rec2,
     Location((rail_x, rec_y_offset, -2)),
     (0.96, 0.62, 0.08, 1, 0.0, 0.5)),    # orange

    # Feeder motor — below feeder, shaft pointing up
    ("feed_motor", motor_feed,
     Location((feeder_x, 0, 0), (180, 0, 0)),
     (0.14, 0.14, 0.16, 1, 0.35, 0.55)),  # motor dark
]

# ---------------------------------------------------------------------------
# Export pipeline: part → temp GLB → merge with baked materials
# ---------------------------------------------------------------------------

def read_glb(path):
    with open(path, "rb") as f:
        f.read(4)  # magic
        f.read(4)  # version
        total_len = struct.unpack("<I", f.read(4))[0]
        json_len = struct.unpack("<I", f.read(4))[0]
        f.read(4)  # chunk type
        json_data = json.loads(f.read(json_len).decode("utf-8"))
        bin_data = b""
        if f.tell() < total_len:
            bin_len = struct.unpack("<I", f.read(4))[0]
            f.read(4)  # chunk type
            bin_data = f.read(bin_len)
    return json_data, bin_data


def write_glb(json_dict, bin_data, out_path):
    json_bytes = json.dumps(json_dict, separators=(",", ":")).encode("utf-8")
    json_pad = (4 - len(json_bytes) % 4) % 4
    json_bytes += b" " * json_pad
    bin_pad = (4 - len(bin_data) % 4) % 4
    bin_data += b"\x00" * bin_pad
    total = 12 + 8 + len(json_bytes) + 8 + len(bin_data)
    with open(out_path, "wb") as f:
        f.write(b"glTF")
        f.write(struct.pack("<I", 2))
        f.write(struct.pack("<I", total))
        f.write(struct.pack("<I", len(json_bytes)))
        f.write(struct.pack("<I", 0x4E4F534A))
        f.write(json_bytes)
        f.write(struct.pack("<I", len(bin_data)))
        f.write(struct.pack("<I", 0x004E4942))
        f.write(bin_data)


SITE_DIR = CAD_DIR.parent / "site"
TMP_DIR = Path(tempfile.mkdtemp(prefix="hero_"))

print(f"Exporting {len(parts)} parts...\n")

part_glbs = []
for name, shape, loc, color in parts:
    moved = shape.moved(loc)
    tmp = TMP_DIR / f"{name}.glb"
    export_gltf(moved, str(tmp), binary=True)
    bb = moved.bounding_box()
    print(f"  {name}: size {bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}")
    part_glbs.append((name, tmp, color))

print("\nMerging with baked PBR materials...")

merged = {
    "asset": {"version": "2.0", "generator": "ShuffleDeck hero"},
    "scene": 0,
    "scenes": [{"nodes": []}],
    "nodes": [],
    "meshes": [],
    "accessors": [],
    "bufferViews": [],
    "buffers": [{"byteLength": 0}],
    "materials": [],
}
merged_bin = bytearray()

for name, glb_path, color in part_glbs:
    r, g, b, a, metal, rough = color
    src, src_bin = read_glb(glb_path)
    if not src.get("meshes"):
        continue

    acc_off = len(merged["accessors"])
    bv_off = len(merged["bufferViews"])
    mesh_off = len(merged["meshes"])
    mat_idx = len(merged["materials"])
    bin_off = len(merged_bin)

    merged["materials"].append({
        "name": name,
        "pbrMetallicRoughness": {
            "baseColorFactor": [r, g, b, a],
            "metallicFactor": metal,
            "roughnessFactor": rough,
        },
    })

    for bv in src.get("bufferViews", []):
        nbv = dict(bv)
        nbv["buffer"] = 0
        nbv["byteOffset"] = bv.get("byteOffset", 0) + bin_off
        merged["bufferViews"].append(nbv)

    for acc in src.get("accessors", []):
        nacc = dict(acc)
        if "bufferView" in nacc:
            nacc["bufferView"] += bv_off
        merged["accessors"].append(nacc)

    for mesh in src.get("meshes", []):
        nm = {"name": name, "primitives": []}
        for prim in mesh["primitives"]:
            np = {}
            if "attributes" in prim:
                np["attributes"] = {k: v + acc_off for k, v in prim["attributes"].items()}
            if "indices" in prim:
                np["indices"] = prim["indices"] + acc_off
            np["material"] = mat_idx
            if "mode" in prim:
                np["mode"] = prim["mode"]
            nm["primitives"].append(np)
        merged["meshes"].append(nm)

    for i in range(len(src.get("meshes", []))):
        nidx = len(merged["nodes"])
        merged["scenes"][0]["nodes"].append(nidx)
        merged["nodes"].append({"name": name, "mesh": mesh_off + i})

    merged_bin.extend(src_bin)

merged["buffers"][0]["byteLength"] = len(merged_bin)

out_path = SITE_DIR / "assembly.glb"
write_glb(merged, bytes(merged_bin), out_path)

# Cleanup
for _, p, _ in part_glbs:
    p.unlink(missing_ok=True)
TMP_DIR.rmdir()

sz = out_path.stat().st_size / 1024
print(f"\nExported: {out_path} ({sz:.0f} KB)")
print(f"Parts: {len(parts)}, Materials: {len(merged['materials'])}, Meshes: {len(merged['meshes'])}")
print("Done.")
