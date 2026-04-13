# Market Research — Smart Poker Table Kit

Date: 2026-04-12

## The gap

No integrated consumer "smart poker table" kit exists. The market is fragmented:

| Segment | Product | Price | RFID? | Table-install? |
|---|---|---|---|---|
| Cheap consumer | Amazon shufflers (Srkmxzr, COYEUX) | $25-60 | No | No |
| Pro consumer | Shuffle Tech ST1000 | $650-800 | No | Yes ($140 adapter) |
| Custom build | No Tilt, BBO custom tables | $3,000-5,000+ | Optional | Yes |
| Casino/enterprise | PokerTek, Shuffle Master | $5,000-50,000+ | Yes | Yes |
| Software only | PokerGFX, Smart Poker Table | $500-2,000+ | Requires DIY HW | N/A |

**The gap: $1,500-2,500 for an integrated shuffler + RFID kit.** Nobody is selling this.

## RFID poker cards exist

- **Faded Spade** — official cards of WPT, Moneymaker Tour, Live at the Bike. ~$10-15/deck retail.
- **Standard: 13.56MHz HF** (ISO14443/ISO15693). Compatible with cheap NFC readers ($4 Arduino modules).
- Poker-grade RFID cards available from Faded Spade, RFIDup, NFC Tag Factory, TP-RFID.
- Read range ~1.5m — adequate for under-felt antenna array.

## Target buyers

1. **Serious home game hosts** — $200+ buy-in weekly games. ~10,000-50,000 in North America. Already spending $2,000-$5,000 on tables + accessories.
2. **Poker content creators / streamers** — ~500-2,000 actively monetizing. Currently piecing together RFID + streaming solutions manually. Exploding market post-COVID.
3. **Small card room operators** — ~2,000-5,000 venues. Using PokerTek or custom setups.
4. **Tournament organizers** — want broadcast-quality hole card display.

## Competitive landscape

### Direct competitors (none integrated)

- **Shuffle Tech ST1000** ($650-800) — quality shuffler, no RFID, table-mountable. Closest to our shuffler module.
- **PokerGFX** — RFID streaming software with optional hardware bundles. Tiered licensing (hobbyist to enterprise). Requires DIY hardware assembly.
- **Smart Poker Table (rfidpokertable.com)** — all-in-one software for RFID tables. 
- **RF Poker** — state-of-the-art RFID equipment for streaming. Enterprise pricing.

### DIY ecosystem

- Arduino + RC522 RFID reader modules (~$4 each) can read NFC poker cards.
- Multiple hobbyist builds documented (Arduino Forum, Poker Chip Forum, HN).
- One developer built a working RFID table for **<$300** (bare-bones prototype).
- Community interest is high but no polished product exists.

## Why this hasn't been done

1. **No VC interest** — "poker peripherals" triggers gaming/regulatory concerns.
2. **Small market** — home poker table market is ~$500M/year in North America (niche).
3. **Engineering complexity** — RFID + shuffler + streaming software integration is hard.
4. **Enterprise focus** — all pro RFID vendors target casinos (high margins).
5. **No cannibalization incentive** — BBO, Just Poker Tables have no reason to offer a $2,500 kit when they sell $5,000 custom tables.

## Our positioning

| | ShuffleDeck Core | Shuffle Tech ST1000 | Amazon shufflers |
|---|---|---|---|
| Price | ~$500 (kit) | $650-800 | $25-60 |
| Shuffle quality | 9.2 riffles (proven) | Unknown (proprietary) | Terrible |
| Table-installable | Yes | Yes ($140 adapter) | No |
| RFID capable | Yes (add-on) | No | No |
| Open source | Yes | No | No |
| Jam rate | TBD (target <1/500) | Low | High |

**RFID add-on (~$300):** 13.56MHz antenna array under felt + ESP32 reader + streaming overlay software. Nothing like this exists at consumer price points.

## Recommended product line

1. **ShuffleDeck Core** (~$500) — the shuffler we're building. DIY kit or pre-assembled.
2. **ShuffleDeck RFID** (~$300) — add-on antenna array + reader. Works with Faded Spade cards.
3. **ShuffleDeck Stream** (free, open-source) — OBS overlay plugin for streaming with RFID or manual input.

Total kit: ~$800 + $10-15 for RFID cards. Vs. $5,000+ for anything comparable.

## Risks

- **Market size ceiling** — realistic addressable market is 5,000-20,000 buyers globally.
- **Price compression** — if successful, BBO/Just Poker will copy.
- **Regulatory** — some jurisdictions may restrict "automated dealing" equipment. Need legal review.
- **Customer acquisition** — no established channel for "smart poker table" category. Need influencer/YouTube strategy.

## Next steps

1. Landing page with waitlist (capturing demand signal).
2. Customer interviews — 10-15 serious home game hosts.
3. Regulatory review — gaming attorneys in CA, NV, TX, NY.
4. RFID reader prototype — ESP32 + RC522 + Faded Spade deck, prove read-through-felt works.
5. Pricing validation — would you pay $500/$800/$1,500?
