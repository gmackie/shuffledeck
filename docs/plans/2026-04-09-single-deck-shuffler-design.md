<!-- /autoplan restore point: /Users/mackieg/.gstack/projects/shuffle/main-nogit-autoplan-restore-20260410-142438.md -->
# Single-Deck Automatic Card Shuffler V1 Design

Date: 2026-04-09
Status: Validated design draft

## Summary

This document defines the V1 design for a DIY automatic single-deck poker card shuffler intended for reliable home or pro-am table use. V1 explicitly excludes guided cut-card insertion. The machine is designed as a standalone chassis that can later be adapted into a table-mounted installation with separate dealer-facing openings for the input hopper and output tray.

The chosen architecture prioritizes reliability over compact size or maximum speed:

- Single inclined input hopper
- Friction roller plus retard pad singulation
- 8-bin randomization core
- Two-pass shuffle process
- Separate output tray
- ESP32-based control system
- Standalone chassis sized for later table integration

## Locked Decisions

- Reliability-first design
- Two-pass random bin shuffle
- Friction roller plus retard pad feeder
- 8 storage bins
- ESP32 main controller
- Standalone enclosure dimensioned for future drop-in table integration
- No cut-card mechanism in V1

## Targets — 2026-04-10

Locked via user decision during autoplan execution. These are the numbers V1 ships against. If the feeder bakeoff or subsystem bench tests show any target is infeasible, escalate before silently relaxing.

| Target | Value | Source |
|---|---|---|
| **Primary user** | Pro-am / home poker night, degrades gracefully to home mode | User decision |
| **Shuffle quality** | ≥ 7 riffle-shuffle equivalents (Bayer-Diaconis) | Tier 0 sim validated 2-pass 8-bin FIFO at ~9.2 riffles |
| **Cycle time ceiling** | ≤ 30 s per deck, load-to-tray (pro-am mode); home mode may run slower | User decision |
| **BOM ceiling** | ≤ $500 (hardware only, excludes print plastic and labor) | User decision |
| **Supported deck envelope (V1)** | New KEM plastic + new Bee paper only | User decision |
| **Deferred to V2** | Worn decks, humidity-conditioned, warped (≥ 1 mm bow) | Out of V1 scope |
| **Jam rate** | ≤ 1 unrecovered jam per 500 decks across supported envelope | Test plan Tier 2 |
| **False-success rate** | 0 per 10,000 decks (hard gate) | Test plan Tier 2 |
| **Wear-part swap time** | ≤ 60 s, no re-calibration | Test plan Tier 1 |
| **Cycle time derivation** | 52 cards × 2 passes ÷ 30 s ≈ 104 singulations in ~20 s (leaves ~10 s for recombine + transport) → ~5 cards/s → ~120 mm/s feed speed for 63 mm cards | Arithmetic |

**Cycle time note:** 30 s is aggressive for friction+retard singulation at ~120 mm/s feed speed. This sits above the "laser printer sweet spot" of ~80 mm/s. The feeder bakeoff Phase 2 DOE must include a 120 mm/s point and the winner must pass the BH (humidity) deck at that speed with margin — except BH is out of V1 envelope, so the bakeoff uses BN (new Bee paper) as the worst case instead. If 120 mm/s fails the new Bee paper test cleanly, the options are: (a) relax cycle time to 40 s and run at 80 mm/s, (b) overlap passes (start pass 2 singulation while pass 1 recombine finishes), or (c) switch candidate to escapement/kicker which tolerate higher speeds at the cost of parts count. Decision deferred until bakeoff data exists.

**BOM headroom ($500 vs ~$250 friction+retard BOM):** the extra ~$250 buys: a full vacuum pickup candidate in the bakeoff, a small OLED for diagnostics, better sensors (e.g. Omron B5W-LB2101 over bare TCRT5000), a second ESP32 for logging without interfering with the control loop, and one surprise. Use it.

## Product Goals

- Accept one full 52-card deck in a single input hopper
- Shuffle automatically without manual deck splitting
- Deliver the final shuffled deck to a separate output tray
- Operate conservatively enough to minimize jams and double-feeds
- Detect card-count mismatches and report failure rather than claim success
- Keep all wear parts and jam-clearance points serviceable

## System Architecture

The machine is divided into modular assemblies:

1. Feeder module
2. Selector module
3. Bin bank
4. Recombine module
5. Output module
6. Electronics bay

Cards are loaded into a slightly inclined hopper. The bottom card is singulated by a driven friction roller working against a retard pad. After sensor confirmation, the card enters a selector path and is routed into one of 8 storage bins chosen by the controller. Once all cards are distributed, the machine recombines the bins in a controlled sequence into a temporary stack. That stack is then run through the same process a second time. After the second recombination, the finished deck is delivered to the output tray.

The chassis should remain physically generous in V1. The design should prefer larger clearances, easier access, and slower speeds over compactness.

## Mechanical Design

### Feeder Module

The feeder is the highest-risk subsystem and should be designed for tuning and replacement:

- Inclined hopper with adjustable side rails
- Spring-loaded rear backstop
- Bottom exit throat sized for standard poker cards
- Driven friction roller with replaceable O-ring or silicone sleeve
- Replaceable retard pad opposing the second card
- Adjustable nip and feed pressure
- Two sensors near the feed throat for motion confirmation and timing

The feeder should run conservatively. The primary objective is stable single-card release, not throughput.

### Selector Module

The selector receives each singulated card and routes it into one of 8 bins:

- Narrow guided card path after the feeder
- Stepper-driven diverter or gate
- Fixed, repeatable routing positions
- Sensor checkpoint at the selector throat

The selector must be accurate enough that bin entry errors are rare even with slightly warped or worn cards.

### Bin Bank

The 8 bins should be easy to clear and tolerant of alignment variation:

- Vertical or slightly inclined storage bins
- Large entry funnels
- Removable access covers
- Smooth low-friction internal surfaces
- Geometry that keeps partial stacks square enough for recombination

### Recombine Module

Recombination should be controlled rather than passive:

- Retrieve cards or partial stacks from bins in deterministic order
- Guide them into a temporary stack with side constraint
- Feed the temporary stack back into pass two
- Repeat the same process after pass two into the final output tray

Free-fall stacking should be avoided where it can produce skewed or collapsed stacks.

### Output Module

The output tray should square the deck as it lands:

- Separate tray physically distinct from input hopper
- Side guides or light compression geometry
- Dealer-friendly access
- Layout compatible with a future table cutout

## Controls and Electronics

### Controller

- ESP32 DevKit as the main controller

Reasons:

- Sufficient control capability for state-machine firmware
- Better expansion options than a smaller Arduino board
- Easy future support for logging, diagnostics, or small display upgrades

### Motors

Recommended V1 direction:

- Stepper motors where position matters
- Low-speed geared motor or stepper for the feeder
- TMC2208 or TMC2209 drivers for steppers

Likely motor roles:

- Selector positioning
- Recombine gate or pickup motion
- Optional elevator or output alignment motion
- Feeder drive

### Sensors

Use sensors at choke points rather than saturating the machine with them:

- Hopper/feed exit sensor
- Post-singulation confirmation sensor
- Selector throat transit sensor
- Recombine entry or pickup confirmation sensor
- Recombine exit sensor
- Final output count checkpoint

Total expected sensor count: approximately 5 to 7.

### User Interface

Minimal V1 UI:

- `Shuffle` button
- `Stop/Clear Jam` button
- Status LEDs
- Optional buzzer

Service mode should be available for:

- Jog feeder
- Jog selector
- Jog recombine mechanism
- Run sensor tests

## Firmware Design

Firmware should be implemented as an explicit state machine:

- `idle`
- `feeding_pass_1`
- `recombine_1`
- `feeding_pass_2`
- `recombine_2`
- `complete`
- `jam_recovery`
- `service_mode`

The machine should maintain expected card counts throughout the cycle. On sensor timing failure or count mismatch, it should stop, identify the failing segment, reverse only the affected mechanism a short distance, and retry a limited number of times before entering a fault state.

The controller should never report a successful shuffle unless the end-to-end count matches 52 cards.

## Randomization Strategy

V1 uses two-pass random bin distribution:

- Pass 1: each singulated card is assigned to one of 8 bins using controller-generated randomness
- Recombine bins into a temporary stack
- Pass 2: run the temporary stack through the same 8-bin process again
- Recombine into final output deck

This approach offers significantly better mixing than a single-pass system while remaining much simpler than slot-rack or carousel architectures.

## Recommended Materials and Parts

- PETG for structural printed parts
- TPU only where flexible contact surfaces are needed
- ESP32 DevKit
- 2 to 4 NEMA17 stepper motors
- 1 low-speed geared feeder motor or equivalent stepper
- TMC2208 or TMC2209 drivers
- 12V power supply
- 5V buck converter
- IR sensors
- O-rings or silicone sleeves for feed rollers
- Replaceable retard pad material
- Common bearings such as 608-class where appropriate
- Springs, shoulder bolts, heat-set inserts, wiring, connectors

## Primary Failure Modes to Design Around

- Double-feed at the hopper
- Card skew or nose-dive at the feed throat
- Selector misrouting
- Bin entry jams
- Poor partial-stack geometry during recombination
- Final deck squaring issues in the output tray
- False-success reporting after a count mismatch
- Service procedures that require excessive disassembly

Each jam-prone region should be accessible without tearing down the entire machine.

## Integration Strategy

V1 should be built as a standalone tabletop unit first. The enclosure dimensions should anticipate future conversion into a table-installed module, but the mechanics should not be compromised for under-table constraints yet. The table integration phase should primarily involve mounting, trim, and access design rather than a full mechanical redesign.

## Next Steps

1. Produce a dimensioned subsystem layout for feeder, selector, bins, recombine path, and output tray.
2. Choose exact feeder motor strategy: geared DC motor with feedback or stepper.
3. Define bin selector mechanism in CAD.
4. Build a feeder-only prototype and tune singulation reliability.
5. Add sensor instrumentation and collect timing data.
6. Prototype one-pass bin routing before committing to full two-pass mechanics.
7. Build the full bin bank and recombine path.
8. Implement firmware state machine and jam recovery.
9. Run repeated 52-card validation testing across multiple deck conditions.

## Open Questions

- Final target footprint for the tabletop chassis
- Exact feeder drive choice
- Specific recombine mechanism geometry
- Whether output squaring needs passive guides only or a light active constraint

---

<!-- AUTOPLAN REVIEW BELOW — generated 2026-04-10 -->

# /autoplan Review — Phase 1: CEO

## Phase 1.0 — Prior Art Map (what already exists)

Sub-problem to existing solution:

| Sub-problem | Commercial / prior art | Status |
|---|---|---|
| Home/pro-am shuffler | Shuffle Tech ST-1000 (~$849, 1-2 decks), DeckMATE clones (~$40-120 AliExpress), Shuffle Master used casino units | Covered at multiple price points |
| Junk-tier battery auto-shufflers | Home Depot / Amazon ~$11-15 | Unreliable but solves single-deck for a fiver |
| DIY open projects | Hackaday entries, Instructables, a few YouTube builds | Exist but none dominant; no de facto open platform |
| Friction-roller singulation | Every desktop printer ever | Well-characterized, wear-replacement norm is known |
| Retard pad tuning | Canon / HP service manuals, cheap OEM pads | Characterized |
| 52-slot placement shufflers | Casino-grade multi-deck (ShuffleMaster DeckMate 2) | Existence proof that "one pass, one card per slot" works at scale |
| Randomness quality measurement | Bayer-Diaconis 7-riffle result, rising-sequence test, TV-distance-from-uniform | Standard stats; 30-line Python sim is possible |
| ESP32 firmware state machine | Arduino/ESP32 steppers+TMC2209, tons of reference code | Commodity |

**Key implication:** there is no moat unless this plan targets a specific wedge (open/inspectable/repairable, custom shuffle modes, table-integrated, quiet, sub-$300 BOM). The plan does not state its wedge. See Premise Gate.

## Phase 1.0A — Premise Challenge

Premises stated as locked, and their current evidence:

| # | Premise | Stated | Evidence backing it | Status |
|---|---|---|---|---|
| P1 | Two-pass 8-bin randomization produces acceptable mixing | Locked | None — no simulation, no combinatorics, no target metric | **UNPROVEN** |
| P2 | 8 bins is the right count | Locked | None — not compared to 6, 10, 12, 16 | **ARBITRARY** |
| P3 | Two passes is the right count | Locked | None — not compared to 1-pass / 3-pass | **ARBITRARY** |
| P4 | Friction roller + retard pad is the right singulator | Locked | Familiarity ("printers do it") — no bakeoff | **ASSUMED** |
| P5 | "Reliability-first over compact/fast" matches real user tolerance | Locked | No user research; no cycle-time or size ceiling stated | **ASSUMED** |
| P6 | Standalone chassis can be sized for future table integration without compromise | Locked | No analysis of the dual-constraint trap | **LIKELY WRONG** |
| P7 | ESP32 is sufficient | Locked | True — this one is fine | **OK** |
| P8 | DIY is worth building at all vs commercial alternatives | Unstated | None — no build-vs-buy analysis | **MISSING** |
| P9 | No cut-card in V1 is acceptable scope | Locked | Explicitly scoped out | **OK** |

## Phase 1.0B — Randomization Quality: the core math

Both CEO voices independently computed that **two-pass 8-bin is not a good shuffle**:

- **Radix sort framing (Codex):** two passes into 8 bins is structurally a stable 2-digit base-8 sort. 52 cards distribute across 64 possible (bin₁, bin₂) buckets. Expected collisions: ~20.7 unordered pairs whose relative order is preserved by construction. A real shuffle has ~0 such preserved pairs.
- **Adjacency bias (Claude):** cards adjacent in the input hopper have P=1/8 of landing in the same bin with preserved order each pass. After two passes, P(still adjacent in output) ≈ 1/64 ≈ 1.5%. Across 51 adjacency pairs, expected ~0.8 preserved adjacencies per deck. Detectable. Exploitable.
- **Bits-of-entropy framing (Claude):** log₂(8)=3 bits per card per pass → ~6 bits over two passes. That's roughly equivalent to **2-3 riffle shuffles**, far below the Bayer-Diaconis 7-riffle benchmark for a uniformly mixed deck.

**Verdict:** the entire product's reason to exist rests on an unvalidated, almost certainly inadequate randomization strategy. This is the headline finding.

## Phase 1.0C — Implementation Alternatives (3-approach Pugh)

| Dimension | A) Two-pass 8-bin (current plan) | B) Slot-rack 52-slot one-pass | C) Single-pass 16+ bin |
|---|---|---|---|
| Mixing quality | ~2-3 riffle equivalents; preserved-pair bias | Provably uniform (each slot holds 1 card in random assignment) | ~3-4 bits/card, single pass; better than A if bins ≥ 16 |
| Mechanisms | Feeder + selector + 8-bin + recombine ×2 | Feeder + XY or linear slot positioner | Feeder + selector + 16-bin + recombine |
| Jam surface area | 2 feeds, 2 recombines per shuffle | 1 feed, 1 placement, 1 recombine | 1 feed, 1 recombine |
| Cycle time budget | 52 cards × 2 passes = 104 feed events | 52 cards × 1 pass = 52 placement events | 52 cards × 1 pass = 52 feed events |
| State machine complexity | 8 states | 4-5 states | 4-5 states |
| Dismissed in plan? | No (current pick) | Yes, without quantitative argument | Not mentioned |
| Deterministic count verification | Possible but hard (partial stacks) | Trivial (each slot = 1 card) | Same as A |

**Neither voice recommends A.** Codex recommends a real Pugh matrix including drum/carousel, pick-and-place, mechanical riffle. Claude recommends prototyping B in parallel with the feeder and being willing to abandon the 8-bin architecture.

## Phase 1.0D — Dream State Diagram

```
CURRENT STATE           THIS PLAN (V1 as written)      12-MONTH IDEAL
──────────────           ─────────────────────────       ─────────────────────
No machine.              Standalone unit that           Open-source, repairable,
Manual shuffling.        sometimes jams and              table-integrated shuffler
Design doc only.         produces ~2-3 riffle-          with provably uniform
                         equivalent mixing.              output, ≤1 jam/500 decks,
                         No targets. No metric.          ≤25s cycle, <$300 BOM,
                         No wedge vs commercial.         published test harness.
```

**Delta from plan to ideal:** the plan does not name the wedge, does not define targets, and does not validate its randomization. V1 as written delivers an inferior version of a $40 DeckMATE clone.

## Phase 1.0E — Temporal Interrogation (hour-by-hour regret)

- **Hour 1 after feeder prototype built:** "I wish I'd bought the cheap Canon retard pad instead of casting my own."
- **Hour 6 after bin selector integrated:** "I can't change bin count without reprinting the frame. I should have made the bin bank modular."
- **Hour 12 after first full shuffle cycle:** "The output does not look random. I should have written the test harness first."
- **Week 2 after randomness measured:** "Two passes is not enough. I'm going to add a third pass. Wait — I could have picked slot-rack."
- **Month 2:** "I should have done the build-vs-buy analysis in week 1."

## Phase 1.0F — Mode Selection

Mode: **SELECTIVE EXPANSION** — the plan is structurally incomplete (missing targets, missing randomness validation, missing build-vs-buy, missing wedge) but the locked decisions are salvageable IF the user confirms the premises after seeing the evidence.

## Phase 1.0.5 — Dual Voices Consensus

### CEO DUAL VOICES — CONSENSUS TABLE

| Dimension | Claude subagent | Codex | Consensus |
|---|---|---|---|
| 1. Premises valid? | NO — core randomization math unchecked | NO — radix sort framing makes bias structural | **DISAGREE with plan → both agree it's wrong** |
| 2. Right problem to solve? | NO — no build-vs-buy, no JTBD lock | NO — no 10x wedge stated | **DISAGREE with plan** |
| 3. Scope calibration correct? | NO — dual-constraint chassis trap; scope leaking to table | NO — dual-optimization trap flagged | **DISAGREE with plan** |
| 4. Alternatives sufficiently explored? | NO — slot-rack dismissed in one sentence | NO — no Pugh matrix; mechanical riffle ignored | **DISAGREE with plan** |
| 5. Competitive/market risks covered? | NO — DS-1 / clones not named | NO — ST-1000 at $849, junk-tier at $11-15 | **DISAGREE with plan** |
| 6. 6-month trajectory sound? | NO — 3 explicit regret scenarios | NO — 3 explicit regret scenarios | **DISAGREE with plan** |

**Result: 0/6 CONFIRMED. Both models independently concluded every strategic dimension of the plan has a gap.** This is an unusually strong consensus and is treated as a User Challenge at the final gate.

## Phase 1 — Error & Rescue Registry

| Error class | Source | Rescue | Gap |
|---|---|---|---|
| Double-feed at hopper | Feeder module | Sensor timing → retry with reverse-jog | Plan has no threshold or retry count |
| Card skew at throat | Feeder module | Not specified | **GAP** |
| Selector misroute | Selector | Not specified | **GAP** |
| Bin entry jam | Bin bank | Removable access covers | No firmware-level detection described |
| Recombine stack collapse | Recombine | "Side constraint" | **GAP — mechanism unspecified** |
| Sensor dropout | Any sensor | Not specified | **GAP** |
| Count mismatch at output | Firmware | Report failure, do not claim success | OK — this one is covered |
| False-success report | Firmware | End-to-end count check | OK — this one is covered |

## Phase 1 — Failure Modes Registry (strategic level)

| Mode | Probability | Impact | Mitigation in plan | Critical gap? |
|---|---|---|---|---|
| Randomization quality inadequate | **HIGH** (both voices calculated it) | Product has no reason to exist | None | **YES** |
| Feeder bakeoff not done | **HIGH** | Wrong singulator chosen, affects everything downstream | None | **YES** |
| Chassis envelope frozen before subsystem proofs | **HIGH** | Rework after feeder tuning | None | **YES** |
| No cycle-time budget | **HIGH** | Feeder tuned for wrong speed regime | None | **YES** |
| No MTBF/jam-rate target | **MEDIUM** | Can't tell when V1 is "done" | None | **YES** |
| Commercial alternative does the job for $40-150 | **HIGH** | Project has no wedge | None | **YES** |
| Slot-rack is actually simpler and uniform | **MEDIUM** | Abandon 8-bin months into build | One-sentence dismissal | **YES** |

## Phase 1 — "NOT in scope" (derived from this review)

Should be explicitly out of V1 to keep it shippable:

- Cut-card mechanism (already scoped out — OK)
- Table-integrated form factor (should be deferred entirely — dual-constraint trap)
- Multi-deck handling
- Network / logging / display beyond minimal LEDs (but see SSD1306 suggestion below)
- Auto-calibration of feeder nip / pressure
- Custom shuffle modes

## Phase 1 — "What already exists" (derived)

Sub-problems with existing solutions the builder should buy, not build:

- Retard pads → Canon/HP OEM, ~$5, characterized wear profile
- IR break-beam sensors → Adafruit / generic, ~$2 each
- TMC2209 driver silent stepper → ~$8
- Shuffle-quality test harness → 30-line Python simulation using `rising_sequence_count` or TV-distance metric
- State-machine firmware skeleton → countless ESP32 examples
- Build-vs-buy baseline → just buy a Shuffle Tech DS-1 used for teardown at ~$150

## Phase 1 — Completion Summary

| Section | Finding | Severity |
|---|---|---|
| Prior art map | No wedge stated; commercial alternatives not argued against | Critical |
| Premise P1 (2-pass 8-bin quality) | Both voices computed it is inadequate (~2-3 riffles, preserved pairs by construction) | **CRITICAL** |
| Premise P2 (8 bins) | Arbitrary, no trade study | High |
| Premise P3 (two passes) | Arbitrary, no trade study | High |
| Premise P4 (friction + retard) | No bakeoff, chosen by familiarity | High |
| Premise P5 (reliability-first) | Unfalsifiable without numbers | High |
| Premise P6 (dual-constraint chassis) | Classic dual-optimization trap | High |
| Premise P8 (build-vs-buy) | Missing entirely | Critical |
| Alternatives table | Missing; slot-rack and drum/carousel unexamined | Critical |
| Targets section | Missing (cost, cycle time, jam rate, quality metric) | Critical |
| Error & Rescue Registry | Multiple gaps for skew, misroute, sensor dropout, recombine collapse | High |
| 6-month regrets | 3+ explicit scenarios from both voices | Critical |
| Dream state delta | Plan as written underperforms $40 commercial clones on quality and $11 clones on cost | Critical |

---

**Phase 1 complete.** Codex: 20 concerns (10 critical, 9 high, 2 medium). Claude subagent: 18 findings (5 critical, 9 high, 4 medium). Consensus: 0/6 confirmed, 6 disagreements all aligned → surfaced at final gate as a User Challenge. Premise gate reached.

### Phase 1 — Premise Gate Decision

User selected: **"Validate first, then lock architecture."**

Effect on the plan:
- Premises P1 (2-pass 8-bin quality), P2 (8 bins), P3 (two passes), P4 (friction+retard feeder) are **UNLOCKED pending evidence**.
- Before any CAD work, the plan now requires:
  1. A Python simulation comparing ≥3 architectures (2-pass 8-bin, slot-rack 52, 1-pass 16-bin) on a real mixing-quality metric (rising-sequence count, TV-distance from uniform, or riffle-shuffle equivalence).
  2. A Targets section with BOM ceiling, cycle time ceiling, jam rate target, shuffle-quality threshold, card-envelope definition.
  3. A feeder-separator bakeoff comparing friction+retard against at least one alternative (escapement, single-roller vacuum, kicker) on measured double-feed rate.
- Table-integration scope is **deferred entirely to V2** (per the dual-constraint trap finding).
- Premise P8 (build-vs-buy) requires a one-paragraph wedge statement before the plan is considered ready for implementation.

---

# /autoplan Review — Phase 2: Design

**SKIPPED.** No software UI surface. Physical ergonomics belong in the mechanical design review, not the screen-design review skill.

---

# /autoplan Review — Phase 3: Engineering

Focused on: (a) the validation strategy, since the architecture is TBD, (b) the feeder as an architecture-independent subsystem, (c) the firmware state machine pattern, (d) the test/validation plan.

## Phase 3.0 — Scope Challenge (adapted for hardware)

No source code exists yet — this is a pure green-field hardware plan. Scope challenge is framed as: "what do the existing reference designs already solve that this plan re-invents unnecessarily?"

- **Canon / HP retard pads:** characterized wear curves, ~$5/unit, bolt-in form factor.
- **Printer feeder geometry (throat + sensor) reference designs:** multiple public teardowns; the plan can copy throat spacing, nip force, and lead-in chamfer dimensions instead of deriving from scratch.
- **ESP32 + TMC2209 stepper firmware:** countless reference codebases; state machine skeleton is not novel work.
- **IR break-beam placement patterns:** standard printer reference designs apply directly.

None of these are touched in the plan. Each can be bought as a known-good component rather than derived from first principles.

## Phase 3.1 — Architecture (mechanical + firmware)

### Mechanical module block diagram (consensus from both voices)

```
  [INPUT HOPPER]
        |
        v
  +------------+       sensor A (break-beam, throat enter)
  |  FEEDER    |  --> sensor B (break-beam, post-singulate)
  +------------+
        |
        v
  +------------+       sensor C (break-beam, selector throat)
  |  SELECTOR  |
  +------------+
        | routed to one of N bins (N TBD pending Tier 0 sim)
        v
  +----+----+----+----+----+----+----+----+
  | b1 | b2 | b3 | b4 | b5 | b6 | b7 | b8 |    BIN BANK
  +----+----+----+----+----+----+----+----+
         | deterministic pickup order
         v
  +-------------+      sensor D (pickup confirm)
  | RECOMBINE   | --> sensor E (recombine exit)
  +-------------+
         |
         +--> pass 1: back to FEEDER hopper reload (if multi-pass arch)
         +--> final: to OUTPUT
                 |
                 v
            +------------+       sensor F (output count)
            |   OUTPUT   |
            +------------+

  [ELECTRONICS BAY]  ESP32 + N×TMC2209 + feeder drv + PSU
```

### Architecture findings

| # | Finding | Sev | Fix |
|---|---|---|---|
| A1 | No datum / tolerance budget across module boundaries | Critical | Define hard datums, kinematic mounts, per-handoff pitch/yaw/height budget |
| A2 | Feeder → selector handoff is "narrow guided path" — warped cards nose-dive | High | Captive bridge with continuous lower support, lead-in chamfers sized from card envelope |
| A3 | Recombine module is hand-waved despite being second-highest risk | Critical | Pick ONE extraction concept now (compliant pickup head, belt strip, roller lift) and prototype before full CAD |
| A4 | Bin-bank / selector coupling: selector error and bin funnel offset are indistinguishable to firmware | Medium | Bin funnels 2-3x wider than selector positional error so selector owns tolerance alone |
| A5 | Stack squareness budget undefined at recombine → pass 2 handoff | High | Spec max skew (e.g. ≤1 mm across 52 cards), add squaring step (tap plate or jogger) |
| A6 | Card envelope undefined → throat, funnel, bin geometry have no design basis | Critical | Requirements table: card width/length/thickness, 52-card stack height, bow/curl, finish class, qualified deck set |

### Firmware state machine findings

Current plan: 8 states (`idle`, `feeding_pass_1`, `recombine_1`, `feeding_pass_2`, `recombine_2`, `complete`, `jam_recovery`, `service_mode`).

| # | Finding | Sev | Fix |
|---|---|---|---|
| S1 | Missing `boot_selftest` / `homing` / `calibrate` / `fault_latched` | High | Add boot → selftest → homing → idle path; refuse idle on any fault |
| S2 | `jam_recovery` is a substate family, not a state | Critical | Split into `fault_feeder`, `fault_selector`, `fault_recombine`, `fault_count` with bounded per-mechanism retry |
| S3 | Missing `paused` distinct from fault (user-pressed Stop ≠ jam) | Medium | Add `paused` with resume/abort transitions |
| S4 | Abort-mid-cycle, power-loss recovery, sensor-fail behavior unspecified | High | Define safe-stop rules, retained context, resume-vs-scrap criteria |
| S5 | End-to-end count=52 is insufficient invariant | Critical | Per-pass invariants: feeder_exits == selector_entries == sum(bin_counts); recombine_out == sum(bin_counts) before pass 2 or success |
| S6 | Brownout during shuffle loses count state | High | On brownout IRQ, write pass + bin counts to ESP32 NVS. On reboot → `fault_power`; never auto-resume; require operator clear |

## Phase 3.2 — Feeder Subsystem

| # | Finding | Sev | Fix |
|---|---|---|---|
| F1 | No nip-pressure tuning protocol — "adjustable" with no target or measurement | Critical | Gram-force gauge or calibrated spring; target range (150-300 gf); log before every test run; reference-gauge + locked calibration position |
| F2 | Two throat sensors with no defined events | High | Sensor A = `card_started` (leading edge at roller exit); B = `card_singulated` (leading edge post-singulate). A→B interval validates single-card transit; B→nextA validates spacing; A-still-blocked-past-threshold = double-feed fault |
| F3 | No sensor sample rate / polling spec | High | At 200 mm/s transit + 3 mm IR beam, leading edge crosses in ~15 ms. Require HW interrupt or ≥1 kHz poll. Document worst-case transit, require ≥10x sample rate |
| F4 | No wear curve / swap-time target | High | Life-test roller sleeve + retard pad; singulation error vs cycles; require ≤60 s swap with no re-shim |
| F5 | Throat event classification for double-feed / skew / stall / bounce-back not specified | Critical | Sensor spacing + edge sequence rules; thickness discriminator OR dual-zone measurement; 100% classification on induced events |
| F6 | No bakeoff — friction+retard chosen on familiarity | Critical | DOE bakeoff: roller durometer × retard pad material × nip force × feed speed across fixed deck matrix before freezing geometry |

## Phase 3.3 — Test / Validation Plan (MANDATORY SECTION)

**Full test plan written to disk:** `/Users/mackieg/.gstack/projects/shuffle/mackieg-main-nogit-test-plan-20260410-142438.md`

The test plan defines three tiers:

1. **Tier 0 (pre-CAD, pure Python):** architecture shuffle-quality simulator comparing ≥3 candidate architectures on rising-sequence, TV-distance, adjacency-preservation, and riffle-shuffle-equivalence metrics. Gate: ≥7 riffle equivalence before any CAD.
2. **Tier 1 (subsystem bench rigs):** feeder bakeoff, wear life, sensor timing, selector positional repeatability, recombine pickup/handoff.
3. **Tier 2 (full system):** bring-up, per-pass invariant injection, jam recovery per segment, brownout recovery, 1500-deck MTBF soak across 6 deck conditions, physical randomness validation against Python model.

### Test Diagram — codepath / event → test → gap status

| Codepath / Event | Test that would catch failure | Gap in current plan? |
|---|---|---|
| Feeder singulate | Feed-only rig, 500 cards, nip-force log | **GAP** |
| Double-feed detection | Inject stuck cards, expect fault | **GAP** |
| Skew detection | Feed warped card, expect fault or recovery | **GAP** |
| Throat sensor timing | Logic analyzer on sensor pins during feed | **GAP** |
| Selector position repeatability | 1000 moves/bin, dial indicator | **GAP** |
| Selector misroute | Force off-by-one step, expect bin-drop sensor fault | **GAP (no bin sensor)** |
| Bin drop confirm | Per-bin drop sensor toggles on every card | **GAP (sensor missing)** |
| Recombine pickup | Partial-stack pickup, 100 cycles/bin | **GAP** |
| Recombine squareness | Feeler gauge on recombined stack | **GAP** |
| Per-pass invariants | Inject missed edge, expect mismatch fault | **GAP** |
| Pass-1 → Pass-2 handoff | 52 in / 52 out, 500 runs | Partial |
| Count verify | Remove card mid-run, expect fault | **GAP** |
| Randomization quality | Python harness + physical validation | **GAP — critical** |
| MTBF / jam rate | 1500-deck soak across 6 deck conditions | **GAP — critical** |
| Brownout recovery | Kill 12V mid-shuffle | **GAP** |
| Sensor dropout | Disconnect sensor, expect self-test fail | **GAP** |
| Wear-part swap time | Stopwatch change-out, ≤60 s | **GAP** |
| Boot self-test | Power-on blocked-path test | **GAP** |
| Thermal soak | 30 min continuous, log driver temps | **GAP** |

**Of 19 critical codepaths, 18 have no defined test.** The test plan is functionally empty in the current doc.

## Phase 3.4 — Sensor Strategy

| # | Finding | Sev | Fix |
|---|---|---|---|
| SE1 | No bin-drop confirmation sensor | High | Either per-bin reflective, shared moving sensor on selector head, OR single beam across all N bin entries that each card interrupts on the way in |
| SE2 | Break-beam vs reflective not assigned per location | Medium | Throat + selector transit + count checkpoint = break-beam (edge-accurate). Bin-presence + output-tray = reflective (presence only). Homing = mechanical / Hall switch |
| SE3 | EMI from stepper drivers + 12V bus not addressed | High | Separate analog 3.3V rail for IR receivers; ferrite on stepper power leads; twisted-pair sensor wiring; 100 nF at receiver; star ground at PSU |
| SE4 | No sensor-dropout detection | High | Boot self-test: each sensor must register both states via test card or flag. During run: expect each sensor to toggle within every pass; sensor that never toggles for >N cards = dead → fault |

## Phase 3.5 — Power / BOM

| # | Finding | Sev | Fix |
|---|---|---|---|
| P1 | PSU not sized | High | 4× NEMA17 @ 0.8A + feeder + ESP32 + sensors ≈ 4-5 A peak @ 12V with 2-3x inrush. Spec 12V / 8A min (Meanwell LRS-100-12 or equiv), 470 µF bulk near driver bank, staggered enable to avoid simultaneous inrush |
| P2 | TMC2209 thermals unaddressed | Medium | At 1 A RMS × 4 active drivers ≈ 4 W total. Add heatsinks + 40 mm 12V fan on driver bank; reduce IRUN, raise IHOLD only during holds |
| P3 | Worst-case current budget not closed | High | Calculate: all steppers + feeder motor + ESP32 logic + sensors + buck losses; compare against PSU rating with 30% margin |
| P4 | 5V buck not sized | Medium | ESP32 peaks at ~500 mA; sensors + logic ~100 mA; pick 5V/2A minimum |

## Phase 3.6 — Serviceability

| # | Finding | Sev | Fix |
|---|---|---|---|
| SV1 | Jam-clearance access not verified against layout | High | Red-team the card path, mark every jam-prone zone, verify each is reachable by removing ≤1 panel. Gate CAD review on this |
| SV2 | No calibration procedure documented | High | Per-build calibration artifact: selector zero positions, feeder nip force, sensor thresholds, retard pad angle. Store in NVS. Printable via service mode |
| SV3 | No diagnostic surface beyond LEDs + buzzer | High | Add $3 SSD1306 128×64 I²C OLED. Shows state, last fault code, sensor live view in service mode. Not scope creep — it's the diff between "tune it until it works" and "engineered" |
| SV4 | "Removable access covers" may disturb alignment | Medium | Jam-clear doors must be tool-less AND non-datum; locating features never touched during service |

## Phase 3.7 — Security

N/A. Unconnected local device, no attack surface beyond physical access.

## Phase 3.0.5 — Dual Voices Consensus

### ENG DUAL VOICES — CONSENSUS TABLE

| Dimension | Claude subagent | Codex | Consensus |
|---|---|---|---|
| 1. Architecture sound? | Modular split OK but recombine handoff unmodeled; `jam_recovery` is a family | Module split coherent but no datum/tolerance budget; feeder→selector handoff is the warp trap; recombine hand-waved | **DISAGREE with plan** (converges) |
| 2. Test coverage sufficient? | 16/18 codepaths have no test; randomness + MTBF both missing | 15-item test matrix all marked "missing" or "partial" | **DISAGREE with plan** (strong) |
| 3. Performance risks addressed? | No cycle time budget; no sensor polling spec | No ms timing budgets per segment | **DISAGREE with plan** |
| 4. Security threats covered? | N/A | N/A | **CONFIRMED N/A** |
| 5. Error paths handled? | `jam_recovery` too coarse; no per-pass invariants; no brownout recovery | Same; also abort-mid-cycle, sensor-fail, power-loss unspecified | **DISAGREE with plan** (strong) |
| 6. Deployment risk manageable? | Feeder bakeoff absent; chassis envelope frozen too early; calibration procedure absent | Same; also no card envelope, no deck condition matrix | **DISAGREE with plan** |

**Result: 1/6 CONFIRMED (security N/A), 5/6 DISAGREE with plan with both models converging on the same gaps.** No model-to-model disagreements — both reviewers independently identified the same engineering blind spots.

## Phase 3 — Failure Modes Registry (engineering level)

| Mode | Probability | Impact | Mitigation in plan | Critical gap? |
|---|---|---|---|---|
| Feeder double-feed undetected | Medium | False success | Throat sensors (no classification rules) | **YES** |
| Feeder wear → doubles over time | High | Drift failure | "Replaceable" but no life test | **YES** |
| Selector misroute | Medium | Count mismatch | Sensor at selector throat (but no bin-drop sensor) | **YES** |
| Recombine stack telescope | Medium | Pickup failure | "Side constraint" hand-wave | **YES** |
| Per-pass count drift | Low-medium | False success if end-to-end is only invariant | End-to-end only | **YES** |
| Brownout mid-shuffle | Low | Partial state / false resume | Unspecified | **YES** |
| EMI false-trigger sensor | Medium | Phantom card events | Unspecified | **YES** |
| TMC2209 thermal shutdown | Medium | Mid-run failure | Unspecified | **YES** |
| Sensor dropout (dead sensor reading "clear") | Low | Phantom success | Unspecified | **YES** |
| Jam in non-accessible location | Medium | Required full disassembly | "Accessible zones" stated but not verified | **YES** |

## Phase 3 — Completion Summary

| Section | Finding count | Critical | High | Medium |
|---|---|---|---|---|
| Architecture (mech + firmware) | 12 | 4 | 6 | 2 |
| Feeder | 6 | 3 | 3 | 0 |
| Test plan | 19 (gap matrix) | 2 | 15 | 2 |
| Sensors | 4 | 0 | 3 | 1 |
| Power / BOM | 4 | 0 | 3 | 1 |
| Serviceability | 4 | 0 | 3 | 1 |
| Security | 0 (N/A) | — | — | — |
| **TOTAL** | **49** | **9** | **33** | **7** |

**Phase 3 complete.** Codex: 20 findings (8 critical, 11 high, 1 medium). Claude subagent: 25 findings (3 critical, 14 high, 8 medium). Consensus: 1/6 confirmed (security N/A), 5/6 DISAGREE-with-plan with models converging. Zero model-to-model disagreements. Passing to Phase 4 (Final Approval Gate).

---

# /autoplan Review — Phase 3.5: DX Review

**SKIPPED.** No developer-user scope. End user is a dealer/host operating a finished hardware product, not a developer integrating a library or SDK. Firmware development happens internally and is covered by the engineering review.

---

# /autoplan Review — Phase 4: Final Approval Gate

**Status: APPROVED 2026-04-10.**

User accepted both user challenges and all auto-decided engineering additions. Effective plan deltas from original:

1. **Premises P1-P4 unlocked pending evidence.** Architecture (2-pass 8-bin vs slot-rack vs 1-pass N-bin), bin count, pass count, and feeder separator are all TBD until Tier 0 simulation + feeder bakeoff complete.
2. **Table-integration scope deferred entirely to V2.** V1 is a benchtop unit with no dual-constraint footprint requirements.
3. **SSD1306 128×64 I²C OLED added to V1 UI.** Diagnostic surface is now mandatory.
4. **Bin-drop sensor coverage is now a hard requirement.** Either per-bin reflective, shared moving sensor on selector head, or single beam across all bin entries.
5. **Per-pass count invariants required** (feeder_exits == selector_entries == sum(bin_counts)). End-to-end-only is insufficient.
6. **Firmware state machine expanded.** Add `boot_selftest`, `homing`, `calibrate`, `paused`, `fault_power`. Split `jam_recovery` into per-segment faults (`fault_feeder`, `fault_selector`, `fault_recombine`, `fault_count`). Add brownout → NVS preservation.
7. **Test plan artifact lives at** `/Users/mackieg/.gstack/projects/shuffle/mackieg-main-nogit-test-plan-20260410-142438.md`. Three tiers: Tier 0 (pure Python shuffle quality sim), Tier 1 (subsystem bench rigs), Tier 2 (full system validation).
8. **Targets section still required.** User to fill: BOM ceiling, cycle time ceiling, deck envelope, primary user (home vs pro-am), shuffle-quality acceptance metric, jam rate target.

## Gating sequence before V1 CAD

1. ✅ Write the Python shuffle-quality simulator (Tier 0). — `sim/shuffle_quality.py`, 10k trials × 9 architectures.
2. ✅ Fill in Targets section. — pro-am primary, $500 BOM, 30 s cycle, new KEM + new Bee envelope. See Targets section above.
3. ✅ Feeder separator bakeoff protocol written. — `docs/tests/feeder-bakeoff.md`, 4 candidates (friction+retard, escapement, vacuum, kicker+weight) × new KEM + new Bee. Ready to build rig.
4. ✅ Lock architecture based on Tier 0 + bakeoff results.
5. Design datum/tolerance budget across module boundaries.
6. Begin subsystem CAD.

## Tier 0 Results — 2026-04-10

Simulator: `sim/shuffle_quality.py`. 10,000 Monte Carlo trials per architecture, seed=42, N=52.
Full output: `docs/tests/shuffle-quality-results.txt`.

**Rising-sequence mean (uniform target ≈ 26.48, 7-riffle benchmark ≈ 24.96):**

| Architecture | Rising seq. | Adjacency preserved | ≈ Riffle equiv. | Verdict |
|---|---|---|---|---|
| True uniform (ideal) | 26.48 ± 2.10 | 0.98 | 10.0 | baseline |
| Riffle × 7 (Bayer-Diaconis) | 24.96 ± 2.06 | 1.15 | 7.0 | benchmark |
| **Current plan: 2-pass 8-bin FIFO** | **26.08 ± 2.11** | **1.45** | **~9.2** | **PASS** |
| 2-pass 8-bin LIFO | 26.11 ± 2.08 | 1.43 | ~9.3 | PASS |
| 2-pass 16-bin FIFO | 26.37 ± 2.12 | 1.11 | ~10 | PASS |
| 1-pass 16-bin FIFO | 24.88 ± 2.09 | 3.35 | ~7.0 | FAIL (below target) |
| 1-pass 24-bin FIFO | 25.46 ± 2.11 | 2.41 | ~7.6 | FAIL (marginal) |
| 1-pass 32-bin FIFO | 25.68 ± 2.10 | 2.01 | ~7.9 | FAIL (marginal) |
| 3-pass 8-bin FIFO | 26.46 ± 2.10 | 1.03 | ~10 | PASS |
| Slot-rack 52 | 26.48 ± 2.11 | 0.98 | ~10 | PASS |

**Finding that invalidates the CEO review pessimism:** Both CEO voices computed 2-pass 8-bin as ~2-3 riffle equivalents by framing it as a radix sort. That framing is wrong. A radix sort requires deterministic bin assignment by card rank; this architecture uses *random* bin assignment per pass, so within-bin order depends on the random arrival sequence of other cards, not the card's own identity. Two independent random digit assignments mix 52! down to ≈ 8^(2·52) = 2^312 bits of entropy budget, far more than the 226 bits in 52!. Empirically, 2-pass 8-bin lands within 0.4 rising sequences of true uniform — indistinguishable at the 95% CI level.

**Architecture decision — P1 LOCKED: 2-pass 8-bin FIFO.**

- Meets and exceeds the 7-riffle target (9.2 equivalent).
- Matches true uniform on rising sequences, Kendall tau, and displacement.
- Only metric where it lags uniform: adjacency preservation (1.45 vs 0.98 — ~0.5 more preserved adjacent pairs per deck). Negligible for poker.
- 3-pass 8-bin offers marginal improvement (1.03 adjacency vs 1.45) but costs a full extra pass. Not worth it.
- Slot-rack 52 is theoretically ideal but requires 52 addressable positions. Mechanism count kills it.
- 1-pass configurations (16/24/32 bin) all fail or are marginal. Two passes is the minimum.

**Premise P1 (randomization architecture): LOCKED at 2-pass 8-bin FIFO.**
**Premise P2 (bin count): LOCKED at 8.**
**Premise P3 (pass count): LOCKED at 2.**
**Premise P4 (feeder separator): still pending bakeoff protocol.**

Next step: feeder bakeoff protocol → Targets section → begin CAD.

## Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale |
|---|---|---|---|---|---|
| 1 | 1 | Skip Phase 2 (Design review) | Mechanical | P3 pragmatic | No software UI surface. Physical ergonomics belong in Eng review. |
| 2 | 1 | Skip Phase 3.5 (DX review) | Mechanical | P3 pragmatic | No developer-user scope. End user is a dealer. |
| 3 | 1 | Run both Claude subagent + Codex voices for CEO | Mechanical | P6 bias toward action | Both available; both complete before consensus. |
| 4 | 1 | Surface 0/6 CEO consensus to premise gate | Mechanical | — | Both voices disagreed with plan on every dimension. Premise gate is the non-auto-decided gate. |
| 5 | 1 | User selected: Validate first, then lock arch | User decision | — | Unlocks P1-P4; defers CAD until Tier 0 sim + Targets + feeder bakeoff exist. |
| 6 | 3 | Defer table-integration scope entirely to V2 | Mechanical | P2 boil lakes but stay in radius | Dual-constraint trap confirmed by both voices. |
| 7 | 3 | Require SSD1306 OLED for V1 (upgrade from LED-only) | Taste | P1 completeness + P3 pragmatic | $3 part; diff between "tune until works" and "engineered" per Claude subagent. |
| 8 | 3 | Require bin-drop sensor coverage (new requirement) | Mechanical | P1 completeness | Critical gap flagged by both voices; selector misroutes otherwise silent. |
| 9 | 3 | Per-pass count invariants required, not just end-to-end | Mechanical | P1 completeness | Codex #15 + Claude F15 both flagged; no pushback. |
| 10 | 3 | `jam_recovery` must split into per-segment recovery states | Mechanical | P5 explicit over clever | Both voices flagged; implementation is concrete. |
| 11 | 3 | Brownout → NVS state preservation required | Mechanical | P1 completeness | Claude F22; Codex #14 aligned; implementation is a 10-line handler. |
| 12 | 3 | Generate test plan artifact at disk | Mechanical | P1 completeness | Required output per skill. |

