# 3D Printing Guide -- Single-Deck Card Shuffler V1

Date: 2026-04-12
Reference CAD: `cad/constants.py`, module source files
Print tolerance defaults: 0.2 mm general, 0.1 mm tight (bearing bores, shaft fits)

---

## General Print Settings

Unless overridden per-part below, use these defaults:

| Setting | Value |
|---------|-------|
| Material | PETG (eSUN, Polymaker, or Hatchbox) |
| Nozzle | 0.4 mm |
| Layer height | 0.2 mm |
| Perimeters | 4 (gives ~1.6 mm wall, above the 1.2 mm minimum) |
| Top/bottom layers | 5 (1.0 mm solid) |
| Infill | 25% gyroid |
| Print speed | 50 mm/s for perimeters, 80 mm/s for infill |
| Bed temp | 80 C |
| Nozzle temp | 240 C (tune to your filament) |
| Elephant foot compensation | -0.15 mm first layer horizontal expansion |
| Seam position | Rear / nearest to edge (away from card-contact surfaces) |
| Support | Only where noted per part |

**TPU parts** use different settings -- see the TPU section at the end.

**Before printing any parts:** Print a tolerance test coupon with a 22.0 mm bore, a 5.0 mm bore, and a 3.2 mm bore. Measure with calipers. If your printer under/over-sizes bores by more than 0.1 mm, apply a horizontal expansion correction in your slicer globally rather than editing the CAD.

---

## Part-by-Part Guide

### P15: Chassis Base Frame (3 sections)

| | |
|---|---|
| **File** | `cad/chassis/chassis_section_0.step`, `chassis_section_1.step`, `chassis_section_2.step` |
| **Material** | PETG |
| **Quantity** | 3 sections |
| **Layer height** | 0.2 mm |
| **Infill** | 30% gyroid (structural -- carries all module loads) |
| **Estimated weight** | ~65 g per section (~200 g total) |
| **Estimated time** | ~4-5 hr per section |

**Why it is split:** The full chassis is ~785 mm long (total X extent). Each section is roughly 261 mm, which fits most 256 mm+ beds. The split points include alignment dowel pin holes (4.2 mm bores) and M3 bolt holes at each joint.

**Print orientation:** Print each section flat, base plate on the build plate. The side rail and end stop walls print vertically. This gives the best surface accuracy on the base plate top (Datum A) since it is the first layer's mating surface flipped over.

**Supports:** Not needed. The side rail, end stop, and stiffening rib all grow straight up from the base plate.

**Critical dimensions to check:**
- Base plate flatness: lay on a known-flat surface and check for rocking. Should be < 0.2 mm deviation across the section.
- Dowel pin bores at split joints: 4.2 mm diameter (4.0 mm pin + 0.2 mm clearance). Check with a 4.0 mm rod -- it should slide in with light finger pressure.
- M3 heat-set insert bores: 3.2 mm diameter, 5.0 mm deep. Check with a 3.0 mm drill bit -- slight resistance is correct.
- Side rail inner face: this is Datum B. It must be straight along its full length. Sight down the rail -- any bow > 0.3 mm will affect card alignment across the machine.

**Post-processing:**
1. Install M3 brass heat-set inserts with a soldering iron at 220 C. The chassis receives approximately 16 inserts for module mounting plus 4-6 for the electronics bay. Count from the CAD: 4 feeder mount, 12 bin bank mount, 6 selector mount, 3 recombine mount, 4 output mount, plus electronics bay inserts.
2. Ream the dowel pin bores with a 4.0 mm drill bit if the alignment pins do not slide in freely.
3. Lightly sand the base plate top surface (Datum A) with 220-grit on a flat surface to remove any first-layer texture. This is the reference for all module Z heights.
4. Test-fit the 3 sections together with dowel pins before installing any heat-set inserts. Confirm the side rail forms a continuous straight line across all joints.

---

### P1: Feeder Hopper + Base (Candidate A)

| | |
|---|---|
| **File** | `cad/feeder/feeder_candidate_a.step` |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.2 mm (0.12 mm for the exit throat zone -- see notes) |
| **Infill** | 25% gyroid |
| **Estimated weight** | ~120 g |
| **Estimated time** | ~6-8 hr |

**Print orientation:** Print with the NEMA17 mounting plate face down (motor side on the build plate). This puts the hopper opening at the top and the exit throat walls printing vertically. The critical throat gap dimension is formed by vertical walls, not horizontal bridges, which gives the best accuracy.

**Supports:** YES -- needed for:
- The bearing pockets in the side walls (horizontal cylindrical bores, 8.2 mm radius). Use tree supports or painted supports on these bores only. Breakaway style, not soluble, is fine since you will ream the bores.
- The roller pocket in the hopper floor (cylindrical bore through the floor).
- The exit guide channel ceiling (small horizontal overhang).
- The dovetail slide channel for the retard pad holder.

Keep supports away from the hopper interior walls -- these need a smooth finish for cards to slide.

**Layer height note:** If your slicer supports variable layer height (PrusaSlicer, OrcaSlicer), use 0.12 mm layers for the zone from Z = 0 to Z = 10 mm (the throat gap and roller pocket area). This improves the resolution of the 0.35 mm throat gap. The rest of the hopper can stay at 0.2 mm.

**Critical dimensions to check:**
- Exit throat gap: 0.8 mm nominal (CARD_THICKNESS 0.3 mm + 0.5 mm clearance). After printing, this will likely round to the nearest layer increment. Verify with feeler gauges -- a 0.3 mm gauge should pass, a 0.6 mm gauge should not pass easily. If the gap is too tight, sand lightly; if too loose, the retard pad spring preload compensates.
- Bearing bores in side walls: 8.2 mm radius (16.4 mm diameter). Test-fit a 625ZZ bearing (16 mm OD). It should press in with moderate force. If too tight, ream with a 16 mm drill bit or round file.
- NEMA17 pilot recess: 22.2 mm diameter, 2.5 mm deep. Test-fit against a NEMA17 face plate.
- NEMA17 mounting holes: 3.4 mm clearance for M3. Should accept M3 bolts freely.
- Shaft through-hole: 5.2 mm diameter. Must clear the 5 mm D-shaft with room to spin.
- Eccentric bushing bore (right side): 20.2 mm diameter. Verify the eccentric bushing fits.

**Post-processing:**
1. Carefully remove all supports from bearing pockets. Use a needle file to clean up the bore surface.
2. Ream both bearing bores for a smooth press-fit. Test-fit the 625ZZ bearings.
3. Clean out the roller pocket -- remove any stringing or support residue.
4. Sand the hopper interior walls lightly (320-grit) for smooth card feeding. Pay special attention to the exit throat channel walls.
5. Clean the retard pad dovetail channel so the holder slides freely.
6. Tap the M3 set screw hole in the rear wall (spring preload adjustment) with an M3 tap if needed, or install an M3 heat-set insert.
7. Install heat-set inserts for chassis mounting (4 locations on the base).

---

### P2: Feeder Roller (with O-ring grooves)

| | |
|---|---|
| **File** | (Generated from feeder CAD, or modeled separately) |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.12 mm (precision part) |
| **Infill** | 60% gyroid (structural rigidity) |
| **Estimated weight** | ~15 g |
| **Estimated time** | ~1.5 hr |

**Print orientation:** Print with the shaft bore vertical (bore axis = Z axis). This gives the best bore roundness. The O-ring grooves will be concentric rings formed by perimeters, which is ideal.

**Supports:** None needed.

**Critical dimensions to check:**
- Center bore: 5.2 mm for the D-shaft (5.0 mm shaft + 0.2 mm tight tolerance). The D-flat must be correct. Test-fit on the actual motor shaft.
- O-ring grooves: sized for 18-22 mm ID O-rings with 2-3 mm cross-section. Test-fit an O-ring -- it should seat fully in the groove without bulging above the roller OD.
- Roller OD: 20.0 mm. Measure with calipers.

**Post-processing:**
1. Ream the center bore with a 5 mm drill bit. The D-shaft must spin freely but without excessive wobble (< 0.1 mm radial play).
2. Test-fit O-rings. If grooves are too tight, widen gently with a hobby knife.

---

### P3: Retard Pad Holder

| | |
|---|---|
| **File** | (Derived from feeder CAD retard cavity dimensions) |
| **Material** | PETG |
| **Quantity** | 1 (print 2 -- this is a wear/tuning part) |
| **Layer height** | 0.2 mm |
| **Infill** | 40% gyroid |
| **Estimated weight** | ~8 g |
| **Estimated time** | ~0.5 hr |

**Print orientation:** Print flat, pad contact face up. The dovetail slide profile should be on the bottom layer for accuracy.

**Supports:** None.

**Critical dimensions:**
- Shoulder bolt pivot bore: 4.2 mm (4.0 mm shoulder + 0.2 mm clearance). Must spin freely on the shoulder bolt.
- Pad slot dimensions: 40 x 15 x 3 mm cavity for the cork/rubber retard pad material.
- Dovetail profile: must slide smoothly into the feeder housing channel.

**Post-processing:**
1. Ream pivot bore with a 4 mm drill bit.
2. Test-fit in the feeder dovetail channel. Sand the dovetail surfaces if the slide is too tight.
3. Cut the retard pad material (cork/rubber composite) to 40 x 15 mm and glue it into the slot with CA glue.

---

### P4: Selector Carriage + Card Guide

| | |
|---|---|
| **File** | `cad/selector/selector.step` (carriage portion) |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.2 mm |
| **Infill** | 30% gyroid |
| **Estimated weight** | ~45 g |
| **Estimated time** | ~3-4 hr |

**Print orientation:** Print with the carriage base plate on the build plate and the card guide channel growing upward. This puts the MGN12H mounting holes on the bottom face (best flatness) and the guide channel walls vertical (best dimensional accuracy for card slot width).

**Supports:** Minimal. The belt clamp overhang on the rear may need support depending on the angle. The card entry flare at the top of the guide is a small overhang that most printers handle without support (3 mm flare at roughly 45 degrees).

**Critical dimensions to check:**
- MGN12H bolt pattern: 20 mm x 12 mm spacing, M3 clearance holes (3.4 mm). Test-fit on the carriage block before full assembly.
- Card guide internal width: 65.5 mm (card width + 2 x 1.0 mm clearance). Measure at multiple heights along the channel.
- Card guide internal depth (slot thickness): 1.3 mm (card thickness + 1.0 mm clearance). Measure with feeler gauges.
- Belt slot: 7.0 mm wide x 2.0 mm tall. Test-fit a GT2 belt through the clamp.
- Guide channel height: 30 mm. Cards must slide through without catching.

**Post-processing:**
1. Sand the inside of the card guide channel walls (320-grit) for smooth card sliding.
2. Verify the belt clamp slot with a piece of GT2 belt. It should slide through with slight resistance when the clamp bolts are loose, and grip firmly when tightened.
3. No heat-set inserts needed -- this part uses through-bolts to the MGN12H block.

---

### P5: Selector Motor Mount Bracket

| | |
|---|---|
| **File** | `cad/selector/selector.step` (motor mount portion -- separate during export) |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.2 mm |
| **Infill** | 40% gyroid (carries motor cantilevered load) |
| **Estimated weight** | ~30 g |
| **Estimated time** | ~2 hr |

**Print orientation:** Print with the base flange on the build plate, motor mounting face vertical. The NEMA17 bolt pattern will be on a vertical face, which prints well with good hole accuracy.

**Supports:** Possibly needed under the base flange overhang where it meets the vertical plate, depending on the fillet radius. Use minimal breakaway supports.

**Critical dimensions to check:**
- NEMA17 mounting holes: 31 mm diagonal pattern, M3 clearance (3.4 mm).
- NEMA17 pilot recess: 22.2 mm diameter.
- Shaft through-hole: 5.2 mm diameter.
- Base flange mounting holes: M3 clearance (3.4 mm), positioned to reach chassis heat-set inserts.

**Post-processing:**
1. Install M3 heat-set inserts in the base flange if the chassis uses clearance holes at these positions (check CAD).
2. Test-fit a NEMA17 motor to the face plate. All 4 bolts should thread in without binding.

---

### P6: Selector Idler Bracket

| | |
|---|---|
| **File** | (Separate part, mirror of motor mount without the motor pattern) |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.2 mm |
| **Infill** | 30% gyroid |
| **Estimated weight** | ~20 g |
| **Estimated time** | ~1.5 hr |

**Print orientation:** Same as motor mount -- base flange down.

**Supports:** None typically needed.

**Critical dimensions:**
- Idler pulley bore: 5.2 mm for a 5 mm shoulder bolt or shaft.
- Base mounting holes: M3 clearance.

**Post-processing:**
1. Ream idler bore with a 5 mm drill bit.
2. Install heat-set inserts if applicable.

---

### P7: Bin Bank (8 bins, printed as sections)

| | |
|---|---|
| **File** | `cad/bin-bank/bin_bank.step` (full), split for printing |
| **Material** | PETG |
| **Quantity** | 4 sections (2-bin quarters) or 2 sections (4-bin halves) |
| **Layer height** | 0.2 mm (0.12 mm for the top 3 mm funnel zone if using variable layer height) |
| **Infill** | 20% gyroid (walls are the structural element, not infill) |
| **Estimated weight** | ~250 g total (~63 g per quarter, ~125 g per half) |
| **Estimated time** | ~5-6 hr per quarter, ~10-12 hr per half |

**Why it is split:** The full bin bank is 570 mm along X. This exceeds all common print beds. Split options:

- **4 quarters of 2 bins each (~143 mm):** Fits any printer with a 150 mm+ bed. Recommended for Bambu A1 Mini, Prusa MK3/MK4, Ender 3. Three alignment joints, each with 2 dowel pin holes and 2-3 bolt holes.
- **2 halves of 4 bins each (~285 mm):** Fits Bambu X1C (256 mm -- tight, may need diagonal), Prusa XL (360 mm), or any 300mm+ bed. One joint, fewer tolerance stack.

Choose based on your bed size. Halves are preferred if your bed allows it (fewer joints = better bin-to-bin accuracy).

**Splitting procedure:** In your slicer or CAD, cut the bin bank STL at the midpoint of the BIN_SPACING gap between bins 2-3, 4-5, and 6-7 (for quarters) or bins 4-5 (for halves). The 2.0 mm gap between bins provides a natural cut line. Add alignment dowel pin holes (4.0 mm, 8 mm deep) on each mating face during CAD export, or drill them after printing using a jig.

**Print orientation:** Print each section with the bin floor on the build plate and bin openings facing up. This gives:
- Best floor flatness (critical for recombine pusher plate interaction).
- Vertical bin walls (best dimensional accuracy for card clearance).
- Open top for easy support removal if any bridges require it.

**Supports:** Minimal. The funnel chamfers at the top of each bin are 3 mm at 45 degrees -- most printers handle 45-degree overhangs without support. If your printer struggles with 45-degree overhangs in PETG, add painted support on the funnel chamfer undersides only.

**Critical dimensions to check:**
- Bin internal width: 65.5 mm. Measure each bin with calipers at floor level and at the midpoint. All 8 bins should be within +/- 0.3 mm of each other.
- Bin internal depth: 90.9 mm. Same check.
- Bin pitch (center-to-center between adjacent bins): 71.5 mm nominal (69.5 mm cell + 2.0 mm spacing). Measure across multiple bins and compare to nominal. The selector will calibrate to actual positions, but they should be close.
- Floor flatness: lay a straightedge across each bin floor. Should be flat to 0.2 mm.
- Funnel chamfer: 3.0 mm at 45 degrees. Verify the top opening is wide enough for card entry. Test by dropping a card through each funnel -- it should fall freely without catching.

**Post-processing:**
1. Sand bin interior walls lightly (320-grit) to remove layer lines. Cards must slide freely without catching.
2. If printed as sections, join with 4.0 mm dowel pins and M3 bolts. Apply a thin bead of CA glue along the joint if desired for rigidity, but the bolts alone should suffice.
3. Install M3 heat-set inserts on the bottom face for chassis mounting (4 corner locations per the CAD).
4. Drop-test every bin with a playing card before assembly. The card should fall to the floor under gravity without sticking.

---

### P8: Recombine X Carriage + Pickup Head

| | |
|---|---|
| **File** | `cad/recombine/recombine.step` (carriage + pusher + elevator section) |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.2 mm |
| **Infill** | 30% gyroid |
| **Estimated weight** | ~50 g |
| **Estimated time** | ~4 hr |

**Print orientation:** Print with the MGN12H mounting face on the build plate. The elevator frame and pusher guide channel grow upward.

**Supports:** YES -- needed for:
- The pusher travel channel (internal horizontal ceiling).
- The vertical guide slots (if they have horizontal ceilings).
Use breakaway supports; avoid support touching the pusher travel bore surfaces.

**Critical dimensions to check:**
- MGN12H bolt pattern: 20 x 15 mm, M3 clearance.
- Pusher channel width: must accept the pusher plate (63.5 mm wide) with 0.4 mm total clearance.
- Elevator guide slot width: 8.0 mm, must accept the linear guide rods or printed slide.
- Sensor mount holes on pusher plate: M2 clearance (2.2 mm).

**Post-processing:**
1. Remove supports from the pusher channel. Clean the channel walls so the pusher plate slides freely.
2. Test-fit the pusher plate in the channel -- it should move smoothly through the full elevator travel without binding.
3. Install sensor onto the pusher plate boss.

---

### P9: Recombine Rail Mount Plate

| | |
|---|---|
| **File** | `cad/recombine/recombine.step` (rail plate section) |
| **Material** | PETG |
| **Quantity** | 2-3 sections (total plate is ~610 mm long) |
| **Layer height** | 0.2 mm |
| **Infill** | 30% gyroid |
| **Estimated weight** | ~60 g total |
| **Estimated time** | ~3-4 hr per section |

**Why it is split:** The rail mount plate is 610 mm x 43 mm x 4 mm. At 610 mm, it must be split into 2-3 sections similar to the chassis. Split at points between rail mounting holes (every 20 mm), adding dowel pin holes at each joint.

**Print orientation:** Print flat. The 4 mm plate thickness means this is essentially a thin slab. Print it with the rail-mounting face up (the top surface) so the MGN12 rail seats on the smoothest surface.

**Supports:** None.

**Critical dimensions:**
- Rail mounting holes: M3 clearance, spaced 20 mm along the length. These must be straight and consistent -- the linear rail must lay flat along the plate.
- Plate flatness: this is critical. After printing, lay the plate on a flat surface and check for warp. PETG plates this thin can warp. If warped, anneal in an oven at 80 C for 30 min, then cool slowly, or clamp flat while still warm off the print bed.
- M3 heat-set insert bores at corners for chassis mounting.

**Post-processing:**
1. Check flatness. If warped, re-flatten by warming and clamping.
2. Install heat-set inserts at the 4 corner chassis mounting points.
3. Bolt the MGN12H rail to the plate and verify the carriage slides smoothly across the full length without binding. If it binds, the plate is not flat enough.

---

### P10: Recombine Z Elevator Bracket

| | |
|---|---|
| **File** | `cad/recombine/recombine.step` (elevator frame section) |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.2 mm |
| **Infill** | 35% gyroid |
| **Estimated weight** | ~25 g |
| **Estimated time** | ~2 hr |

**Print orientation:** Print with the back face (motor mount side) on the build plate. The vertical guide channels grow upward.

**Supports:** May need support inside the travel channel ceiling. Use breakaway.

**Critical dimensions:**
- LM8UU bearing bores: should press-fit the 15 mm OD linear bearings. Print at 15.1 mm and ream if needed.
- Travel channel: must allow smooth vertical motion of the pusher carriage.

**Post-processing:**
1. Ream linear bearing bores. Press-fit LM8UU bearings.
2. Test vertical slide motion with the 8 mm rods installed.

---

### P11: Recombine Motor Mount Bracket (X axis)

| | |
|---|---|
| **File** | `cad/recombine/recombine.step` (motor mount section) |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.2 mm |
| **Infill** | 40% gyroid |
| **Estimated weight** | ~30 g |
| **Estimated time** | ~2 hr |

Same print approach as the selector motor mount (P5). Print with base flange down, motor face vertical. Check NEMA17 bolt pattern and pilot recess.

---

### P12: Recombine Z Motor Mount

| | |
|---|---|
| **File** | `cad/recombine/recombine.step` (Z motor bracket section) |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.2 mm |
| **Infill** | 30% gyroid |
| **Estimated weight** | ~20 g |
| **Estimated time** | ~1.5 hr |

**Print orientation:** Print flat, mounting face down.

**Critical dimensions:**
- 28BYJ-48 mounting tab holes: 35 mm spacing, 4.2 mm diameter (M4 clearance).
- Shaft bore: 28.2 mm diameter.

---

### P13: Output Tray

| | |
|---|---|
| **File** | `cad/output/output.step` |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.2 mm |
| **Infill** | 20% gyroid |
| **Estimated weight** | ~80 g |
| **Estimated time** | ~4 hr |

**Print orientation:** Print with the tray floor on the build plate, open top facing up. The side walls and rear wall grow vertically. The open front naturally faces one side.

**Supports:** None needed. The funnel chamfer at the top is a 3 mm overhang at 45 degrees, which prints fine. The spring pocket bores in the rear wall are horizontal cylinders -- if your printer handles small horizontal bores cleanly, no support needed. Otherwise, add painted support inside the spring bores only.

**Critical dimensions to check:**
- Pocket width: 66.5 mm (card width + 2 x 1.5 mm clearance). Generous.
- Pocket depth: 90.4 mm.
- Spring bore diameter: 6.0 mm, 12 mm deep. Test-fit the compression springs.
- M3 heat-set insert bores on the base: 3.2 mm, 4 positions.

**Post-processing:**
1. Sand interior pocket walls (320-grit) for smooth card handling.
2. Install 4 M3 heat-set inserts on the base.
3. Test-fit a deck of cards. The deck should drop in easily and sit square.

---

### P14: Electronics Bay / Tray

| | |
|---|---|
| **File** | (Designed to fit the chassis electronics bay recess) |
| **Material** | PETG |
| **Quantity** | 1 |
| **Layer height** | 0.2 mm |
| **Infill** | 20% gyroid |
| **Estimated weight** | ~40 g |
| **Estimated time** | ~2.5 hr |

**Print orientation:** Print flat, mounting face down.

**Supports:** None.

**Critical dimensions:**
- ESP32 standoff pattern: 44 x 22 mm hole spacing, M3.
- TMC2209 standoff pattern: 14 x 10 mm per board, 22 mm pitch between 4 boards.
- Ventilation slots: verify they are open (not bridged over).

**Post-processing:**
1. Install M3 heat-set inserts for each standoff position (4 for ESP32, 8 for TMC2209 boards, plus buck converter mounting).

---

### P16: Enclosure Panels (optional for V1)

| | |
|---|---|
| **Material** | PETG |
| **Quantity** | 4-6 panels |
| **Layer height** | 0.2 mm |
| **Infill** | 15% gyroid (cosmetic, not structural) |
| **Estimated weight** | ~180 g total |
| **Estimated time** | ~2-3 hr per panel |

These are optional for V1. Print them last, after the machine is working. Print flat, exterior face down for best surface finish.

---

### P19: Sensor Mount Clips

| | |
|---|---|
| **Material** | PETG |
| **Quantity** | 6 |
| **Layer height** | 0.2 mm |
| **Infill** | 30% gyroid |
| **Estimated weight** | ~2 g each |
| **Estimated time** | ~15 min each (batch all 6 on one plate, ~1 hr total) |

**Print orientation:** Print flat. These are small parts -- batch all 6 on one plate.

**Critical dimensions:**
- TCRT5000 module pocket: verify the sensor board snaps in or sits flat.
- M3 clearance hole for chassis/module mounting.

---

### P20: Belt Tensioner Blocks

| | |
|---|---|
| **Material** | PETG |
| **Quantity** | 2 |
| **Layer height** | 0.2 mm |
| **Infill** | 40% gyroid |
| **Estimated weight** | ~5 g each |
| **Estimated time** | ~20 min each |

Print flat. Check the spring bore and idler bolt hole dimensions.

---

### P21: Cable Clips / Guides

| | |
|---|---|
| **Material** | PETG |
| **Quantity** | 6 |
| **Layer height** | 0.2 mm |
| **Infill** | 20% gyroid |
| **Estimated weight** | ~1.3 g each |
| **Estimated time** | ~10 min each (batch all 6) |

Print flat. No critical dimensions. Snap-fit tabs should flex without cracking -- if they crack, your PETG is too brittle (try drying filament or raising nozzle temp).

---

## TPU Parts

Switch to these slicer settings for TPU 95A:

| Setting | Value |
|---------|-------|
| Material | TPU 95A (NinjaTek NinjaFlex, eSUN, or Sainsmart) |
| Nozzle temp | 225 C |
| Bed temp | 50 C |
| Print speed | 25 mm/s (all moves) |
| Retraction | Minimal (1-2 mm direct drive) or disabled (Bowden) |
| Infill | 100% (these are small, solid parts) |
| Layer height | 0.2 mm |

### P17: Feeder Roller Sleeve (TPU)

| | |
|---|---|
| **Material** | TPU 95A |
| **Quantity** | 1 (print 2 spares -- wear part) |
| **Estimated weight** | ~5 g |
| **Estimated time** | ~30 min |

**Print orientation:** Print standing upright (sleeve bore vertical). This gives the best bore roundness for press-fitting onto the PETG roller.

**Critical dimensions:**
- Inner bore: must press-fit over the PETG roller OD (20.0 mm). Print the bore at 19.6-19.8 mm so the TPU stretches onto the roller.
- Outer surface: this is the card-contact surface. It must be smooth and concentric.

**Post-processing:** None. The slight layer texture actually helps grip the card surface.

### P18: Output Tray Bumpers (TPU)

| | |
|---|---|
| **Material** | TPU 95A |
| **Quantity** | 2 |
| **Estimated weight** | ~1.5 g each |
| **Estimated time** | ~15 min each |

Print flat. These are simple pads that press-fit or glue into the output tray. No critical dimensions.

---

## Print Order Recommendation

Print in this order to allow early assembly and testing while later parts are still printing:

1. **Chassis sections** (P15) -- print all 3 first, they take the longest total time and everything mounts to them.
2. **Bin bank sections** (P7) -- second longest print. Start while you are post-processing the chassis.
3. **Feeder hopper** (P1) -- the most complex single print. Allocate time for support removal and bore reaming.
4. **Feeder roller** (P2) and **retard pad holder** (P3) -- quick prints, needed with the feeder.
5. **Selector carriage** (P4), **motor mount** (P5), **idler bracket** (P6) -- medium prints.
6. **Recombine parts** (P8-P12) -- multiple parts but none are very large.
7. **Output tray** (P13) -- straightforward print.
8. **Electronics bay** (P14), **sensor clips** (P19), **cable clips** (P21), **belt tensioners** (P20) -- small parts, batch-print.
9. **TPU parts** (P17, P18) -- print last since they require a filament change and slower speeds.
10. **Enclosure panels** (P16) -- optional, print after the machine is working.

---

## Total Print Estimates

| | |
|---|---|
| **Total PETG** | ~1,200 g (buy 2 kg to have margin for reprints) |
| **Total TPU** | ~8 g (you will need a full spool regardless) |
| **Total print time** | ~55-70 hours (varies by printer speed) |
| **Heat-set inserts consumed** | ~50 (buy 100 for margin) |

---

## Common Problems and Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| Bearing won't press into bore | Bore printed too small | Ream with correct-size drill bit. For 625ZZ, use 16 mm. |
| Heat-set insert goes in crooked | Bore printed with horizontal staircase | Print insert bores with bore axis vertical. If horizontal bore is unavoidable, oversize by 0.1 mm and use the soldering iron slowly. |
| Bin bank section warps after removal | PETG stress relief, thin floor | Let parts cool on the bed fully. If warped, anneal at 80 C or clamp flat. |
| Card catches on layer lines inside bin | Rough interior walls | Sand with 320-grit. For persistent issues, print outer walls only (no inner perimeter gap) or use "ironing" on top surfaces that cards contact. |
| Chassis sections don't align at joints | Dowel pin bores off-center | Ream bores slightly oversized (4.2 to 4.3 mm) and accept the minor play, or reprint. |
| Belt clamp doesn't grip GT2 belt | Slot too wide or smooth | Print a thin serrated insert for the clamp slot, or add a drop of CA glue to the belt-contact surface inside the clamp. |
