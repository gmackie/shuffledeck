from __future__ import annotations

import json
import struct
import sys
import tempfile
from pathlib import Path

from build123d import Align, Axis, Box, BuildPart, Cylinder, Location, Locations, Mode, chamfer, export_gltf


CAD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CAD_DIR))


CARD_W = 63.5
CARD_H = 89.0

BIN_COUNT = 8
BIN_WALL = 2.5
BIN_INTERNAL_W = CARD_W + 3.0
BIN_INTERNAL_D = CARD_H + 3.0
BIN_HEIGHT = 48.0
BIN_FLOOR = 2.0
BIN_CELL_W = BIN_INTERNAL_W + BIN_WALL
BIN_TOTAL_W = BIN_COUNT * BIN_CELL_W + BIN_WALL

FEEDER_W = 86.0
OUTPUT_W = 82.0
GAP = 14.0
TOTAL_X = FEEDER_W + GAP + BIN_TOTAL_W + GAP + OUTPUT_W

RAIL_Z = BIN_FLOOR + BIN_HEIGHT + 12.0
CARRIAGE_Z = RAIL_Z + 8.0
RECOMBINE_Y = BIN_INTERNAL_D / 2 + BIN_WALL + 42.0

MOTOR_FACE = 42.3
MOTOR_LEN = 40.0
MOTOR_SHAFT_D = 5.0

RAIL_W = 12.0
RAIL_H = 8.0


def build_bin_bank_hero():
    with BuildPart() as bp:
        Box(
            BIN_TOTAL_W,
            BIN_INTERNAL_D + 2 * BIN_WALL,
            BIN_HEIGHT + BIN_FLOOR,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        for i in range(BIN_COUNT):
            x = -BIN_TOTAL_W / 2 + BIN_WALL + i * BIN_CELL_W + BIN_INTERNAL_W / 2
            with Locations([(x, 0, BIN_FLOOR)]):
                Box(
                    BIN_INTERNAL_W,
                    BIN_INTERNAL_D,
                    BIN_HEIGHT + 1.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )
    return bp.part


def build_feeder_hopper():
    with BuildPart() as bp:
        Box(FEEDER_W, CARD_H + 14, BIN_HEIGHT + 24, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, 3)]):
            Box(
                CARD_W + 8,
                CARD_H + 6,
                BIN_HEIGHT + 25,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
        with Locations([(FEEDER_W / 2 - 3, 0, 3)]):
            Box(10, CARD_W + 6, 2.4, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    return bp.part


def build_output_tray():
    with BuildPart() as bp:
        Box(OUTPUT_W, CARD_H + 14, 28, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, 3)]):
            Box(CARD_W + 8, CARD_H + 6, 28, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    return bp.part


def build_selector_carriage():
    with BuildPart() as bp:
        Box(54, 46, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, 6)]):
            Box(CARD_W + 10, 12, 38, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, 6)]):
            Box(CARD_W + 2, 14, 39, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    return bp.part


def build_linear_rail(length: float):
    with BuildPart() as bp:
        Box(length, RAIL_W, RAIL_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, RAIL_H)]):
            Box(26, 26, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return bp.part


def build_recombine_bridge():
    with BuildPart() as bp:
        Box(BIN_TOTAL_W * 0.78, 28, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, 2.5)]):
            Box(BIN_TOTAL_W * 0.68, 22, 12, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    return bp.part


def build_recombine_head():
    with BuildPart() as bp:
        Box(44, 24, 18, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, 18)]):
            Box(18, 20, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return bp.part


def build_nema17():
    with BuildPart() as bp:
        Box(MOTOR_FACE, MOTOR_FACE, MOTOR_LEN, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, MOTOR_LEN)]):
            Cylinder(11, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, MOTOR_LEN)]):
            Cylinder(MOTOR_SHAFT_D / 2, 18, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(0, 0, 0)]):
            Box(16, 7, 4, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return bp.part


def build_belt(length: float):
    return Box(length, 6, 1.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))


def build_base_plate():
    with BuildPart() as bp:
        Box(TOTAL_X + 50, BIN_INTERNAL_D + 2 * BIN_WALL + 120, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
        chamfer(bp.part.edges().filter_by(Axis.Z), length=1.5)
    return bp.part


def build_card_stack(height: float):
    with BuildPart() as bp:
        Box(CARD_W, CARD_H, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations([(1.5, 1.0, height)]):
            Box(CARD_W, CARD_H, 0.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return bp.part


def build_hero_parts():
    print("Building hero model parts...\n")

    feeder_x = -TOTAL_X / 2 + FEEDER_W / 2
    bin_x = feeder_x + FEEDER_W / 2 + GAP + BIN_TOTAL_W / 2
    output_x = bin_x + BIN_TOTAL_W / 2 + GAP + OUTPUT_W / 2
    selector_x = bin_x - BIN_TOTAL_W / 2 + 2.2 * BIN_CELL_W
    recombine_x = bin_x + BIN_TOTAL_W * 0.08

    base = build_base_plate()
    bins = build_bin_bank_hero()
    feeder = build_feeder_hopper()
    output = build_output_tray()
    sel_rail = build_linear_rail(BIN_TOTAL_W + 48)
    selector = build_selector_carriage()
    sel_motor = build_nema17()
    feed_motor = build_nema17()
    rec_motor = build_nema17()
    recombine_bridge = build_recombine_bridge()
    recombine_head = build_recombine_head()
    sel_belt = build_belt(BIN_TOTAL_W + 24)
    cards_in = build_card_stack(14)
    cards_out = build_card_stack(6)

    teal = (0.08, 0.58, 0.42, 1, 0.08, 0.50)
    teal_light = (0.12, 0.66, 0.48, 1, 0.06, 0.55)
    chassis_dark = (0.18, 0.19, 0.21, 1, 0.15, 0.85)
    steel = (0.46, 0.50, 0.56, 1, 0.55, 0.28)
    motor_dark = (0.13, 0.14, 0.16, 1, 0.32, 0.58)
    belt_orange = (0.96, 0.62, 0.08, 1, 0.0, 0.5)
    card_cream = (0.95, 0.93, 0.88, 1, 0.0, 0.92)

    return [
        ("base", base, Location((bin_x, RECOMBINE_Y / 2 - 6, -4)), chassis_dark),
        ("bins", bins, Location((bin_x, 0, 0)), teal_light),
        ("feeder", feeder, Location((feeder_x, 0, 0)), teal),
        ("output", output, Location((output_x, 0, 0)), teal),
        ("sel_rail", sel_rail, Location((bin_x, 0, RAIL_Z)), steel),
        ("selector", selector, Location((selector_x, 0, CARRIAGE_Z)), teal),
        ("sel_motor", sel_motor, Location((bin_x - BIN_TOTAL_W / 2 - 40, 0, RAIL_Z + 3), (0, -90, 0)), motor_dark),
        ("feed_motor", feed_motor, Location((feeder_x, 0, -2), (180, 0, 0)), motor_dark),
        ("recombine_bridge", recombine_bridge, Location((recombine_x, RECOMBINE_Y, 6)), steel),
        ("recombine_head", recombine_head, Location((bin_x + BIN_TOTAL_W * 0.18, RECOMBINE_Y, 15)), teal),
        ("rec_motor", rec_motor, Location((bin_x - BIN_TOTAL_W / 2 - 36, RECOMBINE_Y, 2), (0, -90, 0)), motor_dark),
        ("sel_belt", sel_belt, Location((bin_x, 0, RAIL_Z + 10)), belt_orange),
        ("cards_in", cards_in, Location((feeder_x - 6, 0, 18)), card_cream),
        ("cards_out", cards_out, Location((output_x - 4, 0, 4)), card_cream),
    ]


def read_glb(path: Path):
    with open(path, "rb") as f:
        if f.read(4) != b"glTF":
            raise RuntimeError(f"{path} is not a binary GLB")
        f.read(4)
        total_len = struct.unpack("<I", f.read(4))[0]
        json_len = struct.unpack("<I", f.read(4))[0]
        f.read(4)
        json_data = json.loads(f.read(json_len).decode("utf-8"))
        bin_data = b""
        if f.tell() < total_len:
            bin_len = struct.unpack("<I", f.read(4))[0]
            f.read(4)
            bin_data = f.read(bin_len)
    return json_data, bin_data


def write_glb(json_dict, bin_data: bytes, out_path: Path):
    json_bytes = json.dumps(json_dict, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * ((4 - len(json_bytes) % 4) % 4)
    bin_data += b"\x00" * ((4 - len(bin_data) % 4) % 4)
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


def export_site_hero() -> Path:
    site_dir = CAD_DIR.parent / "site"
    tmp_dir = Path(tempfile.mkdtemp(prefix="hero_"))
    parts = build_hero_parts()

    print(f"Exporting {len(parts)} parts...\n")

    part_glbs = []
    for name, shape, loc, color in parts:
        moved = shape.moved(loc)
        tmp = tmp_dir / f"{name}.glb"
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

        merged["materials"].append(
            {
                "name": name,
                "pbrMetallicRoughness": {
                    "baseColorFactor": [r, g, b, a],
                    "metallicFactor": metal,
                    "roughnessFactor": rough,
                },
            }
        )

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

    out_path = site_dir / "assembly.glb"
    write_glb(merged, bytes(merged_bin), out_path)

    for _, p, _ in part_glbs:
        p.unlink(missing_ok=True)
    tmp_dir.rmdir()

    sz = out_path.stat().st_size / 1024
    print(f"\nExported: {out_path} ({sz:.0f} KB)")
    print(f"Parts: {len(parts)}, Materials: {len(merged['materials'])}, Meshes: {len(merged['meshes'])}")
    print("Done.")
    return out_path


def main() -> None:
    export_site_hero()


if __name__ == "__main__":
    main()
