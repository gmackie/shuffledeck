# Order List — What to Buy

Date: 2026-04-12

**Already have:** 4× NEMA17 (Lumen 3D printer), 1× ESP32 DevKit, 4× TMC2209 drivers

Everything below is what you still need. Organized by order (Amazon first for speed, AliExpress for the linear rails).

---

## Amazon Order 1 — Electronics + Misc (~$50)

| Item | Search Term | Qty | ~Price |
|---|---|---|---|
| OLED display | "SSD1306 0.96 inch OLED I2C 128x64" | 1 | $4 |
| IR sensors | "TCRT5000 IR reflective sensor module" (10-pack) | 1 pack | $4 |
| Power supply | "12V 10A power supply enclosed" (Mean Well or clone) | 1 | $14 |
| Buck converter | "MP1584EN 5V buck converter module" (3-pack) | 1 pack | $3 |
| IEC inlet | "IEC C14 panel mount fused switch" | 1 | $3 |
| JST-XH kit | "JST-XH connector kit 2 3 4 pin" | 1 | $8 |
| Jumper wires | "Dupont jumper wire kit M-M M-F F-F" | 1 | $5 |
| Wire | "22 AWG stranded wire 6 color" | 1 | $8 |
| Buttons | "12mm momentary push button panel mount" (5-pack) | 1 pack | $3 |
| **Subtotal** | | | **~$52** |

## Amazon Order 2 — Mechanical (~$45)

| Item | Search Term | Qty | ~Price |
|---|---|---|---|
| GT2 belt | "GT2 timing belt 6mm 2m open loop" | 2 | $8 |
| GT2 drive pulleys | "GT2 20 tooth pulley 5mm bore 6mm" (5-pack) | 1 pack | $7 |
| GT2 idler pulleys | "GT2 20T idler pulley 5mm bore bearing" | 2 | $4 |
| 608ZZ bearings | "608ZZ bearing 8x22x7" (10-pack) | 1 pack | $6 |
| D-shaft | "5mm steel rod 100mm" or "5mm D-shaft" | 1 | $3 |
| Spring assortment | "small compression spring assortment" | 1 | $7 |
| O-rings | "silicone O-ring 20mm ID 2mm cross section" | 1 pack | $3 |
| Retard pad | "printer pickup pad rubber" or "cork rubber sheet 2mm" | 1 | $5 |
| 8mm linear rod | "8mm linear shaft 100mm hardened" (2-pack) | 1 pack | $3 |
| LM8UU bearings | "LM8UU linear bearing 8mm" (4-pack) | 1 pack | $4 |
| **Subtotal** | | | **~$50** |

## Amazon Order 3 — Fasteners (~$35)

| Item | Search Term | Qty | ~Price |
|---|---|---|---|
| M3 screw assortment | "M3 socket head cap screw assortment kit" (200-300 pcs) | 1 | $13 |
| M3x16 (NEMA17) | "M3x16 socket head cap screw" (50-pack) | 1 | $3 |
| Heat-set inserts | "M3 brass heat set insert 4mm OD 4mm length" (100-pack) | 1 | $8 |
| Heat-set tip | "soldering iron heat set insert tip M3" | 1 | $3 |
| M3 hex nuts | "M3 hex nut stainless" (100-pack) | 1 | $3 |
| M3 washers | "M3 flat washer stainless" (100-pack) | 1 | $3 |
| M3 nylock nuts | "M3 nylon lock nut" (50-pack) | 1 | $2 |
| **Subtotal** | | | **~$35** |

## Amazon Order 4 — Filament (~$62)

| Item | Search Term | Qty | ~Price |
|---|---|---|---|
| PETG | "eSUN PETG 1.75mm" or "Polymaker PolyLite PETG" | 2 kg | $40 |
| TPU 95A | "eSUN TPU 95A 1.75mm" or "NinjaTek NinjaFlex" | 1 spool (250g+) | $22 |
| **Subtotal** | | | **~$62** |

## Amazon Order 5 — Misc (~$15)

| Item | Search Term | Qty | ~Price |
|---|---|---|---|
| Rubber feet | "adhesive rubber feet 12mm" | 1 pack | $3 |
| Spiral wrap | "6mm spiral cable wrap 2m" | 1 | $3 |
| Zip ties | "100mm nylon zip ties" | 1 bag | $2 |
| Heat shrink | "heat shrink tubing assortment" | 1 | $4 |
| Hex key | "2mm ball end hex key" | 1 | $3 |
| **Subtotal** | | | **~$15** |

## Amazon Order 6 — RFID Test Kit (~$4)

| Item | Search Term | Qty | ~Price |
|---|---|---|---|
| RC522 module | "RC522 RFID module 13.56MHz SPI" | 1 | $4 |
| **Subtotal** | | | **~$4** |

## Faded Spade Order (~$15)

Order directly from fadedspade.com or Amazon:

| Item | Search Term | Qty | ~Price |
|---|---|---|---|
| RFID poker deck | "Faded Spade RFID poker cards" | 1 deck | $15 |
| **Subtotal** | | | **~$15** |

## AliExpress Order — Linear Rails (~$36)

These are the only parts worth waiting 2-3 weeks for. Amazon rails are 2-3x the price.

| Item | Search Term | Qty | ~Price |
|---|---|---|---|
| MGN12H 600mm | "MGN12H 600mm linear rail carriage" (ReliaBot or CHUANGNUO) | 2 | $18 each |
| **Subtotal** | | | **~$36** |

**When rails arrive:** remove factory grease, clean with isopropanol, re-grease with Superlube or white lithium grease. Run the carriage back and forth 20+ times to work in the new grease. Cheap rails that feel gritty will smooth out.

---

## Grand Total

| Source | Amount |
|---|---|
| Amazon orders 1-6 | ~$218 |
| Faded Spade | ~$15 |
| AliExpress | ~$36 |
| **Total** | **~$269** |

Subtract the ~$60 you already have in motors + ESP32 + drivers, and the effective BOM is **~$269 out of pocket** against the $500 ceiling. $231 headroom for iteration, spare parts, and the full RFID add-on later.

---

## Order Priority

**Order today (Amazon, arrives in 1-2 days):**
- Orders 1-5 — everything needed to start building as soon as prints are done
- Order 6 + Faded Spade — RFID test kit, can run the felt test with just the ESP32 you already have

**Order today (AliExpress, arrives in 2-3 weeks):**
- Linear rails — start printing immediately, rails arrive around the time you finish all prints

**Start printing today:**
1. Chassis section 0 (longest print, structural foundation)
2. Chassis section 1
3. Chassis section 2
4. Bin bank (may need to split into two 4-bin halves)
5. Feeder hopper
6. Everything else

See `docs/plans/print-guide.md` for per-part slicer settings.
