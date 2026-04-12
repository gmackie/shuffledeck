"""
Shuffle quality simulator for the single-deck shuffler architecture selection.

Purpose: compare candidate shuffler architectures on standard mixing-quality
metrics before committing to CAD. This is the Tier 0 gate from the test plan.

Architectures simulated:
  - 2-pass 8-bin (current plan, FIFO and LIFO recombine variants)
  - 2-pass 16-bin
  - 1-pass 16-bin
  - 1-pass 24-bin
  - 3-pass 8-bin
  - Slot-rack 52 (one card per slot, single pass)

Baselines:
  - True uniform random (the ideal)
  - 1..10 riffle shuffles (the Bayer-Diaconis benchmark; 7 riffles is the
    classic "sufficiently mixed" line for a 52-card deck)

Metrics:
  - Rising-sequence count: number of maximal increasing runs of consecutive
    values in the output permutation. Uniform expectation ~(N+1)/2 = 26.5.
    One fresh riffle of a sorted deck produces exactly 2 rising sequences.
    Seven riffles brings the deck close to uniform. This is the classic
    shuffle-quality benchmark.
  - Adjacency preservation: ordered pairs (a, b) that were adjacent in the
    original deck AND remain adjacent in the output. Uniform expectation is
    (N-1)/N ≈ 0.98.
  - Mean displacement: average |output_position - input_position| per card.
    Uniform expectation is ≈ (N^2 - 1)/(3N) ≈ 17.3 for N=52.
  - Kendall tau: inversion count (pairs out of order vs original).
    Uniform expectation is N(N-1)/4 = 663 for N=52.

Usage:
    python3 shuffle_quality.py [--trials N]

The simulator uses a fixed seed for reproducibility. Change SEED to vary.
"""

import argparse
import random
import statistics
from dataclasses import dataclass, field
from typing import Callable

N = 52
DECK = list(range(N))
SEED = 42


# ---------- Architectures ----------

def two_pass_n_bin(deck, n_bins, passes=2, recombine="fifo", rng=None):
    """N-bin random-assign shuffle, configurable passes and recombine mode.

    recombine="fifo": bins are read in input order within each bin.
    recombine="lifo": bins are read in reverse within each bin (physically,
    this is what you get if you pick up each bin and dump it on the stack
    mouth-down — the top of the bin goes out first).
    """
    rng = rng or random.Random()
    current = list(deck)
    for _ in range(passes):
        bins = [[] for _ in range(n_bins)]
        for card in current:
            bins[rng.randint(0, n_bins - 1)].append(card)
        if recombine == "fifo":
            current = [c for b in bins for c in b]
        else:  # lifo
            current = [c for b in bins for c in reversed(b)]
    return current


def slot_rack(deck, rng=None):
    """Assign each card to a unique slot 0..N-1 (one pass, provably uniform)."""
    rng = rng or random.Random()
    slots = list(range(N))
    rng.shuffle(slots)
    out = [None] * N
    for card, slot in zip(deck, slots):
        out[slot] = card
    return out


def riffle_shuffle(deck, times=1, rng=None):
    """Gilbert-Shannon-Reeds (GSR) riffle model — the standard model
    for a single riffle shuffle. Cut at the middle, interleave with
    probability proportional to remaining stack heights."""
    rng = rng or random.Random()
    current = list(deck)
    for _ in range(times):
        n = len(current)
        mid = n // 2
        left = current[:mid]
        right = current[mid:]
        out = []
        i = j = 0
        while i < len(left) and j < len(right):
            remaining_left = len(left) - i
            remaining_right = len(right) - j
            if rng.random() < remaining_left / (remaining_left + remaining_right):
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        current = out
    return current


def true_uniform(deck, rng=None):
    rng = rng or random.Random()
    out = list(deck)
    rng.shuffle(out)
    return out


# ---------- Metrics ----------

def rising_sequences(perm):
    """Number of maximal rising subsequences of consecutive values in perm.

    A permutation π has a "break" between value v and v+1 whenever
    pos(v+1) < pos(v). Rising-sequence count = 1 + number of breaks.
    """
    pos = [0] * len(perm)
    for i, v in enumerate(perm):
        pos[v] = i
    count = 1
    for v in range(1, len(perm)):
        if pos[v] < pos[v - 1]:
            count += 1
    return count


def adjacency_preservation(original, shuffled):
    """Count ordered pairs (a, b) adjacent in original AND still adjacent
    in shuffled, with a still immediately before b."""
    original_pairs = {(original[i], original[i + 1]) for i in range(len(original) - 1)}
    shuffled_pairs = {(shuffled[i], shuffled[i + 1]) for i in range(len(shuffled) - 1)}
    return len(original_pairs & shuffled_pairs)


def mean_displacement(original, shuffled):
    orig_pos = {v: i for i, v in enumerate(original)}
    return statistics.mean(abs(i - orig_pos[v]) for i, v in enumerate(shuffled))


def kendall_tau(original, shuffled):
    """Inversion count: number of (i, j) pairs where i < j in output
    but ranks(i) > ranks(j) relative to original order."""
    orig_pos = {v: i for i, v in enumerate(original)}
    ranks = [orig_pos[v] for v in shuffled]
    inv = 0
    n = len(ranks)
    for i in range(n):
        ri = ranks[i]
        for j in range(i + 1, n):
            if ri > ranks[j]:
                inv += 1
    return inv


# ---------- Runner ----------

@dataclass
class Result:
    name: str
    n_trials: int
    rising: list = field(default_factory=list)
    adj: list = field(default_factory=list)
    disp: list = field(default_factory=list)
    kendall: list = field(default_factory=list)

    def summary(self):
        return {
            "rising_mean": statistics.mean(self.rising),
            "rising_std": statistics.stdev(self.rising) if len(self.rising) > 1 else 0,
            "adj_mean": statistics.mean(self.adj),
            "adj_std": statistics.stdev(self.adj) if len(self.adj) > 1 else 0,
            "disp_mean": statistics.mean(self.disp),
            "disp_std": statistics.stdev(self.disp) if len(self.disp) > 1 else 0,
            "kendall_mean": statistics.mean(self.kendall),
            "kendall_std": statistics.stdev(self.kendall) if len(self.kendall) > 1 else 0,
        }


def simulate(name, shuffle_fn, n_trials, seed=SEED):
    rng = random.Random(seed)
    result = Result(name=name, n_trials=n_trials)
    for _ in range(n_trials):
        out = shuffle_fn(DECK, rng=rng)
        result.rising.append(rising_sequences(out))
        result.adj.append(adjacency_preservation(DECK, out))
        result.disp.append(mean_displacement(DECK, out))
        result.kendall.append(kendall_tau(DECK, out))
    return result


def riffle_equivalence(rising_mean, uniform_mean, riffle_curve):
    """Given a rising-sequence mean, find the closest matching point on the
    riffle-count curve. Returns fractional riffles (0..10+)."""
    # riffle_curve is [(k, rising_mean_at_k), ...]
    # Find the first k where rising_mean_at_k >= rising_mean (we're approaching uniform from below).
    for i, (k, rm) in enumerate(riffle_curve):
        if rm >= rising_mean:
            if i == 0:
                return float(k)
            prev_k, prev_rm = riffle_curve[i - 1]
            # Linear interp
            if rm == prev_rm:
                return float(k)
            frac = (rising_mean - prev_rm) / (rm - prev_rm)
            return prev_k + frac * (k - prev_k)
    return float(riffle_curve[-1][0])  # Off the end of the curve


def print_table(results, riffle_curve, uniform_summary):
    print()
    print(f"{'Architecture':<36} {'Rising seq.':>14} {'Adjacency':>13} {'Displace.':>13} {'Kendall τ':>14} {'≈ Riffles':>11}")
    print("-" * 105)

    def fmt(r):
        s = r.summary()
        rising = f"{s['rising_mean']:5.2f} ± {s['rising_std']:4.2f}"
        adj = f"{s['adj_mean']:4.2f} ± {s['adj_std']:3.2f}"
        disp = f"{s['disp_mean']:5.2f} ± {s['disp_std']:4.2f}"
        kendall = f"{s['kendall_mean']:5.0f} ± {s['kendall_std']:4.0f}"
        rif = riffle_equivalence(s['rising_mean'], uniform_summary['rising_mean'], riffle_curve)
        rif_str = f"{rif:5.2f}"
        print(f"{r.name:<36} {rising:>14} {adj:>13} {disp:>13} {kendall:>14} {rif_str:>11}")

    for r in results:
        fmt(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=10000, help="Monte Carlo trials per architecture")
    args = ap.parse_args()

    n = args.trials
    print(f"Running {n} trials per architecture (seed={SEED}, N={N} cards)")
    print("Uniform expectation: rising ~26.5, adjacency ~0.98, displacement ~17.3, Kendall τ ~663")

    # Baseline: true uniform
    uniform = simulate("True uniform (ideal)", true_uniform, n)
    uniform_summary = uniform.summary()

    # Riffle curve
    riffle_results = []
    riffle_curve = []  # [(k, rising_mean)]
    for k in [1, 2, 3, 4, 5, 6, 7, 8, 10]:
        r = simulate(
            f"Riffle shuffle × {k}",
            lambda d, rng=None, k=k: riffle_shuffle(d, k, rng),
            n,
        )
        riffle_results.append(r)
        riffle_curve.append((k, r.summary()["rising_mean"]))

    # Candidates
    candidates = [
        ("Current plan: 2-pass 8-bin FIFO",
         lambda d, rng=None: two_pass_n_bin(d, 8, 2, "fifo", rng)),
        ("Current plan: 2-pass 8-bin LIFO",
         lambda d, rng=None: two_pass_n_bin(d, 8, 2, "lifo", rng)),
        ("Alt: 2-pass 16-bin FIFO",
         lambda d, rng=None: two_pass_n_bin(d, 16, 2, "fifo", rng)),
        ("Alt: 1-pass 16-bin FIFO",
         lambda d, rng=None: two_pass_n_bin(d, 16, 1, "fifo", rng)),
        ("Alt: 1-pass 24-bin FIFO",
         lambda d, rng=None: two_pass_n_bin(d, 24, 1, "fifo", rng)),
        ("Alt: 1-pass 32-bin FIFO",
         lambda d, rng=None: two_pass_n_bin(d, 32, 1, "fifo", rng)),
        ("Alt: 3-pass 8-bin FIFO",
         lambda d, rng=None: two_pass_n_bin(d, 8, 3, "fifo", rng)),
        ("Alt: 3-pass 8-bin LIFO",
         lambda d, rng=None: two_pass_n_bin(d, 8, 3, "lifo", rng)),
        ("Alt: Slot-rack 52 (1 pass)", slot_rack),
    ]

    candidate_results = [simulate(name, fn, n) for name, fn in candidates]

    print_table([uniform] + riffle_results + candidate_results, riffle_curve, uniform_summary)

    # Verdict
    print()
    print("=" * 105)
    print("VERDICT")
    print("=" * 105)
    target_rising = 26.0  # ~7-riffle equivalent
    for r in candidate_results:
        s = r.summary()
        rif = riffle_equivalence(s['rising_mean'], uniform_summary['rising_mean'], riffle_curve)
        passes = "PASS" if s['rising_mean'] >= target_rising else "FAIL"
        print(f"  {r.name:<36}  rising={s['rising_mean']:5.2f}  ~{rif:4.2f} riffles  {passes}")
    print()
    print(f"Pass criterion: rising-sequence mean >= {target_rising} (target: ~7 riffle equivalent).")
    print(f"Uniform reference: {uniform_summary['rising_mean']:.2f}.")


if __name__ == "__main__":
    main()
