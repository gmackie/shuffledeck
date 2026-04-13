# First Power-On Preflight Checklist

Date: 2026-04-12

Go through this before applying 12V power to anything. Mistakes here fry TMC2209 drivers ($5 each, fragile).

---

## Phase 0: Before Any Power

- [ ] **Inspect all solder joints** under magnification. Cold joints on TMC2209 UART pins are the #1 failure mode.
- [ ] **Verify 12V PSU polarity.** Measure with multimeter before connecting. Some cheap PSUs have swapped terminal labels.
- [ ] **Verify 5V buck converter output.** Connect 12V in, measure output with multimeter. Adjust trim pot to 5.0V ± 0.1V. Do this BEFORE connecting the ESP32.
- [ ] **Check TMC2209 MS1/MS2 addresses.** Reference `motor-setup-lumen.md`. Each driver must have a unique address.
- [ ] **Motor coil check.** For each motor, confirm coil pairs with the touch-and-spin method. Swapped coils = motor vibrates in place instead of rotating.
- [ ] **No shorts.** Continuity-check VM to GND on each TMC2209 board. Should read open circuit (megaohms). If shorted, find the solder bridge before proceeding.

## Phase 1: ESP32 Only (USB Power)

- [ ] Connect ESP32 via USB (no 12V yet)
- [ ] Flash shuffler firmware: `cd firmware/shuffler && pio run -t upload`
- [ ] Open serial monitor at 115200 baud
- [ ] Verify boot message appears: "ShuffleDeck V1 — Boot Self-Test"
- [ ] OLED should display boot screen (if connected via I2C)
- [ ] Type `status` in serial monitor — should report all motors as COMM_FAIL (expected, they have no power yet)

## Phase 2: Single Motor Test (12V)

Test ONE motor at a time. If a driver is wired wrong, you only lose one.

- [ ] Connect 12V PSU to ONE TMC2209 only (the feeder, addr 0)
- [ ] Connect 5V buck output to ESP32 VIN (or continue using USB power)
- [ ] Connect UART bus (GPIO 12/13) to the feeder TMC2209 only
- [ ] Type `status` — feeder should report COMM_OK
- [ ] Type `service` to enter service mode, then `jog feed+` — motor should rotate ~1 rev
- [ ] **Check motor temperature** after jogging. Should be barely warm. If hot, current setting is too high or coils are swapped.
- [ ] **Listen.** StealthChop should be nearly silent. If the motor screams, UART communication may have failed and the driver fell back to defaults.

Repeat for each motor (enter `service` mode first, `exit` to leave):

- [ ] Selector X (addr 1): `jog sel+`
- [ ] Recombine X (addr 2): `jog recx+`
- [ ] Recombine Z (addr 3): `jog recz+`

## Phase 3: All Motors Together

- [ ] Connect all 4 TMC2209 boards to 12V and UART bus
- [ ] Type `status` — all 4 should report COMM_OK
- [ ] Type `selftest` — each axis jogs forward 50 steps and back
- [ ] **Watch for missed steps.** If a motor doesn't return to its start position, check mechanical binding or increase current by 100mA.

## Phase 4: Sensor Check

- [ ] Connect each TCRT5000 module one at a time
- [ ] Type `sensors` — should show 6 sensor states (HIGH = clear, LOW = blocked)
- [ ] Wave a card in front of each sensor — state should flip
- [ ] Verify ISR triggers: type `events` after triggering each sensor. Event queue should show the trigger with timestamp.

Sensor positions and expected GPIO:

| Sensor | GPIO | Location |
|---|---|---|
| Feed exit | 34 | After feeder roller |
| Post-singulation | 35 | Confirms single card |
| Selector throat | 36 | Card entering selector |
| Bin entry | 39 | Card landed in bin |
| Recombine pickup | 23 | Card grabbed by elevator |
| Output | 22 | Card in output tray |

## Phase 5: Full Integration

- [ ] Type `shuffle` in serial monitor, or press the Shuffle button (GPIO 15)
- [ ] State machine should advance: IDLE → FEED_PASS1 → ...
- [ ] Without cards, it will hit MISS_TIMEOUT after ~1 second (no card detected at feed exit sensor). This is expected.
- [ ] Verify the OLED shows state transitions
- [ ] Press Stop button (GPIO 0) — should halt all motors and enter JAM_RECOVERY

## Phase 6: First Card Test

- [ ] Load 5-10 cards (not the full deck) into the feeder hopper
- [ ] Press Shuffle
- [ ] Watch for: card singulation, selector routing, bin entry confirmation
- [ ] If a card jams: note which sensor timed out, check card path alignment at that point
- [ ] Gradually increase to full 52-card deck

---

## Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---|---|---|
| Motor doesn't move | EN pin stuck HIGH | Check enable pin wiring, verify `motor_enable()` pulls LOW |
| Motor vibrates but doesn't rotate | Coil wires swapped | Swap one coil pair (e.g., swap A+ and A-) |
| Motor screams (loud whine) | UART failed, no StealthChop | Check UART wiring, verify 1kΩ resistor on TX line |
| TMC2209 version reads 0x00 | No UART communication | Check TX/RX wiring, verify VIO connected to 3.3V |
| TMC2209 version reads 0xFF | Bus contention | Check for shorted UART lines, verify MS1/MS2 addresses are unique |
| Sensor always reads LOW | Sensor too close to surface | Adjust mount distance to 3-5mm, check for ambient IR interference |
| Sensor never triggers | Sensor dead or wired wrong | Check VCC/GND, verify correct GPIO pin (34-39 are input-only on ESP32) |
| OLED blank | Wrong I2C address | Try 0x3D instead of 0x3C, run I2C scanner sketch |
| ESP32 reboots on motor start | Power spike | Add 100µF electrolytic cap across 5V rail, use separate 5V supply |
| Cards double-feed | Retard pad worn or wrong pressure | Increase spring preload, replace pad material, check roller O-ring condition |
| Cards skew in selector | Guide channel too tight/loose | Sand or shim the card guide on the selector carriage |
