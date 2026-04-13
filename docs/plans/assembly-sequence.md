# Assembly Sequence -- Single-Deck Card Shuffler V1

Date: 2026-04-12
Reference: `docs/plans/bom.md`, `docs/plans/print-guide.md`, `docs/plans/datum-tolerance-budget.md`

---

## Prerequisites

### All Printed Parts Ready

Before starting assembly, every printed part from the print guide must be complete with post-processing done:

- [ ] Chassis sections 0, 1, 2 (P15) -- heat-set inserts installed, dowel bores reamed, base plate sanded
- [ ] Bin bank sections (P7) -- interior walls sanded, heat-set inserts in base
- [ ] Feeder hopper (P1) -- bearing bores reamed, supports removed, heat-set inserts installed
- [ ] Feeder roller (P2) -- D-shaft bore reamed
- [ ] Retard pad holder (P3) -- pivot bore reamed, retard pad material glued in
- [ ] Selector carriage (P4) -- guide channel sanded
- [ ] Selector motor mount (P5) and idler bracket (P6)
- [ ] Recombine carriage (P8), rail plate (P9), Z elevator (P10), motor mounts (P11, P12)
- [ ] Output tray (P13) -- heat-set inserts installed
- [ ] Electronics bay (P14) -- heat-set inserts installed
- [ ] Sensor clips (P19), belt tensioners (P20), cable clips (P21)
- [ ] TPU roller sleeve (P17) and bumpers (P18)

### All BOM Items Received

Cross-reference `bom.md`. Key items to verify before starting:

- [ ] ESP32 DevKit V1 (E1) -- verify it powers on via USB and serial monitor works
- [ ] 4x TMC2209 driver boards (E2) -- verify all 4 have correct MS1/MS2 pads for addresses 0-3
- [ ] 4x NEMA17 steppers: 1 pancake E3, 2 standard E4/E5, 1 short E6
- [ ] 2x MGN12H rail + carriage sets, 600 mm (M1, M2)
- [ ] GT2 belts 2x 2m (M3, M4), 4 drive pulleys (M5), 2 idler pulleys (M6)
- [ ] 4x 608ZZ bearings (M7) or 625ZZ as specified in feeder CAD
- [ ] 5 mm D-shaft (M8)
- [ ] Compression springs (M9), extension springs for tensioners (M10)
- [ ] Silicone O-rings (M11) or TPU roller sleeve (P17)
- [ ] Retard pad material (M12)
- [ ] Shoulder bolts (M13)
- [ ] 2x 8 mm linear rods (M14), 2x LM8UU bearings (M15)
- [ ] Full fastener assortment: M3x6 through M3x20 SHCS, M3 hex nuts, washers, lock washers
- [ ] M3 brass heat-set inserts (100 pcs total, ~50 already installed in printed parts)
- [ ] 6x TCRT5000 IR sensors (E8)
- [ ] OLED display (E7)
- [ ] 12V PSU (E9), 5V buck converter (E10), IEC inlet (E11)
- [ ] JST-XH connectors (E12), wire (E15)
- [ ] Buttons (X1), rubber feet (X2)

### Tools Needed

- 2.0 mm hex key (M3 socket cap screws) -- ball-end preferred
- 2.5 mm hex key (M4 if used)
- Soldering iron with fine tip (for heat-set inserts, already done, and wiring)
- Heat-set insert installation tip (dedicated tip for soldering iron, or use a flat tip carefully)
- Digital calipers
- Multimeter
- Feeler gauge set (0.05 mm increments, for nip gap adjustment)
- Small Phillips screwdriver (for some sensor modules)
- Wire strippers, crimping tool for JST-XH
- USB cable (micro or Type-C depending on your ESP32 DevKit variant)
- Computer with PlatformIO or Arduino IDE installed
- Deck of playing cards (poker size, 52 cards) for testing
- Small level or straightedge (~300 mm)
- Needle files, 320-grit sandpaper
- CA glue (thin viscosity)
- Threadlocker (blue Loctite 242) -- optional but recommended for motor mount screws

---

## Assembly Sequence

### Phase 1: Chassis Frame

Everything mounts to the chassis, so assemble it first and verify datum surfaces.

#### Step 1.1: Join Chassis Sections

**Parts:** Chassis sections 0, 1, 2, 4x M4 dowel pins, 6x M3x10 bolts, 6x M3 nuts

1. Lay all three sections on a flat surface (glass, granite tile, or machine table) with the base plate face down (side rail facing up).
2. Insert two 4.0 mm dowel pins into the bores at the Split 1 joint (between sections 0 and 1). Pins should protrude ~8 mm from each face.
3. Slide section 1 onto the pins until the faces mate. The joint should close with minimal gap (< 0.3 mm).
4. Insert the 3x M3x10 bolts through the joint bolt holes from the bottom (base plate side) and thread M3 nuts on top. Tighten evenly.
5. Repeat for the Split 2 joint (sections 1 and 2).
6. Flip the assembled chassis right-side up. Check:
   - The side rail (Datum B) forms a continuous straight line. Sight along it -- no steps at the joints.
   - The base plate is flat. Set it on your flat surface and check for rocking. Shim under the joints if needed.
   - Measure overall length: should be ~785 mm (CHASSIS_LENGTH).

#### Step 1.2: Install Rubber Feet

**Parts:** 4x rubber feet (X2), 4x M3x8 bolts

1. Flip the chassis upside down.
2. Insert an M3x8 bolt through each corner foot hole (15 mm inset from each edge).
3. Place a rubber foot over each bolt and secure. The feet provide vibration isolation and prevent the machine from walking during operation.
4. Flip right-side up. The chassis should sit level and stable.

#### Step 1.3: Verify Datum Surfaces

Before mounting anything, confirm the three datum surfaces:

- **Datum A (base plate top):** Run your finger along it. It should be smooth and flat. If any section joints have a Z-step, sand the high side flush.
- **Datum B (side rail inner face):** Lay a straightedge along the full length. Maximum deviation: 0.3 mm. This is the lateral reference for every module.
- **Datum C (feeder end stop inner face):** Verify it is perpendicular to Datum B with a small square.

---

### Phase 2: Linear Rails

Install the linear rails early because other modules mount to or reference the rail carriages. Rails are easier to align before the chassis is crowded with parts.

#### Step 2.1: Selector Rail (MGN12H, 600 mm)

**Parts:** 600 mm MGN12H rail + carriage (M1), M3x6 bolts (quantity depends on rail hole count, typically 15-20)

1. The selector rail mounts alongside the bin bank zone on the chassis base plate. The rail runs parallel to Datum B along the X axis.
2. Loosely position the rail in the selector mounting area (X = 105 mm to X = 675 mm, the bin bank zone).
3. Insert M3x6 bolts through the rail's mounting holes into the chassis heat-set inserts. Start from the center and work outward. Finger-tighten only.
4. Push the rail against a straight reference (a steel ruler clamped along Datum B works well) to ensure it is parallel to the side rail. The rail-to-Datum-B distance must be consistent along its length to within 0.2 mm.
5. Tighten all bolts evenly, working from center outward. Do not overtorque -- the heat-set inserts will pull out of PETG if you exceed ~0.5 N-m.
6. Slide the carriage block back and forth by hand. It should glide smoothly with no binding. If it binds at any point, loosen the bolts in that area, re-align, and re-tighten.

#### Step 2.2: Recombine Rail (MGN12H, 600 mm)

**Parts:** 600 mm MGN12H rail + carriage (M2), M3x6 bolts

1. Mount the recombine rail to the recombine rail mount plate (P9) first, not directly to the chassis. Follow the same center-out bolt pattern.
2. Verify carriage motion across the full plate length.
3. Set the rail plate assembly aside -- it will be installed on the chassis after the bin bank.

---

### Phase 3: Bin Bank

The bin bank is the largest module and sets the physical positions of all 8 bins. The selector and recombine modules both reference the bin positions.

#### Step 3.1: Assemble Bin Bank Sections

**Parts:** Bin bank sections (P7), 4.0 mm dowel pins, M3x8 bolts, M3 nuts (for inter-section joints)

If printed as 4 quarters:
1. Join the 4 sections using dowel pins and bolts at each joint, same procedure as the chassis joints.
2. Verify bin-to-bin pitch by measuring center-to-center distance across several bin pairs. Nominal: 71.5 mm. Record the actual positions -- you will enter these as calibration values in firmware later.
3. Check internal bin dimensions: 65.5 mm width x 90.9 mm depth. Drop a card into each bin to verify free fit.

#### Step 3.2: Mount Bin Bank to Chassis

**Parts:** Assembled bin bank, M3x8 bolts, M3 washers

1. The bin bank sits in the bin bank zone (X = 105 to X = 675 mm) on the chassis base plate.
2. Push the bin bank's left edge (the side that will face the cards) against Datum B (side rail). This registers the bin bank laterally.
3. Insert M3x8 bolts through the bin bank's base clearance holes into the chassis heat-set inserts. The bin bank has slotted holes for X adjustment -- center the bolts in the slots for now.
4. Tighten all mounting bolts.
5. Verify: drop a card into each of the 8 bins. Every card should fall freely to the bin floor and sit flat.

---

### Phase 4: Feeder Module

The feeder is the most precision-critical module. Take your time here.

#### Step 4.1: Install Bearings and Shaft

**Parts:** Feeder hopper (P1), 2x 625ZZ bearings (or 608ZZ per BOM -- match to your CAD), 5 mm D-shaft (M8), O-rings (M11) or TPU sleeve (P17)

1. Press one 625ZZ bearing into the left side wall bore of the feeder hopper. It should be a firm press-fit. If it is too tight, ream the bore slightly and retry. If it is loose, use a drop of retaining compound (Loctite 638) or thin CA glue.
2. If using an eccentric bushing on the right side, install the bushing into the oversized right-side bore first, then press the second bearing into the bushing. If not using a bushing, press the second bearing directly.
3. Slide the 5 mm D-shaft through both bearings. Spin it -- it should rotate freely with no perceptible wobble.
4. Install the feeder roller (P2) onto the shaft. The D-flat prevents rotation. If using a TPU sleeve (P17), stretch it over the roller now. If using O-rings (M11), seat them in the roller grooves.
5. Verify the roller protrudes approximately 1.0 mm above the hopper floor surface. This is the drive contact point for the bottom card.

#### Step 4.2: Install Retard Pad Assembly

**Parts:** Retard pad holder (P3), 2x shoulder bolts (M13), 1x compression spring (M9)

1. Slide the retard pad holder into the dovetail channel from the right side of the hopper.
2. Insert the shoulder bolts through the side wall holes and through the holder's pivot bores. The holder should pivot freely on the shoulder bolts.
3. Insert the compression spring into the spring pocket behind the retard pad.
4. Thread the M3 set screw into the rear wall hole until it just contacts the spring. This controls the nip pressure.

#### Step 4.3: Set the Nip Gap

**Critical adjustment.** The gap between the roller surface and the retard pad determines whether the feeder singulates one card at a time.

1. With no cards in the hopper, rotate the roller by hand and observe the retard pad contact point.
2. Insert a 0.30 mm feeler gauge between the roller and the retard pad. It should slide through with light resistance.
3. Insert a 0.60 mm feeler gauge. It should NOT pass through (this would allow doubles).
4. Adjust the set screw to tune spring preload until the gap is in the 0.30-0.40 mm range.
5. If using an eccentric bushing, rotate it to fine-tune the roller height, then lock it with a set screw or friction fit.

#### Step 4.4: Mount NEMA17 Pancake Stepper (Feeder)

**Parts:** NEMA17 pancake stepper (E3), 4x M3x16 bolts

1. The motor mounts to the bottom of the feeder hopper on the mounting plate.
2. Slide the motor shaft through the pilot hole and into the roller shaft coupling (or the D-shaft bore if direct-drive).
3. Align the motor so the shaft engages the roller correctly.
4. Insert 4x M3x16 bolts through the mounting plate into the motor's threaded holes. Apply a drop of threadlocker to each bolt.
5. Tighten in a cross pattern.
6. Spin the motor shaft by hand. The roller should spin smoothly and the retard pad should deflect slightly when a card-thickness object passes through the nip.

#### Step 4.5: Mount Feeder to Chassis

**Parts:** Assembled feeder, M3x8 bolts

1. Place the feeder at the X = 0 end of the chassis, butting the back of the hopper against Datum C (feeder end stop).
2. Push the left side of the feeder against Datum B (side rail).
3. Bolt down through the feeder's base into the chassis heat-set inserts (4 locations). These are fixed holes (not slotted) because the feeder references Datum C directly.
4. Verify: the exit throat is clear, aligned with where the selector will be, and at the correct height above Datum A.

---

### Phase 5: Selector Module

#### Step 5.1: Assemble Selector Carriage onto Rail

**Parts:** Selector carriage (P4)

1. The MGN12H carriage block should already be on the selector rail (installed in Step 2.1).
2. Bolt the selector carriage (P4) onto the carriage block using 4x M3x8 bolts through the carriage's base plate into the block's threaded holes.
3. Slide the assembly back and forth by hand. The carriage should glide smoothly and the card guide channel should remain vertical (not tilting).

#### Step 5.2: Install Selector Motor Mount and Idler

**Parts:** Motor mount bracket (P5), idler bracket (P6), NEMA17 standard stepper (E4), GT2 20T drive pulley (M5), GT2 idler pulley (M6), 4x M3x16 bolts (motor), M3x8 bolts (bracket mounting)

1. Mount the NEMA17 stepper to the motor mount bracket (P5) using 4x M3x16 bolts. Apply threadlocker.
2. Press the GT2 20T drive pulley onto the motor shaft, teeth facing the rail. Tighten the set screw against the D-flat.
3. Bolt the motor mount bracket to the chassis at the -X end of the selector rail. Use slotted holes for X adjustment. Leave slightly loose.
4. Mount the idler bracket at the +X end of the rail. Install the idler pulley on a 5 mm shoulder bolt or shaft with a bearing.

#### Step 5.3: Install GT2 Belt (Selector)

**Parts:** GT2 belt (M3), belt tensioner block (P20), extension spring (M10)

1. Thread the GT2 belt around the drive pulley, along the rail, around the idler pulley, and back.
2. Clamp both belt ends into the belt clamp on the selector carriage (P4). Thread the belt through the clamp slot and tighten the 2x M3 clamp bolts.
3. Install the belt tensioner if needed -- a spring-loaded idler that keeps constant tension.
4. Check belt tension: press the belt midspan with a finger. It should deflect 2-3 mm with moderate pressure, then spring back. Too loose causes skipped teeth; too tight causes motor stall and premature bearing wear.

#### Step 5.4: Align Selector to Feeder Exit

1. Manually position the selector carriage at the feeder end (bin 0 position).
2. Check the alignment between the feeder exit throat and the selector card guide entry:
   - **Lateral (Y):** The guide channels should be co-linear. The card must pass from the feeder exit into the selector guide without hitting a wall edge. Adjust the selector mounting bolts in their slotted holes if needed.
   - **Vertical (Z):** The selector guide entry should be at the same height or slightly lower (up to 0.5 mm) than the feeder exit. A downward step is acceptable; an upward step will catch cards. Use shims under the selector rail if the Z step is wrong.
   - **Entry chamfer:** The selector guide has a 3 mm flared entry. Verify by sliding a card from the feeder exit path into the selector guide by hand. It should enter smoothly.
3. Once aligned, tighten all mounting bolts.

---

### Phase 6: Recombine Module

#### Step 6.1: Assemble Recombine Z Elevator

**Parts:** Z elevator bracket (P10), 2x 8 mm linear rods (M14), 2x LM8UU bearings (M15), pusher plate (from P8), Z motor mount (P12), NEMA17 short stepper (E6) or 28BYJ-48

1. Press the LM8UU linear bearings into the elevator bracket bores.
2. Slide the 8 mm rods through the bearings. The rods should move smoothly vertically.
3. Attach the pusher plate to the linear bearing carriage.
4. Verify the pusher plate travels smoothly through the full elevator range (0 to ~25 mm).
5. Mount the Z-axis stepper to the Z motor mount (P12) and connect it to the elevator mechanism (belt, leadscrew, or rack-and-pinion depending on your implementation).

#### Step 6.2: Assemble Recombine X Carriage

**Parts:** Recombine X carriage (P8), the Z elevator sub-assembly from Step 6.1, collection tray (part of recombine)

1. Bolt the recombine carriage (P8) onto the MGN12H carriage block on the recombine rail plate (assembled in Step 2.2).
2. Mount the Z elevator sub-assembly onto the X carriage.
3. Attach the collection/accumulator tray above the elevator.
4. Slide the assembly along the rail. Verify it travels the full bin bank width without interference.

#### Step 6.3: Install Recombine Motor Mount and Belt

**Parts:** Recombine motor mount bracket (P11), NEMA17 standard stepper (E5), GT2 pulley (M5), idler pulley (M6), GT2 belt (M4), belt tensioner (P20), extension spring (M10)

1. Same procedure as the selector belt installation (Steps 5.2 and 5.3), but for the recombine rail.
2. Mount the motor bracket at one end of the rail plate.
3. Thread and tension the belt. Clamp to the carriage.

#### Step 6.4: Mount Recombine Rail Plate to Chassis

**Parts:** Assembled recombine rail plate with carriage, M3x8 bolts

1. Position the rail plate assembly below/behind the bin bank (in the recombine zone on the chassis).
2. Bolt down using slotted holes for X adjustment. Align so the pusher plate can reach the center of each bin cavity when the X carriage is at the corresponding bin position.
3. Test: move the X carriage to each of the 8 bin positions. At each position, the pusher plate should align with the bin floor slot (if using bottom-push extraction). Adjust X position of the rail plate as needed.

#### Step 6.5: Squaring Station

**Parts:** Squaring station (integrated into recombine part), solenoid or tap arm mechanism

1. The squaring station is positioned after the accumulator tray in the card path. Verify the tight pocket dimensions: 64.5 mm width (card width + 0.5 mm per side clearance).
2. Mount the solenoid or tap-arm mechanism to the external boss on the squaring station. Wire to a JST-XH connector (leave wiring for Phase 8).
3. Test by manually placing a small stack of cards into the squaring station funnel. They should settle into the tight pocket and sit square.

---

### Phase 7: Output Tray

#### Step 7.1: Mount Output Tray

**Parts:** Output tray (P13), TPU bumpers (P18), 4x M3x8 bolts

1. Press or glue the TPU bumpers into the output tray.
2. Position the output tray at the far end of the chassis (X = 680 to X = 780 mm, the output zone).
3. Push the tray against Datum B.
4. Bolt down using slotted holes for X adjustment. The output tray has generous internal dimensions, so precise alignment is not critical.

#### Step 7.2: Verify Card Path

At this point, the full mechanical card path is assembled. Walk through it manually:

1. Place a card in the feeder hopper.
2. Manually rotate the feeder roller. The card should feed through the exit throat.
3. Manually guide the card from the feeder exit into the selector guide.
4. With the selector over bin 0, release the card. It should drop through the guide, through the funnel, and land flat in the bin.
5. Repeat for bins 1-7 by moving the selector carriage by hand.
6. Test the recombine pickup: manually raise the pusher plate through a bin floor slot. It should lift the card(s).
7. Test the squaring station: manually transfer a small stack into the squaring station funnel.
8. Test the output: manually place a deck in the output tray. It should sit square and be easy to pick up from the open front.

Fix any alignment issues, binding, or card-catching problems NOW before wiring electronics.

---

### Phase 8: Electronics and Wiring

#### Step 8.1: Power Distribution

**Parts:** 12V PSU (E9), IEC inlet + fused switch (E11), 5V buck converter (E10), wire (E15), connectors (E12)

1. Mount the IEC inlet panel connector in your enclosure panel or a dedicated bracket on the chassis.
2. Wire the IEC inlet hot and neutral through the fused switch to the 12V PSU input terminals. Connect earth ground to the PSU ground terminal and to the chassis (if metal parts are present; for all-plastic V1, ground to the PSU enclosure).
3. Mount the 12V PSU. It can sit in the electronics bay area or externally.
4. Wire the 12V PSU output to:
   - A distribution bus with 4 branches for the TMC2209 driver boards (VM / motor power).
   - The 5V buck converter input.
5. Adjust the buck converter output to 5.0V using a multimeter. Verify under no-load.
6. Wire the buck converter 5V output to:
   - ESP32 DevKit VIN pin (or 5V pin, depending on your board revision).
   - OLED display VCC.
   - TCRT5000 sensor modules VCC.

**Test checkpoint:** Power on the system. The ESP32 should boot (blue LED). The OLED should light up (if firmware already flashed). The 12V rail should read 12.0V +/- 0.5V. The 5V rail should read 5.0V +/- 0.1V.

#### Step 8.2: TMC2209 Driver Boards

**Parts:** 4x TMC2209 boards (E2), perfboard (E14), JST-XH connectors

1. Set the UART addresses on each board using the MS1/MS2 solder jumpers:
   - Feeder motor driver: Address 0 (MS1 = low, MS2 = low)
   - Selector X driver: Address 1 (MS1 = high, MS2 = low)
   - Recombine X driver: Address 2 (MS1 = low, MS2 = high)
   - Recombine Z driver: Address 3 (MS1 = high, MS2 = high)
2. Mount all 4 drivers on the perfboard or directly on the electronics bay standoffs.
3. Wire the UART bus: all 4 drivers share a single UART TX/RX pair on ESP32 GPIO 12 (TX) and GPIO 13 (RX). Use 1K ohm resistors in series on each driver's UART pin if the driver board does not have them onboard. This is a daisy-chain bus.
4. Wire motor outputs: each TMC2209 has 4 motor output pins (A1, A2, B1, B2). Wire to the corresponding NEMA17 stepper coils using JST-XH connectors for each motor. Double-check coil pairing with a multimeter (continuity between A1-A2 and between B1-B2).
5. Wire motor power: connect 12V and GND to each driver's VM and GND pins.
6. Wire logic power: connect 5V to each driver's VCC pin.

**Critical warning:** Never connect or disconnect motor wires while the driver is powered. Disconnecting a motor under power will destroy the TMC2209 driver. Always power down first.

#### Step 8.3: ESP32 Wiring

**Parts:** ESP32 DevKit (E1), wire, JST-XH connectors

Wire the ESP32 GPIO pins to all peripherals. Suggested pin assignments (from BOM):

| Function | GPIO | Notes |
|----------|------|-------|
| TMC2209 UART TX | 12 | Shared bus to all 4 drivers |
| TMC2209 UART RX | 13 | Shared bus |
| Feeder STEP | 16 | Step pulse output |
| Feeder DIR | 17 | Direction output |
| Selector X STEP | 18 | Step pulse output |
| Selector X DIR | 19 | Direction output |
| Recombine X STEP | 25 | Step pulse output |
| Recombine X DIR | 26 | Direction output |
| Recombine Z STEP | 27 | Step pulse output |
| Recombine Z DIR | 14 | Direction output |
| OLED SDA | 21 | I2C data |
| OLED SCL | 5 | I2C clock (note: GPIO 5 has pull-up at boot) |
| Sensor: Feed exit | 34 | Input only, no pull-up (use external if needed) |
| Sensor: Post-singulation | 35 | Input only |
| Sensor: Selector throat | 36 | Input only |
| Sensor: Bin entry | 39 | Input only |
| Sensor: Recombine pickup | 23 | General GPIO |
| Sensor: Output checkpoint | 22 | General GPIO |
| Shuffle button | 15 | Internal pull-up, active-low |
| Stop/Clear Jam button | 0 | Internal pull-up, active-low (boot pin -- hold low at reset enters bootloader) |
| Solenoid (squaring tap) | 4 | Digital output, through MOSFET |

1. Wire all STEP and DIR pins to the corresponding TMC2209 inputs.
2. Wire I2C bus (SDA/SCL) to the OLED display.
3. Wire each TCRT5000 sensor module's digital output to the assigned GPIO pin. Connect sensor VCC and GND.
4. Wire the two panel buttons to their GPIO pins. Each button connects the pin to GND when pressed (using the ESP32's internal pull-up resistors).
5. If using a solenoid for the squaring station, wire GPIO 4 through a logic-level MOSFET (IRLZ44N or similar) to control the solenoid coil. Include a flyback diode across the solenoid.

#### Step 8.4: Sensor Installation

**Parts:** 6x TCRT5000 modules (E8), 6x sensor mount clips (P19), M3x6 bolts

Mount sensors at these positions along the card path:

1. **Feed exit sensor** -- at the feeder exit throat, detects a card leaving the feeder.
2. **Post-singulation sensor** -- just after the nip zone, confirms only one card passed.
3. **Selector throat sensor** -- at the entry to the selector card guide, confirms the card entered the selector.
4. **Bin entry sensor** -- at the bottom of the selector guide, confirms the card dropped into a bin.
5. **Recombine pickup sensor** -- on the pusher plate or above it, detects stack presence during extraction.
6. **Output checkpoint sensor** -- at the output tray entry, confirms final deck delivery.

For each sensor:
1. Snap or bolt the TCRT5000 module into a sensor mount clip (P19).
2. Bolt the clip to the appropriate location on the feeder, selector, or chassis.
3. Aim the sensor so the IR beam crosses the card path at 2-5 mm range.
4. Route the sensor wire through cable channels and secure with cable clips (P21).

#### Step 8.5: OLED Display and Buttons

**Parts:** SSD1306 OLED (E7), 2x panel buttons (X1), wire

1. Mount the OLED display in the electronics bay or on an enclosure panel. It connects via the I2C bus (4 wires: VCC, GND, SDA, SCL).
2. Mount the Shuffle and Stop buttons on an enclosure panel or a bracket on the chassis. Wire to their GPIO pins and GND.

#### Step 8.6: Cable Management

**Parts:** Cable clips (P21), zip ties (X4), cable sleeve (X3)

1. Route all motor cables through the chassis cable channels (8 mm wide grooves in the base plate top surface, running longitudinally and transversely).
2. Bundle motor cables using cable sleeve or spiral wrap.
3. Secure with printed cable clips at intervals.
4. Keep power wires (12V motor supply) separated from signal wires (sensor, UART) to reduce noise.
5. Leave enough slack at each motor and sensor for module removal during service.

---

### Phase 9: Firmware Flashing

#### Step 9.1: Flash ESP32

1. Connect the ESP32 to your computer via USB.
2. Open the firmware project in PlatformIO or Arduino IDE.
3. Verify the pin assignments in the firmware configuration file match the wiring from Step 8.3.
4. Compile and upload.
5. Open the serial monitor at 115200 baud. You should see boot messages.

#### Step 9.2: TMC2209 UART Verification

1. The firmware should attempt to communicate with each TMC2209 on the UART bus at startup.
2. Check the serial monitor for each driver responding at its address (0, 1, 2, 3). If a driver does not respond:
   - Verify MS1/MS2 jumper settings.
   - Check UART wiring (TX/RX not swapped).
   - Verify 5V power to the driver's VCC pin.
3. Once all 4 drivers respond, verify motor direction by commanding a small move on each axis. If a motor spins the wrong way, swap the DIR pin polarity in firmware (or swap one coil pair on the JST connector).

---

### Phase 10: First Power-On and Self-Test

**Do not load cards yet.** This phase verifies all axes move correctly and all sensors read properly.

#### Step 10.1: Boot Self-Test Sequence

Power on the machine with no cards loaded. The firmware should run an automatic self-test:

1. **OLED check:** Display shows "Shuffler V1 -- Self Test".
2. **Sensor check:** Each of the 6 TCRT5000 sensors is read. The display or serial monitor should report the analog value for each. With no cards present, all sensors should read "clear" (above the detection threshold).
3. **Motor check (feeder):** The feeder roller spins briefly in the forward direction, then stops. Listen for smooth microstepping -- no grinding or skipping.
4. **Motor check (selector X):** The selector carriage moves a short distance (10 mm) in each direction, then returns to start. Listen and watch for smooth motion.
5. **Motor check (recombine X):** Same as selector -- short jog in each direction.
6. **Motor check (recombine Z):** The pusher plate moves up 5 mm, then back down.
7. **Self-test result:** Display shows "PASS" or reports which subsystem failed.

If any motor stalls, grinds, or does not move:
- Check TMC2209 motor current setting (configured via UART -- start at 400 mA RMS and increase if needed).
- Check mechanical binding on that axis.
- Check wiring continuity on the motor connector.

If any sensor reads incorrectly:
- Verify the sensor is aimed at the card path.
- Check the sensor-to-surface distance (2-5 mm nominal for TCRT5000).
- Verify wiring to the correct GPIO pin.

#### Step 10.2: Homing Sequence

The selector and recombine X axes need a home position reference.

1. **Selector homing:** The selector carriage moves toward the -X end (motor mount end) until it triggers a homing sensor or endstop (microswitch or TCRT5000). The carriage should stop, back off 2 mm, then re-approach slowly for a precise home position. Record this as X = 0.
2. **Recombine X homing:** Same procedure for the recombine axis.
3. **Recombine Z homing:** The pusher plate moves down until it triggers a Z-home sensor or stalls against a physical stop (use StallGuard if TMC2209 StealthChop supports it, otherwise a microswitch).

Verify: command each axis to move to a known position and measure with calipers. The actual position should match the commanded position within 0.2 mm.

---

### Phase 11: Initial Calibration

#### Step 11.1: Selector Bin Positions

The selector needs to know the exact X position of each bin center. Because of print tolerances, these will differ slightly from the nominal 71.5 mm pitch.

1. Using the serial monitor or a calibration routine in firmware, manually jog the selector to center it over bin 0. Record the position.
2. Repeat for bins 1 through 7.
3. Store all 8 positions in firmware EEPROM/NVS.
4. Verify: command the selector to each bin position in sequence. At each position, drop a card through the guide by hand. The card should land cleanly in the target bin, not on a wall or in the adjacent bin.

#### Step 11.2: Recombine Bin Positions

Same procedure for the recombine X axis. The recombine must align its pusher plate with each bin's floor slot.

1. Jog the recombine X to each bin position.
2. At each position, command the Z axis to raise the pusher plate. Verify it enters the bin cavity cleanly without hitting bin walls.
3. Store all 8 positions in firmware EEPROM/NVS.

#### Step 11.3: Sensor Thresholds

Each TCRT5000 sensor needs a detection threshold calibrated to its specific mounting position and ambient light conditions.

1. With no card present, read the sensor's analog value. Record as the "clear" baseline.
2. Place a card at the sensor position. Read the analog value. Record as the "card present" value.
3. Set the threshold midway between clear and card-present values.
4. Store thresholds in firmware EEPROM/NVS.
5. Repeat for all 6 sensors.

#### Step 11.4: Feeder Speed and Current Tuning

1. Start with the feeder motor at 400 mA RMS and 60 mm/s feed speed.
2. Load 10 cards into the hopper.
3. Command the feeder to singulate one card. Observe:
   - Did exactly one card feed? (Check with the post-singulation sensor.)
   - Did it feed cleanly into the selector guide?
   - Any sounds of slipping, grinding, or multi-feeding?
4. Gradually increase speed toward the 120 mm/s target while monitoring for multi-feeds.
5. Adjust motor current (up to 600 mA rated) if the roller slips.
6. Adjust the retard pad spring preload (M3 set screw) if multi-feeds occur.

#### Step 11.5: Full Shuffle Dry Run

1. Load a full 52-card deck into the feeder hopper.
2. Command a single pass (pass 1): singulate all 52 cards into the 8 bins using a random bin assignment.
3. Observe the entire pass. Note any jams, mis-feeds, or mis-sorts.
4. Command the recombine sequence: collect all 8 bin stacks into the accumulator tray.
5. Run the squaring station.
6. Reload the squared deck into the feeder (pass 2).
7. Repeat singulation with a different random assignment.
8. Final recombine and deliver to the output tray.

**Target time:** 30 seconds for the full 2-pass shuffle (CYCLE_TIME_TARGET in constants.py). On initial runs, expect 45-60 seconds as you tune speeds.

---

### Phase 12: Final Checks

- [ ] All fasteners are tight, motor mount bolts have threadlocker.
- [ ] No loose wires; all connections use JST-XH or soldered joints with heat shrink.
- [ ] Belt tension is correct on both X axes (2-3 mm deflection).
- [ ] Feeder nip gap is set (0.30-0.40 mm).
- [ ] All 8 bin positions are calibrated and stored in firmware.
- [ ] All 6 sensors are calibrated with thresholds stored.
- [ ] Full 52-card shuffle completes without jams (run at least 5 consecutive shuffles).
- [ ] Output deck is fully shuffled (visually verify randomization).
- [ ] OLED displays status correctly during operation.
- [ ] Shuffle and Stop buttons function correctly.
- [ ] Machine sits level on rubber feet, does not walk during operation.
- [ ] Power supply is secure, IEC inlet fuse is correctly rated.

---

## Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Multi-feed (2+ cards at once) | Nip gap too wide or retard pad worn | Tighten set screw (reduce gap); replace retard pad material |
| No feed (roller slips) | Nip gap too tight, roller dirty, or motor current too low | Loosen set screw; clean roller with isopropanol; increase TMC2209 current |
| Card jams at feeder-selector handoff | Z step between feeder exit and selector entry | Add shim under selector rail; verify lead-in chamfer on selector guide |
| Card misses bin (lands on wall) | Selector position miscalibrated or belt skip | Recalibrate bin positions; check belt tension and pulley set screws |
| Card sticks in bin | Rough bin walls or bin too tight | Sand interior walls; verify bin internal width is 65.5 mm |
| Recombine pusher catches on bin wall | X position miscalibrated or pusher too wide | Recalibrate; verify pusher width is < bin internal width minus 1.0 mm |
| Stack wedges in squaring station | Stack too skewed or squaring pocket too tight | Run squaring tap multiple times; verify pocket width is 64.5 mm |
| Motor stalls (high-pitched whine) | Current too low or mechanical binding | Increase TMC2209 current (check motor rating); check for debris or misalignment |
| TMC2209 overheats | Current too high or poor ventilation | Reduce current; add heatsinks; ensure electronics bay has airflow |
| Sensor false triggers | Ambient light interference or wrong threshold | Shield sensors; recalibrate thresholds; use digital output mode with onboard potentiometer |
| ESP32 resets during motor moves | Power supply brownout | Verify 12V supply capacity; add capacitor (470 uF) across motor power bus |
