# render_hero.py — Export a colored assembly GLB for the landing page.
#
# Strategy: export each part as individual GLB, then merge into one
# GLB with per-part PBR materials baked into the GLTF JSON.
#
# Run: source .venv/bin/activate && cd cad && python render_hero.py

from __future__ import annotations
import sys, json, struct, io
from pathlib import Path

CAD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CAD_DIR))

from build123d import *
import build123d as bd

from chassis.chassis import build_chassis, chassis_info, PLATE_THICKNESS
from feeder.candidate_a_friction_retard import build_feeder_candidate_a
from bin_bank import build_bin_bank, bin_bank_info
from selector.selector import build_selector
from recombine.recombine import build_recombine
from output.output import build_output_tray
from hardware import build_nema17, build_mgn12h_rail, build_gt2_pulley, build_belt_segment

_ci = chassis_info()
_bb = bin_bank_info()
DATUM_A = _ci["datum_a_z"]  # 5.0 — top of base plate

# ---------------------------------------------------------------------------
# Chassis coordinate system:
#   X: 0 = feeder end → 783 = output end
#   Y: 0 = left side rail inner face → 140 = right edge
#   Z: 0 = bottom of base plate, 5 = top of plate (Datum A)
#
# Bin bank zone: X = 105 → 675 (center X ≈ 390)
# Feeder zone:   X = 0 → 100 (center X = 50)
# Output zone:   X = 680 → 780 (center X = 730)
# ---------------------------------------------------------------------------

# Y center of the card path — bins are ~95mm deep, centered in 140mm chassis
CARD_Y = 70.0  # center of chassis depth

print("Building parts...\n")

chassis = build_chassis()
feeder = build_feeder_candidate_a()
bin_bank = build_bin_bank()
selector = build_selector()
recombine = build_recombine()
output_tray = build_output_tray()

# Hardware
feeder_motor = build_nema17()
sel_motor = build_nema17()
rec_x_motor = build_nema17()
rec_z_motor = build_nema17(body_length=34)
sel_rail = build_mgn12h_rail(600)
rec_rail = build_mgn12h_rail(600)

# ---------------------------------------------------------------------------
# Assembly: (name, shape, Location, color_rgba)
#
# Colors chosen for contrast on a dark background:
#   Printed parts: bright teal/emerald
#   Motors: dark gray with metallic
#   Rails: steel silver
#   Chassis: medium gray
#   Belts: orange
# ---------------------------------------------------------------------------

BIN_CENTER_X = 390.0  # center of bin bank zone

# Selector rail sits above the bin bank
SEL_RAIL_Z = DATUM_A + _bb["bank_height"] + 8  # ~34.5

# Recombine sits behind (higher Y) the bin bank, at base level
REC_Y = CARD_Y + _bb["bank_depth"] / 2 + 15  # ~132

parts = []

# 1. Chassis — origin at corner, no transform needed
parts.append(("chassis", chassis, Location((0, 0, 0)),
              (0.35, 0.36, 0.38, 1.0, 0.1, 0.8)))  # medium gray, matte

# 2. Bin bank — origin is center. Place center at bin zone center.
parts.append(("bin_bank", bin_bank, Location((BIN_CENTER_X, CARD_Y, DATUM_A)),
              (0.28, 0.32, 0.30, 1.0, 0.05, 0.75)))  # dark green-gray

# 3. Feeder — origin is center. Place at feeder zone.
parts.append(("feeder", feeder, Location((50, CARD_Y, DATUM_A)),
              (0.06, 0.72, 0.50, 1.0, 0.1, 0.45)))  # bright emerald

# 4. Output tray — origin center-ish but Y goes -92.9→0
#    So origin Y=0 is the front edge. We need back edge at CARD_Y+47.5
parts.append(("output", output_tray, Location((730, CARD_Y + 47, DATUM_A)),
              (0.06, 0.72, 0.50, 1.0, 0.1, 0.45)))  # emerald

# 5. Selector carriage — origin is center, place above bin 3
sel_x = BIN_CENTER_X - 50  # offset from center for visual interest
parts.append(("selector", selector, Location((sel_x, CARD_Y, SEL_RAIL_Z)),
              (0.06, 0.72, 0.50, 1.0, 0.1, 0.45)))  # emerald

# 6. Selector rail — centered at bin bank center, above bins
parts.append(("sel_rail", sel_rail, Location((BIN_CENTER_X, CARD_Y, SEL_RAIL_Z - 5)),
              (0.65, 0.67, 0.70, 1.0, 0.7, 0.25)))  # steel silver

# 7. Selector motor — at left end of rail, shaft pointing +X
#    Motor is built with shaft along +Z. Rotate -90° around Y to point +X.
sel_motor_x = BIN_CENTER_X - 300 - 25  # left of rail
parts.append(("sel_motor", sel_motor,
              Location((sel_motor_x, CARD_Y, SEL_RAIL_Z + 5), (0, -90, 0)),
              (0.18, 0.18, 0.20, 1.0, 0.3, 0.6)))  # dark motor

# 8. Recombine — origin is center, 610mm wide. Place behind bin bank.
parts.append(("recombine", recombine, Location((BIN_CENTER_X, REC_Y, DATUM_A)),
              (0.06, 0.72, 0.50, 1.0, 0.1, 0.45)))  # emerald

# 9. Recombine rail — behind bin bank
parts.append(("rec_rail", rec_rail, Location((BIN_CENTER_X, REC_Y, DATUM_A - 3)),
              (0.65, 0.67, 0.70, 1.0, 0.7, 0.25)))  # steel

# 10. Recombine X motor — left end of recombine rail
rec_motor_x = BIN_CENTER_X - 300 - 25
parts.append(("rec_x_motor", rec_x_motor,
              Location((rec_motor_x, REC_Y, DATUM_A + 8), (0, -90, 0)),
              (0.18, 0.18, 0.20, 1.0, 0.3, 0.6)))  # dark motor

# 11. Recombine Z motor — small, on recombine carriage, shaft pointing up
parts.append(("rec_z_motor", rec_z_motor,
              Location((BIN_CENTER_X + 60, REC_Y - 25, DATUM_A + 45), (180, 0, 0)),
              (0.18, 0.18, 0.20, 1.0, 0.3, 0.6)))

# 12. Feeder motor — below feeder, shaft up through hopper floor
parts.append(("feed_motor", feeder_motor,
              Location((50, CARD_Y, DATUM_A), (180, 0, 0)),
              (0.18, 0.18, 0.20, 1.0, 0.3, 0.6)))

# 13-14. GT2 belts for selector (top and bottom runs)
belt_z = SEL_RAIL_Z + 2
belt_left_x = BIN_CENTER_X - 295
belt_right_x = BIN_CENTER_X + 295
parts.append(("sel_belt_top",
              build_belt_segment((belt_left_x, CARD_Y, belt_z),
                                (belt_right_x, CARD_Y, belt_z)),
              Location((0, 0, 0)),
              (0.96, 0.65, 0.10, 1.0, 0.0, 0.5)))  # orange belt

parts.append(("sel_belt_bot",
              build_belt_segment((belt_left_x, CARD_Y, belt_z - 10),
                                (belt_right_x, CARD_Y, belt_z - 10)),
              Location((0, 0, 0)),
              (0.96, 0.65, 0.10, 1.0, 0.0, 0.5)))

# 15-16. GT2 belts for recombine
rec_belt_z = DATUM_A + 10
parts.append(("rec_belt_top",
              build_belt_segment((belt_left_x, REC_Y, rec_belt_z),
                                (belt_right_x, REC_Y, rec_belt_z)),
              Location((0, 0, 0)),
              (0.96, 0.65, 0.10, 1.0, 0.0, 0.5)))

parts.append(("rec_belt_bot",
              build_belt_segment((belt_left_x, REC_Y, rec_belt_z - 10),
                                (belt_right_x, REC_Y, rec_belt_z - 10)),
              Location((0, 0, 0)),
              (0.96, 0.65, 0.10, 1.0, 0.0, 0.5)))

# ---------------------------------------------------------------------------
# Export each part as individual temp GLB, then merge with colors
# ---------------------------------------------------------------------------
import tempfile, os

SITE_DIR = CAD_DIR.parent / "site"
TMP_DIR = Path(tempfile.mkdtemp(prefix="shuffledeck_"))

print(f"\nExporting {len(parts)} parts to temp GLBs...")

part_glbs = []
for name, shape, loc, color in parts:
    moved = shape.moved(loc)
    tmp_path = TMP_DIR / f"{name}.glb"
    export_gltf(moved, str(tmp_path), binary=True)
    part_glbs.append((name, tmp_path, color))
    bb = moved.bounding_box()
    print(f"  {name}: {bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.0f}mm at ({bb.min.X:.0f},{bb.min.Y:.0f},{bb.min.Z:.0f})")


# ---------------------------------------------------------------------------
# Merge GLBs into one file with per-part PBR materials
# ---------------------------------------------------------------------------

def read_glb(path):
    """Read a GLB file and return (json_dict, binary_chunk_bytes)."""
    with open(path, "rb") as f:
        magic = f.read(4)
        version = struct.unpack("<I", f.read(4))[0]
        total_len = struct.unpack("<I", f.read(4))[0]
        # JSON chunk
        json_len = struct.unpack("<I", f.read(4))[0]
        json_type = struct.unpack("<I", f.read(4))[0]  # 0x4E4F534A
        json_data = json.loads(f.read(json_len).decode("utf-8"))
        # Binary chunk (may not exist for empty meshes)
        bin_data = b""
        if f.tell() < total_len:
            bin_len = struct.unpack("<I", f.read(4))[0]
            bin_type = struct.unpack("<I", f.read(4))[0]  # 0x004E4942
            bin_data = f.read(bin_len)
    return json_data, bin_data


def write_glb(json_dict, bin_data, out_path):
    """Write a GLB file from json dict and binary buffer."""
    json_bytes = json.dumps(json_dict, separators=(",", ":")).encode("utf-8")
    # Pad JSON to 4-byte boundary
    json_pad = (4 - len(json_bytes) % 4) % 4
    json_bytes += b" " * json_pad
    # Pad binary to 4-byte boundary
    bin_pad = (4 - len(bin_data) % 4) % 4
    bin_data += b"\x00" * bin_pad

    total = 12 + 8 + len(json_bytes) + 8 + len(bin_data)
    with open(out_path, "wb") as f:
        f.write(b"glTF")
        f.write(struct.pack("<I", 2))
        f.write(struct.pack("<I", total))
        # JSON chunk
        f.write(struct.pack("<I", len(json_bytes)))
        f.write(struct.pack("<I", 0x4E4F534A))
        f.write(json_bytes)
        # Binary chunk
        f.write(struct.pack("<I", len(bin_data)))
        f.write(struct.pack("<I", 0x004E4942))
        f.write(bin_data)


print("\nMerging into single colored GLB...")

merged_json = {
    "asset": {"version": "2.0", "generator": "ShuffleDeck render_hero.py"},
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
    r, g, b, a, metallic, roughness = color

    src_json, src_bin = read_glb(glb_path)

    if not src_json.get("meshes"):
        print(f"  {name}: no meshes, skipping")
        continue

    # Offsets for merging
    acc_offset = len(merged_json["accessors"])
    bv_offset = len(merged_json["bufferViews"])
    mesh_offset = len(merged_json["meshes"])
    mat_idx = len(merged_json["materials"])
    bin_offset = len(merged_bin)

    # Add material
    merged_json["materials"].append({
        "name": name,
        "pbrMetallicRoughness": {
            "baseColorFactor": [r, g, b, a],
            "metallicFactor": metallic,
            "roughnessFactor": roughness,
        },
    })

    # Copy buffer views with offset
    for bv in src_json.get("bufferViews", []):
        new_bv = dict(bv)
        new_bv["buffer"] = 0
        new_bv["byteOffset"] = bv.get("byteOffset", 0) + bin_offset
        merged_json["bufferViews"].append(new_bv)

    # Copy accessors with offset
    for acc in src_json.get("accessors", []):
        new_acc = dict(acc)
        if "bufferView" in new_acc:
            new_acc["bufferView"] += bv_offset
        merged_json["accessors"].append(new_acc)

    # Copy meshes, rewriting accessor and material indices
    for mesh in src_json.get("meshes", []):
        new_mesh = {"name": name, "primitives": []}
        for prim in mesh["primitives"]:
            new_prim = {}
            if "attributes" in prim:
                new_prim["attributes"] = {}
                for attr, idx in prim["attributes"].items():
                    new_prim["attributes"][attr] = idx + acc_offset
            if "indices" in prim:
                new_prim["indices"] = prim["indices"] + acc_offset
            new_prim["material"] = mat_idx
            if "mode" in prim:
                new_prim["mode"] = prim["mode"]
            new_mesh["primitives"].append(new_prim)
        merged_json["meshes"].append(new_mesh)

    # Add nodes referencing the new meshes
    for i in range(len(src_json.get("meshes", []))):
        node_idx = len(merged_json["nodes"])
        merged_json["scenes"][0]["nodes"].append(node_idx)
        merged_json["nodes"].append({
            "name": name,
            "mesh": mesh_offset + i,
        })

    # Append binary data
    merged_bin.extend(src_bin)

# Update buffer length
merged_json["buffers"][0]["byteLength"] = len(merged_bin)

# Write merged GLB
out_path = SITE_DIR / "assembly.glb"
write_glb(merged_json, bytes(merged_bin), out_path)

# Clean up temp files
for _, p, _ in part_glbs:
    p.unlink(missing_ok=True)
TMP_DIR.rmdir()

print(f"\nExported: {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")
print(f"Parts: {len(parts)}")
print(f"Materials: {len(merged_json['materials'])}")
print(f"Meshes: {len(merged_json['meshes'])}")
print(f"Nodes: {len(merged_json['nodes'])}")
print("Done.")
