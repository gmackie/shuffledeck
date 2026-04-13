# RFID Through-Felt Validation Test

Date: 2026-04-12
Cost: ~$19
Time: ~30 minutes

## Purpose

Prove that a $4 RC522 module can read Faded Spade RFID poker cards through poker table felt before committing to the full ShuffleDeck RFID add-on ($300 BOM).

## Parts Needed

| Part | Cost | Source |
|---|---|---|
| RC522 RFID reader module (13.56MHz) | $4 | Amazon / AliExpress |
| Faded Spade RFID poker deck | $10-15 | fadedspade.com / Amazon |
| ESP32 DevKit (already have) | $0 | — |
| Jumper wires (already have) | $0 | — |
| Piece of poker table felt (~12"×12") | $0-5 | scrap from fabric store, or test on actual table |

Total: ~$19

## Wiring

RC522 → ESP32 (default VSPI):

| RC522 Pin | ESP32 Pin | Notes |
|---|---|---|
| SDA (SS) | GPIO 5 | Chip select |
| SCK | GPIO 18 | SPI clock |
| MOSI | GPIO 23 | SPI data out |
| MISO | GPIO 19 | SPI data in |
| RST | GPIO 22 | Reset |
| 3.3V | 3V3 | **Do NOT use 5V** |
| GND | GND | |

## Firmware

Flash the RFID reader firmware:

```bash
cd firmware/rfid-reader && pio run -t upload
```

Open serial monitor at 115200. The reader starts in read mode by default.

## Test Protocol

### Test 1: Bare Read (Baseline)

1. Place one Faded Spade card directly on the RC522 antenna
2. Serial monitor should print the card UID within 100ms
3. **Pass:** UID printed. **Fail:** no read, check wiring.

### Test 2: Single-Layer Felt

1. Place one layer of poker table felt over the RC522
2. Place card on top of felt
3. Record: does it read? What's the max distance (add cardboard spacers)?
4. **Expected:** reads through 1-3mm felt with no issues

### Test 3: Double-Layer Felt

1. Two layers of felt (simulates thick table padding)
2. Repeat read test
3. Record max read distance

### Test 4: Felt + Foam Padding

1. Felt + 3mm EVA foam (common table underlayment)
2. This is the realistic worst case for under-table mounting
3. **Target:** reliable reads at ≤ 5mm total material thickness

### Test 5: Multi-Card Stack

1. Stack of 2 cards through felt (hole card scenario: 2 cards dealt face down)
2. Can the reader identify both cards?
3. **Expected:** RC522 can read the bottom card but may miss the top due to collision. Anti-collision protocol should handle this, but test it.

### Test 6: Adjacent Card Interference

1. Place the reader under felt
2. Place target card directly above
3. Place two other cards 50mm to each side
4. Verify only the directly-above card is read
5. **This determines antenna spacing** for the 9-seat array

## Recording Results

For each test, record:

```
Test #: [1-6]
Material stack: [description]
Total thickness: [mm]
Read success: [yes/no]
Read time: [ms, from serial timestamp]
UID correct: [yes/no]
False reads from adjacent: [yes/no]
Max reliable distance: [mm]
```

## Decision Criteria

| Result | Decision |
|---|---|
| Reads through ≤ 3mm felt reliably | **GO** — proceed with RFID add-on development |
| Reads through ≤ 5mm with foam | **GO** — may need antenna tuning or PN532 upgrade |
| Fails through single felt layer | **STOP** — RC522 won't work, evaluate PN532 or custom antenna |
| Can't distinguish 2 stacked cards | **ACCEPTABLE** — design for bottom-card-only read, deal with it in software |
| Adjacent card crosstalk at 50mm | **CONCERN** — need smaller antenna or shielding between seats |

## If It Works

The full RFID add-on design:

- 9× RC522 modules (one per seat), ~$36
- Custom PCB or perfboard with SPI multiplexer (CD74HC4067), ~$5
- Under-felt antenna array with 3D-printed positioning jig
- ESP32 reader (can be same as shuffler or dedicated)
- Total RFID hardware: ~$50-80 (well under the $300 ceiling, which includes the streaming software and enclosure)

The `firmware/rfid-reader/` code already handles card database, WebSocket broadcast, and registration mode. The `site/overlay.html` streaming overlay is ready to receive card events.

## If It Doesn't Work

Alternatives in order of preference:

1. **PN532 module** ($8-12) — better antenna, NFC-A + NFC-B, longer range. Drop-in replacement for RC522 in the firmware (different library but same SPI bus).
2. **Custom antenna** — etch or wind a larger loop antenna tuned to 13.56MHz. More range but more complexity.
3. **Different card brand** — try RFIDup or TP-RFID cards, which may have stronger transponders than Faded Spade.
4. **Above-table reader** — redesign as a card slot reader instead of through-felt. Less elegant but guaranteed to work. This is what casino systems do.
