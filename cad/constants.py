# Shared constants for the single-deck card shuffler CAD project.
# Requires: pip install build123d

# ---------------------------------------------------------------------------
# Card dimensions (standard poker / bridge)
# ---------------------------------------------------------------------------
CARD_WIDTH = 63.5        # mm (short edge)
CARD_HEIGHT = 88.9       # mm (long edge)
CARD_THICKNESS = 0.3     # mm (nominal; KEM ~0.31, Bee ~0.29)
DECK_COUNT = 52
DECK_STACK_HEIGHT = DECK_COUNT * CARD_THICKNESS  # ~15.6 mm nominal
DECK_STACK_HEIGHT_MAX = 17.0  # mm — allow for air gaps and variance

# ---------------------------------------------------------------------------
# Bin bank parameters
# ---------------------------------------------------------------------------
BIN_COUNT = 8
BIN_MAX_CARDS = 10       # max cards per bin in worst-case pass
BIN_AVG_CARDS = 6.5      # expected cards per bin (52 / 8)
BIN_STACK_HEIGHT_MAX = BIN_MAX_CARDS * CARD_THICKNESS  # ~3.0 mm

# Card clearance inside bins and guides
CARD_CLEARANCE_WIDTH = 1.0   # mm per side beyond card width
CARD_CLEARANCE_HEIGHT = 1.0  # mm per side beyond card height

# Derived internal bin dimensions
BIN_INTERNAL_WIDTH = CARD_WIDTH + 2 * CARD_CLEARANCE_WIDTH    # 65.5 mm
BIN_INTERNAL_DEPTH = CARD_HEIGHT + 2 * CARD_CLEARANCE_HEIGHT  # 90.9 mm
BIN_INTERNAL_HEIGHT = 20.0   # mm — room for 10 cards + extraction clearance

# Bin construction
BIN_WALL_THICKNESS = 2.0     # mm
BIN_FLOOR_THICKNESS = 1.5    # mm
BIN_ENTRY_FUNNEL_CHAMFER = 3.0  # mm — 45-deg chamfer at top edges for entry
BIN_SPACING = 2.0            # mm gap between adjacent bins (selector access)

# ---------------------------------------------------------------------------
# NEMA 17 stepper motor
# ---------------------------------------------------------------------------
NEMA17_FACE = 42.3       # mm square face dimension
NEMA17_HOLE_SPACING = 31.0   # mm center-to-center (diagonal pattern)
NEMA17_HOLE_DIAMETER = 3.0   # mm (M3 mounting bolts)
NEMA17_PILOT_DIAMETER = 22.0 # mm (central pilot / boss)
NEMA17_PILOT_DEPTH = 2.0     # mm
NEMA17_SHAFT_DIAMETER = 5.0  # mm (D-shaft)
NEMA17_BODY_LENGTH_SHORT = 34.0   # mm (pancake)
NEMA17_BODY_LENGTH_STANDARD = 40.0  # mm
NEMA17_BODY_LENGTH_LONG = 48.0    # mm

# ---------------------------------------------------------------------------
# Electronics
# ---------------------------------------------------------------------------
ESP32_LENGTH = 51.0      # mm
ESP32_WIDTH = 28.0        # mm
TMC2209_LENGTH = 20.3    # mm (typical breakout board)
TMC2209_WIDTH = 15.2     # mm

# ---------------------------------------------------------------------------
# 3D print tolerances (PETG primary, TPU for contact surfaces)
# ---------------------------------------------------------------------------
PRINT_TOL_DEFAULT = 0.2      # mm — general clearance fits
PRINT_TOL_TIGHT = 0.1        # mm — bearing bores, shaft fits
PRINT_TOL_LOOSE = 0.4        # mm — cosmetic / non-critical
LAYER_HEIGHT = 0.2            # mm — assumed slicer layer height
MIN_WALL = 1.2                # mm — minimum printable wall (3 perimeters)
MIN_FEATURE = 0.8             # mm — minimum positive feature size

# ---------------------------------------------------------------------------
# Fasteners — M3 and M4 (hex socket cap screws + heat-set inserts)
# ---------------------------------------------------------------------------
# M3
M3_CLEARANCE_HOLE = 3.4      # mm diameter (close fit)
M3_TAP_HOLE = 2.5            # mm diameter (for threading into plastic)
M3_HEAD_DIAMETER = 5.5       # mm (socket cap head)
M3_HEAD_HEIGHT = 3.0         # mm
M3_HEATSET_OD = 4.0          # mm (brass insert outer diameter, short variant)
M3_HEATSET_LENGTH = 4.0      # mm (insertion depth)
M3_HEATSET_BORE = 3.2        # mm (hole in printed part for press-in)

# M4
M4_CLEARANCE_HOLE = 4.5      # mm diameter (close fit)
M4_TAP_HOLE = 3.3            # mm diameter
M4_HEAD_DIAMETER = 7.0       # mm (socket cap head)
M4_HEAD_HEIGHT = 4.0         # mm
M4_HEATSET_OD = 5.6          # mm
M4_HEATSET_LENGTH = 5.7      # mm
M4_HEATSET_BORE = 4.8        # mm

# ---------------------------------------------------------------------------
# Machine-level targets
# ---------------------------------------------------------------------------
CYCLE_TIME_TARGET = 30.0     # seconds — full 2-pass shuffle
FEED_SPEED_TARGET = 120.0    # mm/s — derived from cycle time
PASSES = 2
SINGULATIONS_PER_SHUFFLE = DECK_COUNT * PASSES  # 104
