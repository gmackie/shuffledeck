# Datum and Tolerance Budget — Single-Deck Card Shuffler

Date: 2026-04-12
Status: Draft

## Overview

This document defines the datum scheme, interface tolerance stackups, and critical dimensions for the single-deck automatic card shuffler. The goal is to identify where tolerance accumulation eats into functional clearance so that adjustability is designed into the right places before CAD freeze.

All dimensions reference `cad/constants.py`. Card nominal: 63.5 x 88.9 x 0.3 mm (poker). Print material: PETG. Default print tolerance: +/-0.2 mm. Tight print tolerance: +/-0.1 mm.

---

## 1. Datum Scheme

Three orthogonal datums define the machine coordinate system. Every module registers to this chain.

### Primary Datums

| Datum | Feature | Description |
|-------|---------|-------------|
| **A** (Z reference) | Chassis base plate, top surface | Flat plane the entire machine sits on. All vertical dimensions reference upward from here. Printed flat on the build plate — best surface accuracy. |
| **B** (Y reference) | Left side rail, inner face | A continuous wall or rail running the full card-travel direction. The "operator side" datum. All lateral (card-width) dimensions reference inward from here. |
| **C** (X reference) | Feeder-end stop, inner face | A single transverse wall at the feeder end of the chassis. All longitudinal (card-travel) dimensions reference forward from here. |

### Module Registration

Each module bolts to the chassis and locates against the datum chain:

| Module | Registers to | Location method |
|--------|-------------|-----------------|
| Feeder | A + B + C | Bolt-down to base plate (A). Side rail contact (B). End stop contact (C). |
| Selector | A + B | Bolt-down to base plate (A). Side rail contact (B). Longitudinal position set by feeder exit — slotted holes allow +/-2 mm X adjustment. |
| Bin bank | A + B | Bolt-down to base plate (A). Side rail contact (B). X position set by selector gate range — slotted holes allow +/-2 mm X adjustment. |
| Recombine | A + B | Bolt-down to base plate (A). Side rail contact (B). X position adjustable. |
| Output tray | A + B | Bolt-down to base plate (A). Side rail contact (B). X position adjustable. |

**Key principle:** Datum B (side rail) is the card-width alignment reference for the entire machine. Every card guide, bin wall, and funnel references its "left" edge off B. This means lateral tolerance stacks are always one-sided — they accumulate from B toward the right, never from both sides toward center.

---

## 2. Interface Tolerance Stackups

For each critical interface, the tolerance chain is calculated worst-case (all contributors add). The available clearance is the designed gap that must absorb the total stack.

### Constants used in calculations

| Symbol | Value | Source |
|--------|-------|--------|
| Card width | 63.5 mm | constants.py |
| Card height | 88.9 mm | constants.py |
| Card thickness | 0.3 mm | constants.py |
| Bin internal width | 65.5 mm (1.0 mm clearance per side) | constants.py |
| Bin internal depth | 90.9 mm (1.0 mm clearance per side) | constants.py |
| Bin entry funnel chamfer | 3.0 mm at 45 deg | constants.py |
| Print tol default | +/-0.2 mm | constants.py |
| Print tol tight | +/-0.1 mm | constants.py |
| Card warp (new deck, V1 envelope) | up to 0.5 mm bow across width | Empirical, new KEM/Bee |
| PETG thermal expansion | ~60 um/m/degC, negligible at room temp deltas of +/-10C over 500 mm span = +/-0.3 mm | Material property |

---

### Interface 1: Feeder Exit Throat --> Selector Entry

**What happens here:** A single card exits the friction roller / retard pad nip and enters a guided path toward the selector gate. The card is moving at ~120 mm/s. Misalignment causes skew, nose-dive, or jam.

**Critical axis:** Card width (lateral, Y). Card must be centered in the guide channel.

| # | Contributor | Nominal | Tolerance | Notes |
|---|------------|---------|-----------|-------|
| 1 | Feeder exit guide width (printed) | 65.5 mm | +/-0.2 mm | Two walls, each +/-0.2 mm, but both ref from Datum B so only right wall floats |
| 2 | Selector entry guide width (printed) | 65.5 mm | +/-0.2 mm | Same datum chain |
| 3 | Feeder-to-selector lateral alignment (assembly) | 0 mm offset | +/-0.3 mm | Two separate printed parts bolted to chassis; each locates off Datum B with bolt clearance |
| 4 | Card width variation | 63.5 mm | +/-0.25 mm | Manufacturing tolerance on poker cards |
| 5 | Card warp (bow across width) | 0 mm | up to 0.5 mm | Effective width increase from bow |

**Nominal clearance:** Guide width - card width = 65.5 - 63.5 = 2.0 mm total (1.0 mm per side).

**Worst-case stack (card too wide for gap):**
- Guide narrows by: 0.2 (feeder wall) + 0.2 (selector wall) + 0.3 (misalignment) = 0.7 mm
- Card widens by: 0.25 (card tolerance) + 0.5 (warp) = 0.75 mm
- Total stack consuming clearance: 0.7 + 0.75 = **1.45 mm**

**Available clearance: 2.0 mm. Margin: 0.55 mm.** PASS — but only 0.55 mm margin at worst case.

**Vertical (Z) concern:** The card must transfer from the feeder's lower guide surface to the selector's lower guide surface without a step. Both surfaces reference Datum A (base plate).

| # | Contributor | Tolerance |
|---|------------|-----------|
| 1 | Feeder guide surface height (from A) | +/-0.2 mm |
| 2 | Selector guide surface height (from A) | +/-0.2 mm |
| 3 | Assembly seating on base plate | +/-0.1 mm |

**Worst-case step: 0.5 mm.** A 0.5 mm downward step will catch card leading edges. A 0.5 mm upward step forces a ramp. Either causes jams at 120 mm/s.

**FLAG: This interface needs a lead-in chamfer or ramp at the selector entry (minimum 1 mm tall, 3 mm long, 18-deg slope) to handle the worst-case step. Alternatively, make the feeder and selector a single printed part to eliminate contributors 1-3.**

---

### Interface 2: Selector --> Bin Entry Funnels

**What happens here:** The selector gate positions over one of 8 bins, and the card drops by gravity into the bin. The card must clear the funnel opening despite selector positional error.

**Critical axis:** Lateral (Y) position of card drop relative to bin center.

| # | Contributor | Nominal | Tolerance | Notes |
|---|------------|---------|-----------|-------|
| 1 | Selector gate position (stepper repeatability) | Bin center | +/-0.1 mm | NEMA17 + microstepping, conservative |
| 2 | Selector rail/bearing play | 0 | +/-0.15 mm | Linear rail or printed slide |
| 3 | Bin bank lateral position (assembly to Datum B) | Per design | +/-0.3 mm | Bolted to chassis |
| 4 | Bin wall print tolerance | Per design | +/-0.2 mm | Each bin wall position |
| 5 | Card lateral drift during drop | 0 | +/-1.0 mm | Gravity drop with air resistance, card curl; ~20-40 mm drop height |
| 6 | Card warp (width effective increase) | 0 | +0.5 mm | Bow makes card wider |

**Available clearance:** Bin internal width = 65.5 mm. Card width = 63.5 mm. Per-side clearance = 1.0 mm. Funnel chamfer adds 3.0 mm effective catch zone at top (so entry opening is ~71.5 mm at the top lip).

**Worst-case offset from center of bin:**
0.1 + 0.15 + 0.3 + 0.2 + 1.0 = **1.75 mm lateral offset**

Plus card effective half-width increase from warp: 0.25 mm per side.

**Total: card edge can be 2.0 mm off from nominal position.**

Against funnel entry half-width of (71.5 - 63.5) / 2 = **4.0 mm.** PASS with 2.0 mm margin at the funnel lip.

Against bin internal half-clearance of 1.0 mm once past the funnel: the card must settle before contacting the straight walls. The 3.0 mm chamfer at 45 degrees provides a centering ramp.

**FLAG: Card lateral drift during drop (contributor 5) dominates this stack. If drop height exceeds ~40 mm, increase funnel chamfer from 3.0 mm to 5.0 mm. Consider adding guide fingers or a short chute below the selector gate to reduce free-fall distance.**

**Depth (X) axis:** Bin internal depth = 90.9 mm vs card height 88.9 mm = 1.0 mm per side. Same funnel chamfer applies. Similar analysis: PASS with the funnel, but the depth clearance is tight once the card is inside the bin.

---

### Interface 3: Bin Bank --> Recombine Pickup

**What happens here:** The recombine module must grab a partial stack of 1-10 cards from a bin and transfer it to a temporary assembly area. The stack could be as thin as 0.3 mm (1 card) or as thick as 3.0 mm (10 cards). Cards may be slightly misaligned within the bin.

**Critical dimensions:**

| # | Contributor | Value/Tolerance | Notes |
|---|------------|----------------|-------|
| 1 | Stack height variation | 0.3 - 3.0 mm | 1-10 cards at 0.3 mm each |
| 2 | Card misalignment within bin | +/-1.0 mm lateral | Cards settle imperfectly against bin walls |
| 3 | Bin floor height (from Datum A) | Nominal +/-0.3 mm | Print tolerance + assembly |
| 4 | Recombine pickup Z position (from Datum A) | Nominal +/-0.3 mm | Print tolerance + assembly |
| 5 | Recombine pickup lateral alignment to bin | Nominal +/-0.5 mm | Two separate assemblies, each referenced to B |

**The core problem:** The pickup mechanism must:
- Enter the bin without colliding with bin walls (needs ~0.5 mm clearance on each side)
- Contact the top card of a stack whose height varies by 10:1
- Grip the partial stack without disturbing the stack below (no telescoping)
- Extract vertically or laterally without snagging

**Worst-case Z mismatch:** Bin floor and pickup reference both have +/-0.3 mm from Datum A. Combined: +/-0.6 mm. For a 1-card stack (0.3 mm thick), the pickup could miss entirely.

**FLAG: This is the highest-risk interface in the machine. A fixed-height pickup cannot work. Requirements:**
1. **Compliant or sensor-guided Z approach** — the pickup must find the top of the stack, not go to a fixed Z coordinate. Spring-loaded fingers, a contact switch, or a beam sensor to detect stack-top height.
2. **Lateral clearance is very tight.** Bin internal width = 65.5 mm. Pickup mechanism + its travel clearance must fit in ~63.5 mm or less to avoid bin wall contact. This leaves essentially zero margin for mechanisms wider than the card.
3. **Consider bottom extraction** (pushing stack up from below through a slot in the bin floor) instead of top pickup. This eliminates the stack-height-finding problem entirely — you always push from a known datum (the floor).

---

### Interface 4: Recombine --> Feeder Input (Pass 2 Reload)

**What happens here:** After pass 1, the recombined 52-card stack is transferred back into the feeder hopper for pass 2. The stack must enter the hopper, settle against the backstop, and be singulatable without manual intervention.

| # | Contributor | Value/Tolerance | Notes |
|---|------------|----------------|-------|
| 1 | Recombine output stack squareness | +/-1.5 mm skew across stack | Accumulated from multiple bin pickups |
| 2 | Recombine output height above hopper | Variable | Transport path dependent |
| 3 | Hopper side rail width | 65.5 mm +/-0.2 mm | Printed, references Datum B |
| 4 | Stack effective width (52 cards, some skew) | 63.5 mm + 1.5 mm skew = 65.0 mm | Worst case |
| 5 | Hopper backstop position | Nominal +/-0.3 mm | Print + assembly |

**Nominal clearance:** Hopper width (65.5 mm) - card width (63.5 mm) = 2.0 mm.

**Worst-case stack width with skew:** 65.0 mm in a 65.1 mm hopper (worst-case narrow). **Margin: 0.1 mm.** FAIL at worst case — skewed stack will wedge in the hopper.

**FLAG: This interface requires a squaring step before reload.** Options:
1. **Vibration jogger** — momentary vibration motor to settle the stack square before inserting into hopper. Simple, no moving parts besides the motor.
2. **Side-tap plate** — a spring-loaded plate that taps the long edge of the stack to register it against a datum wall before transfer.
3. **Wider hopper with active alignment** — increase hopper clearance to 3.0 mm per side (69.5 mm internal) and add a closing guide that narrows during feed.

The recombine-to-hopper transfer is also the only interface where the full 52-card stack moves as a unit. Stack height at this point: ~15.6 mm nominal, up to 17.0 mm with air gaps. The transport mechanism must handle a 17 mm tall, potentially skewed stack without dropping or collapsing it.

---

### Interface 5: Recombine --> Output Tray (Final Delivery)

**What happens here:** After pass 2, the final recombined deck is delivered to the output tray. Same stack-squareness concern as Interface 4, but the output tray can be more forgiving because the stack does not need to be singulatable — it just needs to be presentable.

| # | Contributor | Value/Tolerance | Notes |
|---|------------|----------------|-------|
| 1 | Stack squareness after pass 2 recombine | +/-1.5 mm | Same as Interface 4 |
| 2 | Output tray width | Designed for generous clearance | Target 69-70 mm internal |
| 3 | Output tray depth | Designed for generous clearance | Target 93-95 mm internal |
| 4 | Drop height into tray | Minimize | Free-fall skews the stack |

**Recommendation:** Size the output tray at 70 x 94 mm internal (3.25 mm clearance per side on width, 2.55 mm per side on depth). This is generous enough that worst-case skew and print tolerance will not cause the stack to wedge. Add slight taper to all four walls (2-3 deg draft) so the stack self-centers as it settles.

**This interface is LOW RISK provided the tray is sized generously.** The squaring step before Interface 4 (pass 2 reload) is the one that matters.

---

## 3. Critical Dimensions Table

Every dimension that matters at a module interface, its nominal value, tolerance, and datum reference.

### Feeder Module

| Dimension | Nominal (mm) | Tolerance (mm) | Datum | Notes |
|-----------|-------------|----------------|-------|-------|
| Exit throat width | 65.5 | +/-0.2 | B | Card width + 2 x 1.0 clearance |
| Exit throat height (gap) | 0.35 | +/-0.05 | A | Single card must pass, double must not |
| Roller center height above base | TBD | +/-0.1 | A | Tight — drives nip geometry |
| Retard pad contact line height | TBD | +/-0.1 | A | Must match roller center +/- 0.1 |
| Hopper side rail spacing | 65.5 | +/-0.2 | B | Same as throat |
| Hopper floor inclination angle | ~30 deg | +/-2 deg | A | Gravity feed angle |
| Backstop position from throat | ~95 | +/-0.5 | C | Card height + clearance |

### Selector Module

| Dimension | Nominal (mm) | Tolerance (mm) | Datum | Notes |
|-----------|-------------|----------------|-------|-------|
| Entry guide width | 65.5 | +/-0.2 | B | Must match feeder exit |
| Gate travel range | Spans 8 bins | +/-0.1 per position | B | Stepper positioning |
| Gate-to-bin-top gap (Z) | 2-5 | +/-0.5 | A | Drop height, minimize |
| Entry guide height above base | Same as feeder exit | +/-0.2 | A | Step must be < 0.5 mm |

### Bin Bank

| Dimension | Nominal (mm) | Tolerance (mm) | Datum | Notes |
|-----------|-------------|----------------|-------|-------|
| Bin internal width | 65.5 | +/-0.2 | B | Per constants.py |
| Bin internal depth | 90.9 | +/-0.2 | B, C | Per constants.py |
| Bin internal height | 20.0 | +/-0.3 | A | Room for 10 cards + extraction |
| Bin wall thickness | 2.0 | +/-0.2 | -- | Structural |
| Bin spacing (gap between bins) | 2.0 | +/-0.2 | B | Selector access |
| Bin entry funnel chamfer | 3.0 | +/-0.3 | -- | 45-deg lead-in |
| Bin floor height above base | TBD | +/-0.2 | A | Critical for recombine pickup |
| Bin pitch (center-to-center) | 69.5 | +/-0.3 | B | 65.5 + 2x2.0 wall + 2.0 spacing... see note |

**Note on bin pitch:** Bin pitch = bin internal width (65.5) + wall (2.0) + spacing (2.0) + wall (2.0) = 71.5? No — adjacent bins share a wall. Pitch = internal width (65.5) + one wall thickness (2.0) + spacing (2.0) = 69.5 mm. Over 8 bins the total bank width = 8 x 65.5 + 9 x 2.0 (walls) + 7 x 2.0 (spacings) = 524 + 18 + 14 = 556 mm. This is large. Tolerance accumulation over 556 mm at 0.2 mm per feature could reach several mm at the far end.

**FLAG: Bin bank should be printed as one piece (or two halves that register to each other via alignment pins) to avoid inter-bin tolerance accumulation from separate assembly. If printing as one piece exceeds bed size (~250 mm typical), split into two 4-bin halves with a kinematic pin joint.**

Actually, recalculating: if each bin shares walls with its neighbor, then pitch = internal width + shared wall + gap = 65.5 + 2.0 + 2.0 = 69.5 mm. Total bank width = 8 x 69.5 - 2.0 (last gap not needed) + 2.0 (outer wall at each end) = 556 + 2 = 558 mm. This does not fit on any common print bed as one piece. **Two 4-bin halves at ~280 mm each, or four 2-bin quarters at ~141 mm each.**

### Recombine Module

| Dimension | Nominal (mm) | Tolerance (mm) | Datum | Notes |
|-----------|-------------|----------------|-------|-------|
| Pickup mechanism width | < 63.5 | +/-0.2 | B | Must fit inside bin |
| Pickup Z travel | 0 to 20.0 | +/-0.1 | A | Must reach bin floor |
| Pickup lateral alignment to bin | 0 offset | +/-0.5 | B | Combined assembly tolerance |
| Stack assembly area width | 67.0 | +/-0.3 | B | Wider than card to allow stack building |

### Output Tray

| Dimension | Nominal (mm) | Tolerance (mm) | Datum | Notes |
|-----------|-------------|----------------|-------|-------|
| Tray internal width | 70.0 | +/-0.3 | B | Generous |
| Tray internal depth | 94.0 | +/-0.3 | B, C | Generous |
| Tray internal height | 25.0 | +/-0.5 | A | Full deck + margin |
| Wall draft angle | 2-3 deg | +/-1 deg | -- | Self-centering |

---

## 4. Print-Specific Considerations

### PETG Shrinkage

PETG shrinks approximately 0.4-0.6% during cooling. On a 65.5 mm bin width, that is 0.26-0.39 mm. Most slicers compensate for this, but compensation is never perfect.

**Recommendation:** Design to nominal dimensions and tune with test prints. For critical fits (bearing bores, shaft holes), print a test coupon first and measure actual shrinkage on your printer/filament combination. Apply a per-printer correction factor in `constants.py` rather than baking a shrinkage guess into CAD dimensions.

### Layer Height Effects

Vertical dimensions are quantized to the layer height (0.2 mm per constants.py). Any vertical dimension that is not a multiple of 0.2 mm will be rounded by the slicer.

**Affected critical dimensions:**
- Feeder throat gap (0.35 mm nominal) — will print as either 0.2 mm (too tight) or 0.4 mm (acceptable). **Design to 0.4 mm and tune with shims or retard pad adjustment.**
- Bin floor thickness (1.5 mm) — not a problem, 1.5 / 0.2 = 7.5 layers, slicer rounds to 8 = 1.6 mm. Acceptable.
- Bin entry funnel chamfer — printed as staircase steps. The 45-deg chamfer will have 0.2 mm steps. At 3.0 mm chamfer height, that is 15 steps. Adequate for card sliding but consider sanding or printing at 0.12 mm layer height for the funnel region.

### First-Layer Elephant Foot

The first layer is typically over-extruded by 0.1-0.2 mm (elephant foot). This affects:
- **Bin internal dimensions at the floor:** The first few layers of bin walls will be 0.1-0.2 mm thicker, reducing internal width by 0.2-0.4 mm at the bottom. For a bin, this is a self-clearing problem since cards stack from the bottom and push past it. But for the feeder throat where the bottom surface IS the critical surface, elephant foot must be addressed.
- **Module base surfaces that sit on the chassis plate:** Elephant foot on the contact surface creates a slight convexity. Not a problem for bolt-down registration since the bolt clamp force flattens it.

**Mitigation:** Enable elephant foot compensation in slicer (typically -0.1 to -0.2 mm first layer horizontal expansion). For the feeder throat specifically, print throat-side-down so the critical gap dimension is defined by the top surface of the print, not the first layer.

### Bearing Bore Tolerances

608 bearings (8 mm ID, 22 mm OD, 7 mm wide) are called out in the design. Printed bores for press-fit bearings:

- **Bore diameter:** Print at 22.0 + 0.1 mm = 22.1 mm (tight fit per PRINT_TOL_TIGHT). Test fit; ream with a drill bit if too tight.
- **Bore roundness:** Printed bores are not truly round — they are polygonal approximations. A bore at 0.2 mm layer height with standard faceting will have ~0.05-0.1 mm out-of-round. Acceptable for 608 bearing press-in.
- **Bore depth:** 7.0 mm bearing in a printed pocket. Print pocket at 7.2 mm to allow full seating. The slicer will round 7.2 / 0.2 = 36 layers exactly.

### Heat-Set Insert Bores

Per constants.py: M3 heat-set bore = 3.2 mm, M4 = 4.8 mm. These dimensions already include the slight undersizing needed for the brass insert to melt into the plastic. No additional tolerance adjustment needed, but:
- Print insert bores vertically (bore axis = Z axis) for best roundness.
- If a heat-set insert is in a horizontal bore (bore axis = X or Y), increase bore diameter by 0.1 mm to compensate for layer staircase ovality.

---

## 5. Recommendations

### Where to Use Kinematic Mounts vs Simple Bolt-Down

| Interface | Mounting Method | Rationale |
|-----------|----------------|-----------|
| Feeder to chassis | **Kinematic: 3-point with adjustment** | Highest-risk singulation module. Needs nip height tuning, lateral alignment, and angle adjustment. Use two pins in slotted holes (constrains Y and rotation) plus one bolt (constrains X). Shims under pin seats for Z adjustment. |
| Selector to chassis | **Bolt-down with slotted holes** | Needs X adjustment (longitudinal) to set gap to feeder exit. Y alignment inherits from Datum B rail contact. 2-4 bolts in X-slotted holes. |
| Bin bank to chassis | **Bolt-down, tight, no adjustment** | Once printed correctly, bin positions are internal and self-consistent. Register to Datum B rail. The selector adjusts to the bins, not the other way around. |
| Recombine to chassis | **Kinematic: linear rail or adjustable slide** | Must align precisely to each bin in sequence. Either the recombine module travels on a rail (inherently self-aligning to the bin bank) or it has XY adjustment at its mount point. |
| Output tray to chassis | **Simple bolt-down, loose tolerance** | Generous internal dimensions make precision unnecessary. Two bolts, done. |

### Where Adjustability is Required

1. **Feeder nip gap** — MUST be adjustable. The gap between the friction roller and the retard pad determines singulation reliability. Use an eccentric cam or a screw-and-locknut arrangement to set the gap, then lock it. Target: 0.30-0.40 mm, adjustable in ~0.05 mm increments.

2. **Feeder-to-selector Z step** — Either eliminate by making them one part, or provide a shim stack (0.1, 0.2, 0.3 mm shims) under the selector to match heights.

3. **Selector home/zero position** — Software-adjustable (homing sensor + offset in firmware). Physical endstop must be repeatable to +/-0.1 mm. Use a microswitch with a precision flag, not a printed bump.

4. **Recombine pickup Z zero** — Must be calibrated per-build. Either a contact sensor on the pickup mechanism, or a firmware-stored offset calibrated during assembly.

### Where Tight Tolerance is Justified

- **Feeder throat gap:** +/-0.05 mm. This is the singulation gate. Worth printing test coupons and selecting.
- **Roller and retard pad contact geometry:** +/-0.1 mm. Drives nip force consistency.
- **Selector stepper position repeatability:** +/-0.1 mm. Determines correct bin selection.
- **Bearing bores:** +/-0.1 mm. Standard for press-fit.

### Where Loose Tolerance is Fine

- **Bin internal dimensions:** +/-0.3 mm. The 1.0 mm per-side clearance is ample.
- **Output tray dimensions:** +/-0.5 mm. Oversized by design.
- **Electronics bay dimensions:** +/-1.0 mm. Nothing critical.
- **Chassis overall dimensions:** +/-1.0 mm. Cosmetic only.
- **Fastener clearance holes:** Already oversized per constants.py (M3 clearance = 3.4 mm for 3.0 mm bolt).

### Summary of Flagged Interfaces

| Interface | Risk | Action Required |
|-----------|------|-----------------|
| Feeder exit --> selector entry (Z step) | **HIGH** | Add lead-in chamfer/ramp at selector entry, or combine into one printed part |
| Selector --> bin entry (lateral drift) | **MEDIUM** | Increase funnel chamfer to 5 mm if drop height > 40 mm; add guide chute |
| Bin bank --> recombine pickup | **CRITICAL** | Fixed-height pickup will not work. Needs compliant/sensor-guided Z, or switch to bottom-push extraction |
| Recombine --> feeder pass 2 reload | **HIGH** | Stack squareness eats all clearance. Requires squaring step (jogger or tap plate) before reload |
| Recombine --> output tray | **LOW** | Size tray generously, add wall draft. No special measures needed |

### Bin Bank Printing Strategy

The full 8-bin bank at ~558 mm wide will not fit on a single print bed. Options:

1. **Two 4-bin halves (~280 mm each):** Fits large-format printers (Bambu X1 at 256 mm is close; Prusa XL at 360 mm fits). Join with alignment dowel pins (2x M4 pins) and bolts. Tolerance at the joint: +/-0.3 mm, absorbed by the 2.0 mm inter-bin spacing.

2. **Four 2-bin quarters (~141 mm each):** Fits any printer. More joints = more accumulated tolerance. Each joint adds +/-0.3 mm. Over 3 joints: +/-0.9 mm worst case from first bin to last. The selector must be calibrated to actual bin positions, not nominal.

3. **Individual bins bolted to a common rail:** Maximum flexibility but worst tolerance accumulation. Only use if bin count may change (e.g., testing 6 vs 8 vs 10 bins during development).

**Recommendation for V1:** Option 2 (four 2-bin quarters) for printer compatibility, with the selector homed and calibrated to measured bin positions stored in firmware. This decouples print accuracy from bin-selection accuracy.
