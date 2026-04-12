# Feeder Singulator Bakeoff Protocol

Purpose: settle premise P4 (feeder separator mechanism) before committing to feeder CAD. This is a Tier 1 bench test per the test plan. Built in isolation, no integration.

Gate: cannot begin feeder CAD until one candidate has a declared winner across the full deck envelope matrix.

## Candidates

Four candidates, ordered by implementation cost:

| # | Name | Mechanism | Why include |
|---|---|---|---|
| A | **Friction roller + retard pad** | Driven O-ring roller opposes a high-friction stationary pad. Top card has roller grip, second card is pinned by pad. | Current plan baseline. Proven in every desktop laser printer and scanner on the planet. |
| B | **Escapement gate** | A reciprocating finger below the stack presents one card at a time into a pickup path. Mechanical singulation by geometry, not friction. | Deterministic — no slip variance. But parts count is higher. |
| C | **Vacuum pickup** | Small diaphragm pump pulls card to a suction head, which swings or translates to a transport belt. | Immune to card thickness variance. Used in check scanners. |
| D | **Kicker + weight** | Spring-loaded weight pushes stack against a rotating kicker wheel. Kicker strikes only the bottom card laterally. | Used in casino-grade Shuffle Master machines. Mechanically simple but requires good side-rails. |

Slot-feed / belt-drag variants excluded — too exotic for V1.

## Deck envelope (V1 locked: 2 conditions)

Per Targets section in the plan, V1 ships against **new KEM + new Bee only**. Worn/humid/warped are V2 scope.

| Code | Deck | Condition |
|---|---|---|
| KN | New KEM (100% plastic, ~0.31 mm) | Fresh from pack |
| BN | New Bee (paper/cellulose, ~0.29 mm) | Fresh from pack |

Total: 2 decks × 52 cards = 104 cards per test cycle. Informational-only runs on worn/humid/warped decks are encouraged if time permits — the data feeds V2, and a candidate that silently fails worn decks may need an asterisk in the V1 decision.

**Worst case for Phase 2 DOE:** BN (new Bee paper). Paper cards pick up roller static faster than plastic, have more surface friction variance, and are more sensitive to nip force. If a candidate passes BN at the 120 mm/s target feed speed (pro-am cycle = 30 s), the architecture is sound.

## Metrics

All measured per test cycle:

| Metric | How | Target |
|---|---|---|
| **Double-feed rate** | Dual photo-break sensors 20 mm apart at feeder exit. If both block simultaneously for more than threshold, call a double. | ≤ 1 per 2000 singulations |
| **Miss rate** | Timeout: roller turns 2× card length with no sensor trigger. | ≤ 1 per 500 singulations |
| **Skew** | Feeler gauge or camera measurement of card exit angle. | ≤ 2° deviation from normal |
| **Transit time variance (σ)** | Logic analyzer captures edge timestamps. Measure σ of sensor1→sensor2 interval. | σ < 10% of mean for winner |
| **Jam events** | Count of stalls requiring manual assist. | 0 for winner |
| **Wear-part swap time** | Stopwatch replacing the friction/retard surface. | ≤ 60 s |

## Protocol

Run in this exact order. No re-ordering, no "just trying one config real quick" between candidates — that's how contamination happens.

### Phase 0 — Build the rig (once)

One shared frame accepts all four candidate heads via a bolt pattern with ±0.1 mm repeatability. The frame holds:

- Adjustable input hopper (angle 5°-25°, side rails ±2 mm)
- Exit throat with dual photo-break sensors (IR, Vishay TCRT5000 or equivalent)
- Logic analyzer breakout (Saleae or Pulseview on cheap clone)
- Load cell under the retard pad mount (or gram gauge for initial cal)
- ESP32 running a minimal count-and-log firmware
- Removable catch tray at exit

Document the rig with a dimensioned sketch before running any candidate. No "I'll remember" — rig drift is the single biggest source of bakeoff noise.

### Phase 1 — Per-candidate cold run (500 cards per deck condition)

For each candidate A-D, in order:

1. Install the candidate head on the frame. Record install time.
2. Set the candidate's nominal tuning per the table below.
3. Load deck KN. Run 500 singulations (≈ 10 deck cycles).
4. Log every event: pass / double / miss / skew / jam. Dump to CSV.
5. Reload with BN. Repeat.
6. Total per candidate Phase 1: 500 × 2 = 1000 cards.
7. **No tuning changes within Phase 1.** Tune-then-test is later.

Nominal starting tuning:

| Candidate | Nominal |
|---|---|
| A (friction+retard) | 225 gf nip, 60A durometer O-ring, cast silicone retard pad, 80 mm/s feed |
| B (escapement) | 100 ms dwell per cycle, 2 mm throw, spring return |
| C (vacuum) | 15 kPa vacuum, 50 ms dwell, transport belt at 100 mm/s |
| D (kicker+weight) | 300 gf weight, kicker at 60 RPM, side-rail gap 0.5 mm above thickest deck |

### Phase 2 — Survivor tuning DOE (winners from Phase 1 only)

Any candidate with >5% error rate in Phase 1 is eliminated. For the remaining candidates:

Factorial DOE with 3 factors × 3 levels (27 runs per survivor). Factors differ by candidate:

**Candidate A:** nip force (150/225/300 gf), roller durometer (50A/60A/70A), feed speed (40/80/120 mm/s)
**Candidate B:** dwell (50/100/200 ms), throw (1.5/2.0/2.5 mm), spring preload (low/mid/high)
**Candidate C:** vacuum (10/15/20 kPa), dwell (25/50/100 ms), belt speed (50/100/150 mm/s)
**Candidate D:** weight (200/300/400 gf), kicker RPM (40/60/80), side-gap (0.3/0.5/0.8 mm above stack)

Each run: 500 cards on worst-case deck (BN — new Bee paper, the hardest in V1 envelope) at **120 mm/s feed speed** (the 30 s cycle time target). Log the same metrics as Phase 1.

Pick the minimum-variance config per candidate (not lowest-mean — variance dominates long-tail jams).

### Phase 3 — Wear life (winner only)

Run 5000 cards continuous on the tuned winner. Log error rate every 500 cards. Pass criterion: error rate at 5000 marker ≤ 2× error rate at 500 marker.

Replace wear part. Re-run 500 cards. Pass criterion: error rate returns to ≤ 1.2× baseline.

### Phase 4 — Wear-part swap time

Stopwatch the swap. ≤ 60 s. No re-calibration afterward should be required to pass a 500-card validation run.

## Decision rule

Winner is the candidate that:

1. Passes all Phase 1 deck envelope conditions (≤ 1 double/2000, ≤ 1 miss/500)
2. Has the lowest combined (doubles + misses + jams) in Phase 2 at its tuned config
3. Survives Phase 3 wear test within spec
4. Meets Phase 4 swap time

Tiebreakers in order: parts count, BOM cost, tuning sensitivity (measured by DOE response surface steepness — flatter is better).

If all four fail Phase 1: the design premise is wrong. Stop and escalate — do not proceed to CAD.

## Data format

Per-cycle CSV at `docs/tests/feeder-bakeoff/<candidate>-<deck>-<timestamp>.csv`:

```
event_id,t_ms,sensor1_edge,sensor2_edge,classification,transit_ms,notes
1,1023,1020,1089,single,69,
2,2155,2150,2225,single,75,
3,3201,3198,3198,double,0,simultaneous_block
```

Aggregate per candidate at `docs/tests/feeder-bakeoff/<candidate>-summary.md`.

## What we're NOT testing here

- Full machine timing interactions — that's Tier 2
- Recombine → pass 2 handoff squareness — that's a different bench rig
- Bin entry jams — that's the selector rig
- Firmware jam recovery — that's Tier 2 with the full state machine

Keep this rig isolated. Single purpose: which singulator survives 6 deck conditions with the best margin.

## Estimated effort

- Phase 0 (rig build): 1-2 days
- Phase 1 (4 candidates × 3000 cards): 1 day if singulation is at ~80 mm/s
- Phase 2 (DOE on survivors): 1-2 days
- Phase 3 (wear life): half day
- Phase 4 (swap time): 30 minutes

Budget: one focused week, including data analysis.
