# Motor Setup — Lumen 3D Printer NEMA17 Salvage

Date: 2026-04-12

## Motor Identification

Lumen 3D printers use standard NEMA17 steppers, typically:

- **Frame:** 42×42×40 mm (standard body)
- **Step angle:** 1.8° (200 steps/rev)
- **Current rating:** ~1.5A (varies by Lumen model year)
- **Shaft:** 5 mm D-shaft, 24 mm length
- **Connector:** 4-pin JST-XH or bare leads (varies)

You have 4 motors. All 4 are the same model, which simplifies things.

### Axis Assignment

The BOM originally spec'd different motor sizes per axis. Your Lumen motors are all 40mm standard bodies, which is fine for every axis. The TMC2209 current limiting handles the rest.

| Axis | BOM Spec | Your Motor | Current Setting | Notes |
|---|---|---|---|---|
| Feeder (addr 0) | 25mm pancake, 600mA | Lumen 40mm, ~1.5A | **600 mA** | Overpowered but current-limited. Extra mass doesn't matter, feeder doesn't move fast. |
| Selector X (addr 1) | 40mm standard, 800mA | Lumen 40mm, ~1.5A | **800 mA** | Perfect match. |
| Recombine X (addr 2) | 40mm standard, 800mA | Lumen 40mm, ~1.5A | **800 mA** | Perfect match. |
| Recombine Z (addr 3) | 34mm short, 600mA | Lumen 40mm, ~1.5A | **600 mA** | Slightly larger than needed. More holding torque is actually good for Z. |

**No firmware changes needed.** The current limits in `config.h` are already set correctly. The TMC2209s will limit current regardless of the motor's rated current.

## Wiring the Motors

### Step 1: Identify Coils

Each NEMA17 has 4 wires = 2 coils. You need to identify which pairs are coil A and coil B.

**Method:** Touch two wires together and try to spin the shaft by hand. If the shaft resists (feels "sticky"), those two wires are one coil.

Typical Lumen motor wire colors:

| Wire | Coil | TMC2209 Pin |
|---|---|---|
| Black | A+ (1A) | OA1 |
| Green | A- (1B) | OA2 |
| Red | B+ (2A) | OB1 |
| Blue | B- (2B) | OB2 |

**If your colors differ:** use the touch-and-spin method. It doesn't matter which coil is A vs B... the motor just spins the other direction, and you can fix that in firmware by swapping `dir` polarity.

### Step 2: TMC2209 Address Configuration

The 4 TMC2209 boards share one UART bus. Each needs a unique address set via MS1/MS2 pins.

| Axis | UART Addr | MS1 | MS2 |
|---|---|---|---|
| Feeder | 0 | LOW (GND) | LOW (GND) |
| Selector X | 1 | HIGH (VCC) | LOW (GND) |
| Recombine X | 2 | LOW (GND) | HIGH (VCC) |
| Recombine Z | 3 | HIGH (VCC) | HIGH (VCC) |

**BIGTREETECH TMC2209 boards:** MS1 and MS2 are solder pads on the bottom. Default is both LOW (addr 0). Bridge the pads with solder to set HIGH.

**Fysetc TMC2209 boards:** Same concept, check the silkscreen for MS1/MS2 pad locations.

### Step 3: Wiring Diagram

For each motor axis:

```
ESP32                TMC2209              NEMA17
──────               ───────              ──────
STEP pin ──────────► STEP
DIR pin  ──────────► DIR
EN pin   ──────────► EN
                     OA1  ────────────► Black (A+)
                     OA2  ────────────► Green (A-)
                     OB1  ────────────► Red (B+)
                     OB2  ────────────► Blue (B-)
                     VM   ◄──── 12V PSU
                     GND  ◄──── 12V PSU GND
                     VIO  ◄──── 3.3V (from ESP32 3V3)
```

UART bus (all 4 drivers share):
```
ESP32 GPIO 13 (RX) ──────► TX (all 4 TMC2209 TX pins, direct connect)
ESP32 GPIO 12 (TX) ──────► RX (all 4 TMC2209 RX pins, via 1kΩ resistor)
```

**The 1kΩ resistor on TX is required.** TMC2209 UART is single-wire internally; the resistor prevents bus contention. Some breakout boards have this built in... check the schematic first.

### Step 4: Quick Smoke Test

Before installing in the machine, bench-test each motor individually:

1. Wire one motor + one TMC2209 to the ESP32
2. Set the TMC2209 to address 0 (MS1=LOW, MS2=LOW)
3. Flash the shuffler firmware
4. Open serial monitor at 115200 baud
5. Type `jog feed 200` — the motor should spin ~1 revolution and back
6. If it doesn't move: check UART connection, verify TMC version reads 0x21
7. Repeat for each motor, changing the UART address each time

### Lumen Motor Notes

- **Detent torque:** Lumen motors have noticeable detent torque (you can feel the steps when turning by hand with wires disconnected). This is normal for 1.8° motors.
- **Back-EMF:** If these motors were running at higher currents in the Lumen printer, the TMC2209 will run them much quieter at 600-800mA with StealthChop enabled.
- **Connector swap:** If the Lumen motors have JST-PH connectors (2.0mm pitch), you'll need to re-crimp to JST-XH (2.54mm pitch) or solder direct. Or just cut and solder.
- **Shaft length:** 24mm D-shaft should be fine for GT2 pulleys (need ~12mm engagement) and the feeder roller coupling.
