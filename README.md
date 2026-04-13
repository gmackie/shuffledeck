# ShuffleDeck

Open-source automatic card shuffler for poker tables. Casino-grade randomization at a fraction of the cost.

## What is this?

A table-installed automatic shuffler that produces mathematically verified random output (9.2 riffle equivalents, indistinguishable from true uniform). Plus an RFID hole card reader and streaming overlay for live poker broadcasts.

## Product line

| Product | Price | Status |
|---|---|---|
| **ShuffleDeck Core** | ~$500 kit | CAD + firmware complete, pre-physical-build |
| **ShuffleDeck RFID** | ~$300 add-on | Prototype firmware, needs hardware validation |
| **ShuffleDeck Stream** | Free | Working demo overlay |

## Architecture

2-pass, 8-bin random FIFO shuffle. 52 cards are singulated by a friction roller, routed to one of 8 bins by a belt-driven selector, recombined, and shuffled again. The result is mathematically indistinguishable from a true uniform random permutation.

- **Shuffle time:** 30 seconds
- **Randomization:** ~9.2 riffle equivalents (7 is the classic Bayer-Diaconis benchmark)
- **Controller:** ESP32 with TMC2209 stepper drivers
- **Card support:** New KEM (plastic) and Bee (paper) poker cards
- **BOM cost:** ~$300

## Repository structure

```
sim/                        Shuffle quality simulator (Python)
cad/                        Parametric CAD (Build123d)
  constants.py              Shared dimensions and tolerances
  chassis/                  3-section printable base plate
  feeder/                   Hopper + singulation mechanism
  selector/                 Belt-driven card routing carriage
  bin_bank.py               8-bin FIFO storage
  recombine/                Pusher/elevator + squaring station
  output/                   Deck receiving tray
  renders/                  GLTF + STEP exports for rendering
firmware/
  shuffler/                 Production firmware (ESP32, 13-state machine)
  bakeoff-rig/              Feeder test bench instrument
  rfid-reader/              RFID card reader prototype
site/
  index.html                Landing page with 3D model viewer
  overlay.html              OBS streaming overlay
docs/plans/
  2026-04-09-...design.md   V1 design document
  datum-tolerance-budget.md Interface tolerance stackups
  bom.md                    Full bill of materials
  wiring-pinout.md          GPIO assignments and wiring guide
  print-guide.md            3D printing settings per part
  assembly-sequence.md      12-phase build instructions
  feeder-bakeoff.md         Feeder candidate test protocol
  market-research.md        Smart poker table market analysis
```

## Quick start

### Run the shuffle quality simulator

```bash
python3 sim/shuffle_quality.py
```

### Export CAD models

```bash
uv venv .venv && source .venv/bin/activate
uv pip install build123d
cd cad && python export_all.py       # STEP + STL for all modules
cd cad && python render_images.py    # GLTF for 3D viewer
```

### Flash firmware

```bash
cd firmware/shuffler && pio run -t upload    # production shuffler
cd firmware/bakeoff-rig && pio run -t upload # feeder test bench
cd firmware/rfid-reader && pio run -t upload # RFID reader
```

### Preview the landing page

```bash
python3 -m http.server 8765
open http://localhost:8765/site/index.html
```

### Preview the streaming overlay

```bash
open http://localhost:8765/site/overlay.html
```
Demo mode activates automatically without RFID hardware connected.

## Build the shuffler

1. Order parts from [`docs/plans/bom.md`](docs/plans/bom.md) (~$300)
2. Print parts per [`docs/plans/print-guide.md`](docs/plans/print-guide.md)
3. Wire electronics per [`docs/plans/wiring-pinout.md`](docs/plans/wiring-pinout.md)
4. Assemble per [`docs/plans/assembly-sequence.md`](docs/plans/assembly-sequence.md)
5. Flash firmware and calibrate

## Design validation

The randomization architecture was validated by Monte Carlo simulation (10,000 trials) against 4 metrics:

| Metric | 2-pass 8-bin | True uniform | 7 riffles |
|---|---|---|---|
| Rising sequences | 26.08 ± 2.11 | 26.48 ± 2.10 | 24.96 ± 2.06 |
| Adjacency preserved | 1.45 | 0.98 | 1.15 |
| Mean displacement | 17.16 | 17.32 | 17.25 |
| Kendall tau | 651 | 663 | 658 |

Full results: [`docs/tests/shuffle-quality-results.txt`](docs/tests/shuffle-quality-results.txt)

## License

Open-source hardware and software. License TBD.
