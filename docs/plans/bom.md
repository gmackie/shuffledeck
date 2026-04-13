# Single-Deck Card Shuffler V1 -- Bill of Materials

Date: 2026-04-12
Reference: `docs/plans/2026-04-09-single-deck-shuffler-design.md`
Budget ceiling: **$500** (hardware only, excludes print plastic and labor)

---

## 1. Electronics

| # | Part | Qty | Specification | Unit Cost | Source | Notes |
|---|------|-----|--------------|-----------|--------|-------|
| E1 | ESP32 DevKit V1 (WROOM-32) | 1 | 38-pin, dual-core 240 MHz, Wi-Fi/BLE | $7 | Amazon / AliExpress | Main controller. Plenty of GPIO for 4 motors + 6 sensors + OLED + 2 buttons. |
| E2 | TMC2209 stepper driver (BIGTREETECH or Fysetc) | 4 | UART mode, up to 2A RMS, StealthChop2 | $5 | Amazon / AliExpress | One per axis: feeder (addr 0), selector X (addr 1), recombine X (addr 2), recombine Z (addr 3). Shared UART bus on GPIO 12/13. R_sense = 0.11 ohm. |
| E3 | NEMA 17 stepper -- pancake 25mm (feeder) | 1 | 42x42x25 mm, 0.9 deg/step or 1.8 deg, >= 13 N-cm holding torque, 600 mA rated | $9 | StepperOnline 17HS08-1004S / AliExpress | Low torque OK. Needs smooth microstepping at 120 mm/s feed speed (4800 steps/s). Pancake saves space in feeder module. |
| E4 | NEMA 17 stepper -- standard 40mm (selector X) | 1 | 42x42x40 mm, 1.8 deg, >= 40 N-cm, 800 mA rated | $12 | StepperOnline 17HS16-0404S / Amazon | Moderate torque for fast positioning across 500 mm travel. Must accelerate carriage + card guide mass quickly. |
| E5 | NEMA 17 stepper -- standard 40mm (recombine X) | 1 | 42x42x40 mm, 1.8 deg, >= 40 N-cm, 800 mA rated | $12 | StepperOnline 17HS16-0404S / Amazon | Same as selector X. Traverses bin bank for pickup. |
| E6 | NEMA 17 stepper -- short 34mm (recombine Z) | 1 | 42x42x34 mm, 1.8 deg, >= 26 N-cm, 600 mA rated | $10 | StepperOnline 17HS13-0404S / AliExpress | Lower speed (2000 sps), needs holding torque for stack weight. 800 steps travel. Leadscrew or belt-driven Z. |
| E7 | SSD1306 OLED display | 1 | 0.96", 128x64, I2C (addr 0x3C) | $4 | Amazon / AliExpress | Diagnostics display. SDA = GPIO 21, SCL = GPIO 5. |
| E8 | IR reflective sensor -- TCRT5000 module | 6 | 3.3-5 V, analog/digital out, ~2-15 mm range | $1 | AliExpress (pack of 10 for ~$4) | Feed exit, post-singulation, selector throat, bin entry, recombine pickup, output checkpoint. Active-low, GPIO interrupt-capable pins (34/35/36/39/23/22). |
| E9 | 12V 10A switching power supply | 1 | 12 VDC, 120 W, IEC C14 inlet, enclosed | $14 | Amazon (Mean Well LRS-150-12 or clone) | 4 motors at 800 mA peak = 3.2A motor draw. TMC2209 + logic overhead ~2A. Total ~60W steady, 120W provides headroom for acceleration spikes. |
| E10 | 5V 3A buck converter (MP1584 or LM2596 module) | 1 | 12V in, 5V/3A out, adjustable or fixed | $3 | Amazon / AliExpress | Powers ESP32, OLED, sensors. ESP32 peak draw ~500 mA, sensors ~60 mA total, OLED ~20 mA. 3A provides margin. |
| E11 | IEC C14 panel-mount inlet + fused switch | 1 | 10A, with integrated switch and fuse holder | $3 | Amazon / AliExpress | Clean power entry to enclosure. |
| E12 | JST-XH connector kit (2/3/4 pin) | 1 kit | Assorted JST-XH male + female + crimps | $8 | Amazon | Motor, sensor, and power connectors. Allows modular wiring for service. |
| E13 | Dupont jumper wire kit | 1 kit | M-M, M-F, F-F, 10/20 cm assorted | $5 | Amazon | Prototyping and internal wiring. |
| E14 | Prototype PCB / perfboard | 2 | 5x7 cm, through-hole | $1 | AliExpress | TMC2209 carrier board, sensor breakout. |
| E15 | 22 AWG stranded wire (assorted) | 1 spool | 6 colors, ~25 ft each | $8 | Amazon | Motor and power wiring runs. |

**Electronics subtotal: ~$112**

---

## 2. Mechanical -- Motion

| # | Part | Qty | Specification | Unit Cost | Source | Notes |
|---|------|-----|--------------|-----------|--------|-------|
| M1 | MGN12H linear rail + carriage (selector X) | 1 | 600 mm rail, 1x MGN12H carriage block | $18 | AliExpress / Amazon | Calculated rail length ~571 mm (500.5 mm travel + 50 mm carriage + 20 mm end clearance). 600 mm is nearest standard length. |
| M2 | MGN12H linear rail + carriage (recombine X) | 1 | 600 mm rail, 1x MGN12H carriage block | $18 | AliExpress / Amazon | Rail mount plate width is 610 mm; 600 mm rail fits with motor bracket overhang. Could also use 650 mm. |
| M3 | GT2 timing belt (6mm width) | 1 | Open loop, 2 m length | $4 | Amazon / AliExpress | Cut to fit selector X (~1.4 m loop) and recombine X (~1.4 m loop). Buy 2x 2m if making separate loops. |
| M4 | GT2 timing belt (6mm width) -- spare | 1 | Open loop, 2 m length | $4 | Amazon / AliExpress | Second belt for recombine X axis. |
| M5 | GT2 20-tooth pulley (5mm bore) | 4 | 20T, 6mm belt width, 5mm bore, set screw | $2 | Amazon / AliExpress (pack of 5 ~$7) | 2 drive pulleys (on motor shafts), 2 idler positions. |
| M6 | GT2 20-tooth idler pulley (smooth, 5mm bore) | 2 | Smooth or toothed, 5mm bore, with bearing | $2 | Amazon / AliExpress | Idler end of each belt loop. Toothed preferred to prevent belt skip. |
| M7 | 608ZZ bearing | 4 | 8x22x7 mm, shielded | $1 | Amazon / AliExpress (pack of 10 ~$6) | Feeder roller shaft, idler pulleys, any free-spinning shafts. |
| M8 | 5mm D-shaft steel rod | 1 | 5mm diameter, ~100 mm length | $3 | Amazon / McMaster | Feeder roller shaft. Cut to length. |
| M9 | Compression springs (feeder pressure) | 2 | ~10 mm OD, ~20 mm free length, light rate (~0.3 N/mm) | $1 | Amazon (spring assortment) / McMaster | Retard pad pressure and hopper backstop spring loading. Exact rate tuned during bakeoff. |
| M10 | Extension spring (belt tensioner) | 2 | ~5 mm OD, ~15 mm free length | $1 | Amazon (spring assortment) | Belt tensioning for GT2 loops. |
| M11 | Silicone O-rings (feeder roller) | 10 | ~18-22 mm ID, 2-3 mm cross-section, 50A durometer | $3 | Amazon / McMaster 9452K34 | High-friction contact surface for singulation roller. Buy extras -- these are wear parts. Size depends on roller OD in final feeder design. |
| M12 | Retard pad material (cork + rubber composite) | 1 sheet | ~2 mm thick, 100x100 mm minimum | $5 | Amazon / McMaster | Cut to fit retard pad slot. Separator pad material like Canon/HP pickup pads. Alternative: 3M Bumpon material or printer pickup roller rubber. |
| M13 | Shoulder bolts (M3 thread, 5mm shoulder) | 4 | M3x8 thread, 5mm shoulder dia, 10-15 mm shoulder length | $2 | McMaster 91259A118 / Amazon | Feeder roller pivot, spring anchor points. Allows free rotation while constraining position. |
| M14 | Linear rod 8mm (recombine Z guide) | 2 | 8mm OD, ~80 mm length, hardened | $3 | Amazon / AliExpress | Z-axis vertical guide for recombine elevator. Short travel (800 steps ~20 mm). |
| M15 | LM8UU linear bearing | 2 | 8x15x24 mm | $2 | Amazon / AliExpress | Recombine Z carriage rides on 8mm rods. |

**Mechanical subtotal: ~$73**

---

## 3. Fasteners

| # | Part | Qty | Specification | Unit Cost | Source | Notes |
|---|------|-----|--------------|-----------|--------|-------|
| F1 | M3x6 socket head cap screw | 30 | DIN 912, stainless or black oxide | $4 | Amazon (assortment) / McMaster | OLED mount, sensor mounts, belt clamp, general assembly. |
| F2 | M3x8 socket head cap screw | 40 | DIN 912 | $5 | Amazon / McMaster | Primary assembly screw into heat-set inserts (4 mm insert depth + clearance). |
| F3 | M3x10 socket head cap screw | 20 | DIN 912 | $3 | Amazon / McMaster | Deeper assemblies, motor mounts through brackets. |
| F4 | M3x16 socket head cap screw | 16 | DIN 912 | $3 | Amazon / McMaster | NEMA17 mounting (4 per motor x 4 motors). Standard NEMA17 mounting depth. |
| F5 | M3x20 socket head cap screw | 8 | DIN 912 | $2 | Amazon / McMaster | Long reach through thicker printed parts or stacked assemblies. |
| F6 | M4x10 socket head cap screw | 8 | DIN 912 | $2 | McMaster / Amazon | MGN12H rail mounting to chassis (M3 holes on carriage, but M4 may be used for rail-to-frame). |
| F7 | M3 brass heat-set insert (short) | 50 | M3x4x4 mm (OD 4.0, length 4.0), knurled | $6 | Amazon (CNC Kitchen style) / AliExpress | Counted from CAD: bin bank 4, recombine rail plate 4, output tray 4, selector carriage + motor mounts ~8, feeder module ~8, electronics bay ~6, chassis frame ~16. Total ~50, buy extra. |
| F8 | M3 hex nut | 20 | DIN 934, stainless | $2 | Amazon / McMaster | Belt clamp bolts, adjustable assemblies where inserts don't apply. |
| F9 | M3 flat washer | 30 | DIN 125, stainless | $2 | Amazon / McMaster | Under screw heads on clearance holes, spring retention. |
| F10 | M3 lock washer or Nylock nut | 10 | Split lock washer or M3 Nylock | $1 | Amazon / McMaster | Vibration-prone joints (motor mounts). |
| F11 | M3 brass heat-set insert (short) -- spare bag | 50 | Same as F7 | $6 | Amazon / AliExpress | Reprints and mistakes. 100 total is a comfortable stock for iteration. |

**Fasteners subtotal: ~$36**

Recommended: buy an M3 socket cap screw assortment kit (M3 x 4/6/8/10/12/16/20 mm, ~200 pcs) for ~$12-15 from Amazon. Covers F1-F5 and provides spares.

---

## 4. 3D Printed Parts

| # | Part | Qty | Material | Est. Weight | Notes |
|---|------|-----|----------|-------------|-------|
| P1 | Feeder hopper + base | 1 | PETG | ~120 g | Inclined hopper with side rails, throat, motor mount pocket. Largest single print. |
| P2 | Feeder roller (with O-ring grooves) | 1 | PETG | ~15 g | Precision bore for 5mm D-shaft. O-ring grooves for silicone friction surface. |
| P3 | Retard pad holder | 1 | PETG | ~8 g | Spring-loaded, replaceable pad slot. Wear part -- design for easy swap. |
| P4 | Selector carriage + card guide | 1 | PETG | ~45 g | Rides on MGN12H, belt clamp integrated. Card channel with entry funnel. |
| P5 | Selector motor mount bracket | 1 | PETG | ~30 g | End plate for NEMA17 at -X end of selector rail. |
| P6 | Selector idler bracket | 1 | PETG | ~20 g | Opposite end bracket with idler pulley mount. |
| P7 | Bin bank (8 bins) | 1-2 | PETG | ~250 g | May print as two 4-bin halves if bed is < 570 mm (likely). Entry funnels, smooth internal finish. Largest assembly. |
| P8 | Recombine X carriage + pickup head | 1 | PETG | ~50 g | MGN12H mount, Z-axis guide mounts, belt clamp. |
| P9 | Recombine rail mount plate | 1 | PETG | ~60 g | ~610x43 mm plate. Will need to print diagonally or in sections on standard 256 mm bed. |
| P10 | Recombine Z elevator bracket | 1 | PETG | ~25 g | Linear bearing holders, motor mount for Z stepper. |
| P11 | Recombine motor mount bracket (X) | 1 | PETG | ~30 g | NEMA17 end plate for recombine X axis. |
| P12 | Recombine Z motor mount | 1 | PETG | ~20 g | NEMA17 mount for Z leadscrew/belt drive. |
| P13 | Output tray | 1 | PETG | ~80 g | Card pocket with side guides, 4x chassis mount inserts. |
| P14 | Electronics bay / tray | 1 | PETG | ~40 g | Holds ESP32, TMC2209 boards, buck converter. Ventilation slots. |
| P15 | Chassis base frame | 2-4 | PETG | ~200 g | Structural base, printed in sections. Receives all module mounts via heat-set inserts. |
| P16 | Enclosure panels (top, sides) | 4-6 | PETG | ~180 g | Optional for V1. Can defer to open-frame for debug. |
| P17 | Feeder roller sleeve | 1 | TPU 95A | ~5 g | Alternative to O-rings: full TPU sleeve press-fit over roller for higher friction. |
| P18 | Output tray bumpers | 2 | TPU 95A | ~3 g | Soft landing pads for card stack squaring. |
| P19 | Sensor mount clips | 6 | PETG | ~12 g | Snap-fit or screw-on brackets for TCRT5000 modules at each checkpoint. |
| P20 | Belt tensioner blocks | 2 | PETG | ~10 g | Spring-loaded idler adjustment for GT2 belts. |
| P21 | Cable clips / guides | 6 | PETG | ~8 g | Snap-on wire management along frame. |

| | | | **PETG total** | **~1,200 g** | |
| | | | **TPU total** | **~8 g** | |

| # | Material | Qty | Specification | Unit Cost | Source | Notes |
|---|----------|-----|--------------|-----------|--------|-------|
| P-MAT1 | PETG filament | 2 kg | 1.75 mm, any color | $20/kg | Amazon (Hatchbox, eSUN, Polymaker) | ~1.2 kg estimated usage + waste/supports/reprints. 2 kg provides margin. |
| P-MAT2 | TPU filament (95A) | 0.25 kg | 1.75 mm, 95A Shore | $22 | Amazon (NinjaTek, eSUN) | Small usage but need a full spool. Could substitute O-rings (M11) for roller instead. |

**3D print material subtotal: ~$62**

---

## 5. Miscellaneous

| # | Part | Qty | Specification | Unit Cost | Source | Notes |
|---|------|-----|--------------|-----------|--------|-------|
| X1 | Tactile push button (panel mount, 12mm) | 2 | Momentary, normally-open, panel mount | $2 | Amazon / AliExpress | Shuffle button (GPIO 15) and Stop/Clear Jam button (GPIO 0). Internal pull-up. |
| X2 | Rubber feet (adhesive) | 4 | ~12 mm dia, ~6 mm height, adhesive backed | $3 | Amazon | Anti-vibration, non-slip base. |
| X3 | Cable sleeve / spiral wrap | 1 | 6 mm dia, 2 m length | $3 | Amazon | Wiring harness management for motor and sensor cables. |
| X4 | Zip ties (small) | 1 bag | 100 mm, nylon, assorted | $2 | Amazon | Cable management. |
| X5 | Heat shrink tubing assortment | 1 kit | 2:1 ratio, assorted diameters | $4 | Amazon | Solder joint insulation on sensor and power wiring. |
| X6 | M3 hex key (2.0 mm) | 1 | Ball-end preferred | $3 | Amazon | Service tool. L-key or T-handle. |
| X7 | Soldering iron with fine tip (if not owned) | -- | -- | -- | -- | Required for heat-set inserts and wiring. Assumed already owned. |

**Miscellaneous subtotal: ~$17**

---

## Cost Summary

| Category | Subtotal |
|----------|----------|
| Electronics | $112 |
| Mechanical -- Motion | $73 |
| Fasteners | $36 |
| 3D Print Material | $62 |
| Miscellaneous | $17 |
| **Total** | **$300** |

**Margin to $500 ceiling: $200 (40%)**

---

## Budget Headroom Allocation

Per the design document, the ~$200 headroom is intended for:

| Use | Est. Cost | Notes |
|-----|-----------|-------|
| Sensor upgrade: Omron B5W-LB2101 (replace TCRT5000 at critical positions) | $30 | Better focused beam, more reliable at 3-5 mm range. Use at feed exit and post-singulation; keep TCRT5000 at lower-risk positions. |
| Second ESP32 for logging / debug | $7 | Dedicated serial logger without interfering with control loop timing. |
| Vacuum pickup prototype parts (feeder bakeoff candidate) | $40 | Small vacuum pump, tubing, suction cups for candidate C evaluation. |
| Spare stepper motor | $12 | One extra standard NEMA17 in case of DOA or damage during assembly. |
| Spare TMC2209 drivers | $10 | Two extra drivers. These are fragile -- easy to fry during wiring. |
| Extra MGN12H carriage blocks | $12 | One spare per rail in case of binding or damage. |
| Upgraded belt (Gates PowerGrip GT2) | $10 | Higher quality belt if AliExpress GT2 has pitch accuracy issues. |
| Contingency | $79 | Unexpected parts, reprints, wrong sizes, shipping. |
| **Headroom total** | **$200** | |

---

## Ordering Notes

1. **AliExpress vs Amazon tradeoff**: AliExpress prices are 30-50% lower on motors, drivers, rails, and sensors, but shipping is 2-4 weeks. Amazon is 1-2 day delivery at higher cost. Prices above assume a mix. For fastest start, order everything from Amazon and expect ~$350-380 total.

2. **Linear rails**: buy from a reputable AliExpress seller (Hiwin clones from ReliaBot, CHUANGNUO, or similar). Cheap rails with poor ball recirculation will bind. Inspect and re-grease on arrival.

3. **TMC2209 wiring caution**: the UART daisy-chain requires correct MS1/MS2 pin configuration for addresses 0-3. Verify the breakout board pinout matches BIGTREETECH or Fysetc documentation before wiring.

4. **NEMA17 motor selection**: the feeder motor (E3) can be a cheaper pancake stepper because it runs at low current (600 mA) and moderate speed. The X-axis motors (E4, E5) need full-size 40 mm bodies for the torque to accelerate carriage mass at 4000 steps/s. The Z motor (E6) is intermediate.

5. **Fastener assortment**: a single M3 SHCS assortment kit (~$13) is more economical than buying individual lengths. Supplement with the specific M3x16 pack for NEMA17 mounting.

6. **Heat-set inserts**: buy 100 (two bags of 50). The CNC Kitchen / Ruthex M3x4x4 style is the standard for 3D printing. A soldering iron with a dedicated insertion tip ($8) makes installation much easier.

7. **Bin bank print strategy**: at 570 mm wide, the bin bank exceeds most printer beds. Plan to print as two 4-bin halves with a tongue-and-groove or dowel pin alignment joint, bolted together with M3 screws.

8. **Recombine rail mount plate**: at 610 mm, this also exceeds standard beds. Print in 2-3 sections and join with embedded M3 hardware or print diagonally on a 300+ mm bed (Ender 5 Plus, CR-10, Voron 350).
