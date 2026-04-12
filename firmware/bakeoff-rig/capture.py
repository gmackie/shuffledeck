#!/usr/bin/env python3
"""
Host-side capture script for the feeder bakeoff rig.
Reads serial CSV from ESP32, writes to file, prints running stats.

Usage:
    python capture.py [--port /dev/ttyUSB0] [--baud 115200] [-o output.csv]

Defaults: first available ESP32 serial port, 115200 baud, timestamped output file.
"""

import argparse
import csv
import datetime
import sys
import time

import serial
import serial.tools.list_ports


def find_esp32_port():
    """Auto-detect an ESP32 serial port."""
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").lower()
        vid = p.vid or 0
        # CP210x (0x10C4) or CH340 (0x1A86) are common ESP32 USB-serial chips
        if vid in (0x10C4, 0x1A86) or "cp210" in desc or "ch340" in desc:
            return p.device
    # Fallback: first available port
    ports = serial.tools.list_ports.comports()
    if ports:
        return ports[0].device
    return None


def main():
    parser = argparse.ArgumentParser(description="Feeder bakeoff rig capture")
    parser.add_argument("--port", "-p", default=None, help="Serial port")
    parser.add_argument("--baud", "-b", type=int, default=115200)
    parser.add_argument("-o", "--output", default=None, help="Output CSV path")
    args = parser.parse_args()

    port = args.port or find_esp32_port()
    if not port:
        print("ERROR: no serial port found. Specify with --port.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        outpath = args.output
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        outpath = f"bakeoff_{ts}.csv"

    print(f"Port: {port}  Baud: {args.baud}  Output: {outpath}")

    # Stats
    total = 0
    singles = 0
    doubles = 0
    misses = 0
    skews = 0
    jams = 0

    try:
        ser = serial.Serial(port, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Let ESP32 reset after serial open
    time.sleep(2)
    ser.reset_input_buffer()

    header_written = False

    try:
        with open(outpath, "w", newline="") as f:
            writer = csv.writer(f)

            while True:
                raw = ser.readline()
                if not raw:
                    continue

                try:
                    line = raw.decode("utf-8", errors="replace").strip()
                except Exception:
                    continue

                if not line:
                    continue

                # Comments / metadata from firmware
                if line.startswith("#"):
                    print(line)
                    continue

                # CSV header row
                if line.startswith("event_id,"):
                    if not header_written:
                        writer.writerow(line.split(","))
                        f.flush()
                        header_written = True
                    print(f"\n{'='*60}")
                    print(line)
                    print(f"{'='*60}")
                    continue

                # Data row
                parts = line.split(",")
                if len(parts) < 5:
                    print(f"? {line}")
                    continue

                # Write to file
                writer.writerow(parts)
                f.flush()

                classification = parts[4].strip()
                total += 1
                if classification == "single":
                    singles += 1
                elif classification == "double":
                    doubles += 1
                elif classification == "miss":
                    misses += 1
                elif classification == "skew":
                    skews += 1
                elif classification == "jam":
                    jams += 1

                # Print line + running stats
                transit = parts[5].strip() if len(parts) > 5 else ""
                print(
                    f"[{total:4d}] {classification:<8s} transit={transit:>4s}ms  |  "
                    f"S={singles} D={doubles} M={misses} K={skews} J={jams}"
                )

    except KeyboardInterrupt:
        print(f"\n\nCapture stopped. {total} events written to {outpath}")
        print(f"Final: singles={singles} doubles={doubles} misses={misses} "
              f"skews={skews} jams={jams}")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
