# Single-Deck Card Shuffler -- Wiring & Pinout Reference

Date: 2026-04-12
Controller: ESP32 DevKit V1 (WROOM-32, 38-pin)
Firmware: `firmware/shuffler/src/config.h`

This document contains everything needed to wire the shuffler from scratch
without reading the firmware source code.

---

## 1. Master Pinout Table

Every GPIO used on the ESP32, grouped by function.

| GPIO | Function | Signal Type | Direction | Pull | Wire Gauge | Notes |
|------|----------|-------------|-----------|------|------------|-------|
| 0 | Stop / Clear-Jam button | Digital | Input | Internal pull-up | -- | BOOT button on DevKit. Active-low. |
| 2 | Recombine Z enable (EN) | Digital | Output | -- | 22 AWG | Active-low: LOW = enabled. Directly drives TMC2209 EN pin. |
| 4 | Recombine Z direction (DIR) | Digital | Output | -- | 22 AWG | |
| 5 | OLED I2C clock (SCL) | I2C | Bidirectional | 4.7k external pull-up to 3.3V | 26 AWG | Directly drives SSD1306 SCL. |
| 12 | TMC2209 UART TX | UART (Serial2 TX) | Output | -- | 22 AWG | Shared bus to all 4 TMC2209 drivers. |
| 13 | TMC2209 UART RX | UART (Serial2 RX) | Input | -- | 22 AWG | Shared bus from all 4 TMC2209 drivers. |
| 14 | Selector X enable (EN) | Digital | Output | -- | 22 AWG | Active-low. |
| 15 | Shuffle button | Digital | Input | Internal pull-up | -- | Active-low. Panel-mount momentary switch. |
| 16 | Recombine Z step (STEP) | Digital | Output | -- | 22 AWG | Pulse output. |
| 17 | Recombine X enable (EN) | Digital | Output | -- | 22 AWG | Active-low. |
| 18 | Recombine X direction (DIR) | Digital | Output | -- | 22 AWG | |
| 19 | Recombine X step (STEP) | Digital | Output | -- | 22 AWG | Pulse output. |
| 21 | OLED I2C data (SDA) | I2C | Bidirectional | 4.7k external pull-up to 3.3V | 26 AWG | Directly drives SSD1306 SDA. |
| 22 | Output tray sensor | Digital | Input (interrupt) | External 10k pull-up to 3.3V | 26 AWG | TCRT5000 digital out. Active-low. |
| 23 | Recombine pickup sensor | Digital | Input (interrupt) | External 10k pull-up to 3.3V | 26 AWG | TCRT5000 digital out. Active-low. |
| 25 | Feeder enable (EN) | Digital | Output | -- | 22 AWG | Active-low. |
| 26 | Feeder step (STEP) | Digital | Output | -- | 22 AWG | Pulse output, up to 4800 Hz. |
| 27 | Feeder direction (DIR) | Digital | Output | -- | 22 AWG | |
| 32 | Selector X direction (DIR) | Digital | Output | -- | 22 AWG | |
| 33 | Selector X step (STEP) | Digital | Output | -- | 22 AWG | Pulse output. |
| 34 | Feed exit sensor | Digital | Input (interrupt) | External 10k pull-up to 3.3V | 26 AWG | GPIO 34-39 are input-only, no internal pull-up. |
| 35 | Post-singulation sensor | Digital | Input (interrupt) | External 10k pull-up to 3.3V | 26 AWG | Input-only pin, no internal pull-up. |
| 36 (SVP) | Selector throat sensor | Digital | Input (interrupt) | External 10k pull-up to 3.3V | 26 AWG | Input-only pin, no internal pull-up. |
| 39 (SVN) | Bin entry sensor | Digital | Input (interrupt) | External 10k pull-up to 3.3V | 26 AWG | Input-only pin, no internal pull-up. |

**Important:** GPIO 34, 35, 36, 39 are input-only on the ESP32 and have no internal pull-up/pull-down. You must provide external 10k pull-up resistors to 3.3V for these four sensor pins.

---

## 2. TMC2209 UART Bus

All four TMC2209 stepper drivers share a single UART bus using different addresses.

| Parameter | Value |
|-----------|-------|
| ESP32 serial port | Serial2 |
| TX pin | GPIO 12 |
| RX pin | GPIO 13 |
| Baud rate | 115200 |
| Sense resistor (R_sense) | 0.11 ohm |

### Driver Addressing

TMC2209 addresses are set via the MS1 and MS2 pins on each driver board:

| UART Addr | MS1 | MS2 | Motor | Current (mA RMS) |
|-----------|-----|-----|-------|-------------------|
| 0 | LOW | LOW | Feeder (singulation roller) | 600 |
| 1 | HIGH | LOW | Selector X (positions over 8 bins) | 800 |
| 2 | LOW | HIGH | Recombine X (traverses bins for pickup) | 800 |
| 3 | HIGH | HIGH | Recombine Z (elevator lift/lower) | 600 |

### UART Wiring Notes

- The TMC2209 UART is a single-wire half-duplex protocol. Some breakout boards
  (BIGTREETECH, Fysetc) have a 1k resistor between the TX and RX UART pads.
  If your board does not, place a **1k ohm resistor** in series on the TX line
  from the ESP32 to the shared bus.
- Daisy-chain topology: ESP32 TX (GPIO 12) connects to the UART/PDN pin on
  all four TMC2209 boards in parallel. RX (GPIO 13) connects to the same bus.
- Keep UART wires short (under 150 mm) and away from motor phase wires.
- Verify MS1/MS2 configuration matches the table above before powering on.
  Wrong addresses will cause UART communication failures during `motors_init()`.

---

## 3. Motor Wiring Table

Each motor has three control signals (STEP, DIR, EN) plus a 4-wire stepper coil connection.

### Control Signals

| Motor | STEP Pin | DIR Pin | EN Pin | TMC2209 Addr | Speed (steps/s) |
|-------|----------|---------|--------|--------------|------------------|
| Feeder | GPIO 26 | GPIO 27 | GPIO 25 | 0 | 4800 |
| Selector X | GPIO 33 | GPIO 32 | GPIO 14 | 1 | 4000 |
| Recombine X | GPIO 19 | GPIO 18 | GPIO 17 | 2 | 4000 |
| Recombine Z | GPIO 16 | GPIO 4 | GPIO 2 | 3 | 2000 |

**Enable logic:** All EN pins are active-low. LOW = motor energized. HIGH = motor free (no holding torque). The TMC2209 EN pin draws negligible current; direct ESP32 GPIO drive is fine.

### Motor Coil Connections (JST-XH 4-pin on driver side)

Standard NEMA 17 bipolar wiring. Verify coil pairs with a multimeter (each coil pair reads 2-10 ohms; no continuity between pairs).

| Driver Pin | Function | Recommended Wire Color | Motor Wire (typical) |
|------------|----------|----------------------|---------------------|
| A1 (OA1) | Coil A+ | Red | Red or Black |
| A2 (OA2) | Coil A- | Green | Green or Red |
| B1 (OB1) | Coil B+ | Blue | Blue or Yellow |
| B2 (OB2) | Coil B- | Yellow | Yellow or White |

**Warning:** Wire colors vary between motor manufacturers. Always identify coil pairs with a multimeter before connecting. Swapping wires within a pair (A1/A2 or B1/B2) reverses direction. Swapping wires between pairs (A and B) causes erratic behavior.

### Motor Specifications (from BOM)

| Motor | BOM # | Size | Holding Torque | Rated Current |
|-------|-------|------|---------------|---------------|
| Feeder | E3 | 42x42x25 mm (pancake) | >= 13 N-cm | 600 mA |
| Selector X | E4 | 42x42x40 mm (standard) | >= 40 N-cm | 800 mA |
| Recombine X | E5 | 42x42x40 mm (standard) | >= 40 N-cm | 800 mA |
| Recombine Z | E6 | 42x42x34 mm (short) | >= 26 N-cm | 600 mA |

---

## 4. Sensor Wiring Table

All six sensors are TCRT5000 IR reflective sensor modules. Signal is active-low: **LOW = beam broken (card detected)**, HIGH = clear.

| Sensor | Function | GPIO | Interrupt | Pull-Up | ISR Debounce |
|--------|----------|------|-----------|---------|--------------|
| Feed exit | Card leaves feeder roller | 34 | Yes | External 10k to 3.3V (required) | 2000 us |
| Post-singulation | Confirms single card | 35 | Yes | External 10k to 3.3V (required) | 2000 us |
| Selector throat | Card enters selector | 36 | Yes | External 10k to 3.3V (required) | 2000 us |
| Bin entry | Card enters bin (shared beam) | 39 | Yes | External 10k to 3.3V (required) | 2000 us |
| Recombine pickup | Pickup head has card | 23 | Yes | External 10k to 3.3V (recommended) | 2000 us |
| Output tray | Card count checkpoint | 22 | Yes | External 10k to 3.3V (recommended) | 2000 us |

### Per-Sensor Wiring (3 wires each)

| TCRT5000 Module Pin | Connection | Notes |
|---------------------|------------|-------|
| VCC | 3.3V rail | Do NOT use 5V -- the digital output of most TCRT5000 modules will exceed ESP32 3.3V input tolerance if powered from 5V. If your module requires 5V for the IR LED, add a voltage divider on the digital output pin. |
| GND | Common ground | Star ground to ESP32 GND. |
| DO (digital out) | ESP32 GPIO (see table) | Active-low. 10k pull-up to 3.3V on GPIOs 34/35/36/39 (no internal pull-up). GPIOs 22/23 can use internal pull-up but external is recommended for noise immunity. |

### Pull-Up Resistor Placement

- **GPIOs 34, 35, 36, 39:** External 10k pull-up to 3.3V is **mandatory** (these pins have no internal pull-up).
- **GPIOs 22, 23:** External 10k pull-up to 3.3V is **recommended** for consistency and noise rejection. Internal pull-up is available as a fallback.
- Place pull-up resistors on the sensor breakout perfboard, as close to the ESP32 as practical.

---

## 5. I2C Bus

| Parameter | Value |
|-----------|-------|
| SDA | GPIO 21 |
| SCL | GPIO 5 |
| Bus speed | 400 kHz (Fast mode) |
| Pull-up resistors | 4.7k ohm to 3.3V on both SDA and SCL |

### Devices on Bus

| Device | Address | BOM # | Description |
|--------|---------|-------|-------------|
| SSD1306 OLED | 0x3C | E7 | 0.96" 128x64 display for status and diagnostics |

### I2C Wiring Notes

- Many SSD1306 modules include on-board pull-ups (typically 10k). If your module
  has them, the additional 4.7k external pull-ups are still fine in parallel
  (effective ~3.2k, well within I2C spec).
- Keep I2C wires under 200 mm. Longer runs at 400 kHz may need lower pull-up
  values (2.2k) or reduced bus speed.
- Use twisted pair or keep SDA and SCL wires routed together.

---

## 6. Power Distribution

```
                        AC MAINS
                           |
                    [IEC C14 Inlet + Fused Switch] (BOM E11)
                    |  10A fuse, integrated switch
                           |
                    [12V 10A PSU] (BOM E9, Mean Well LRS-150-12)
                    |  120W capacity, ~60W steady-state draw
                           |
              +============ 12V BUS ============+
              |            |           |         |
          [TMC2209 #0] [TMC2209 #1] [TMC2209 #2] [TMC2209 #3]
          Feeder       Selector X   Recombine X  Recombine Z
          VM pin       VM pin       VM pin       VM pin
          600 mA       800 mA       800 mA       600 mA
              |
              |     +--- 12V IN
              |     |
              [5V 3A Buck Converter] (BOM E10, MP1584 or LM2596)
              |     |
              |     +--- 5V OUT
              |           |
              |     +-----+-------------------+
              |     |                         |
              [ESP32 VIN]              [OLED VCC (if 5V)]
              |  Peak ~500 mA         |  ~20 mA
              |                       |
              +--- 3.3V Rail (ESP32 internal regulator)
                    |           |           |
              [Sensor VCC x6]  [I2C Pull-ups]  [Button Pull-ups]
              ~10 mA each      to 3.3V         (internal)
              ~60 mA total
```

### Power Budget

| Load | Voltage | Current (max) | Notes |
|------|---------|---------------|-------|
| 4x TMC2209 motor drivers (VM) | 12V | 3.2A total | 800 mA per driver worst case |
| ESP32 DevKit | 5V via VIN | 500 mA peak | Wi-Fi transmit spikes |
| SSD1306 OLED | 3.3V or 5V | 20 mA | Check module; most accept either |
| 6x TCRT5000 sensors | 3.3V | 60 mA total | ~10 mA per module (IR LED + comparator) |
| **12V total** | | **~5A peak** | PSU provides 10A -- ample headroom |
| **5V total** | | **~600 mA peak** | Buck provides 3A -- ample headroom |

### Protection Recommendations

- **Input fuse:** 10A fast-blow in the IEC inlet (BOM E11 includes fuse holder).
- **12V bus:** Add a **5A automotive blade fuse** inline between the PSU and the
  TMC2209 VM distribution. Protects against motor driver shorts.
- **5V bus:** The buck converter module typically has built-in overcurrent
  protection. No additional fuse needed.
- **Reverse polarity:** Add a **Schottky diode** (1N5822 or similar, 3A rated)
  on the 12V input to the buck converter if there is any risk of reversed wiring.
  Better: use keyed connectors.
- **TMC2209 VM capacitor:** Place a **100 uF 25V electrolytic capacitor** across
  each TMC2209 VM/GND pair, close to the driver board. Most breakout boards
  include this; verify yours does.

---

## 7. Connector Reference

Standardize connectors for modular assembly and service.

| Connection | Connector Type | Pin Count | Notes |
|------------|---------------|-----------|-------|
| Motor coils (to TMC2209) | JST-XH 4-pin | 4 | A1, A2, B1, B2. Keyed to prevent reversal. |
| Motor control (STEP/DIR/EN) | JST-XH 3-pin | 3 | One per motor. ESP32 side: solder to perfboard header. |
| TMC2209 UART bus | JST-XH 2-pin | 2 | TX/RX daisy chain between driver boards. |
| Sensor (TCRT5000) | JST-XH 3-pin or Dupont 3-pin | 3 | VCC, GND, signal. Dupont acceptable for prototyping. |
| I2C OLED | JST-XH 4-pin or Dupont 4-pin | 4 | VCC, GND, SDA, SCL. |
| 12V PSU to distribution | XT60 or 5.5x2.1 mm barrel jack | 2 | XT60 for reliability, barrel jack for convenience. Solder direct for permanent install. |
| 12V to buck converter | JST-XH 2-pin or solder direct | 2 | Short run, solder preferred. |
| 5V buck to ESP32 | Dupont 2-pin or solder to VIN/GND | 2 | |
| Buttons (Shuffle, Stop) | JST-XH 2-pin | 2 | Signal + GND. Internal pull-up, so no VCC needed. |
| IEC mains inlet | C14 panel mount | 3 (L, N, PE) | BOM E11. Fused and switched. |

### Connector Crimping Notes

- Use proper JST-XH crimp terminals and a ratcheting crimp tool (Engineer PA-09
  or similar). Do not solder wires into JST housings -- the solder wicks up and
  causes brittle joints.
- Label all connectors with a label maker or heat-shrink labels. At minimum,
  label which motor/sensor each cable connects to.

---

## 8. Cable Routing Notes

### Chassis Cable Channels

The 3D-printed chassis base frame (BOM P15) and cable clips (BOM P21) provide
routing paths. Organize cables into three groups:

| Group | Cables | Routing Path |
|-------|--------|-------------|
| **Power (12V)** | PSU to TMC2209 VM bus, PSU to buck converter | Bottom of chassis, center channel. Use 18-20 AWG for 12V main run, 22 AWG for branches. |
| **Motor (STEP/DIR/EN + coil)** | 4x motor control bundles + 4x coil cables | Side channels, one bundle per motor. Keep left side for feeder + selector, right side for recombine X + Z. |
| **Signal (sensors + I2C + UART)** | 6x sensor cables, OLED I2C, TMC2209 UART | Top channel or opposite side from motor coil cables. |

### EMI / Noise Separation

- **Keep sensor signal wires at least 20 mm away from stepper motor coil cables.**
  Motor coil cables carry high-frequency chopped current (TMC2209 chopper at
  ~30 kHz) that can couple noise into sensor lines and cause false triggers.
- If sensor and motor cables must cross, cross them at **90 degrees** to minimize
  coupling.
- The TMC2209 UART wires are relatively robust but should still be routed away
  from motor coils. Keep UART cable length under 150 mm.
- Use **spiral wrap** (BOM X3) to bundle each motor's 7 wires (4 coil + 3 control)
  into a single harness.

### Bend Radius

- **Stepper motor cables (22 AWG stranded):** Minimum bend radius 10 mm (roughly
  5x wire diameter). Avoid sharp kinks at motor mount entry points.
- **Sensor cables (26 AWG stranded):** Minimum bend radius 6 mm.
- **GT2 belt:** Not a cable, but keep belt runs straight. Any twist or lateral
  bend degrades timing accuracy.

### Service Access

- Route all connectors to the **electronics bay** (BOM P14) so that any cable
  can be disconnected without disassembling mechanical components.
- Leave 30-50 mm of slack at each motor and sensor connector to allow module
  removal for service.
- The electronics bay should be accessible by removing a single enclosure panel
  (BOM P16) or from the bottom of the chassis.

---

## Quick Reference: Pin-to-Wire Color Scheme (Recommended)

A consistent color scheme makes debugging much faster.

| Function | Wire Color | Gauge |
|----------|-----------|-------|
| 12V power | Red | 20-22 AWG |
| 5V power | Orange | 22 AWG |
| 3.3V power | Yellow | 22-26 AWG |
| Ground | Black | Match power gauge |
| Motor STEP | White | 22 AWG |
| Motor DIR | Blue | 22 AWG |
| Motor EN | Green | 22 AWG |
| Motor coil A (A1, A2) | Red + Green (twisted pair) | 22 AWG |
| Motor coil B (B1, B2) | Blue + Yellow (twisted pair) | 22 AWG |
| Sensor signal | White | 26 AWG |
| I2C SDA | Purple | 26 AWG |
| I2C SCL | Gray | 26 AWG |
| UART TX | Orange | 22 AWG |
| UART RX | Brown | 22 AWG |
| Button signal | White or Green | 26 AWG |
