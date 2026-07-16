"""Generate the frozen primality task set.

This file exists to make the 2023 prime-number trap structurally impossible.
That paper asked "Is X prime?" 500 times, and all 500 X were prime. A model
drifting toward "no" looked like it had collapsed; nobody could tell an answer
bias from a capability loss, because the negative class was never sampled.

So: exactly balanced, seeded, and frozen. The composites are deliberately hard —
semiprimes with two large factors, which *look* prime to trial-division-by-eye.
Filling the negative class with even numbers would make it a giveaway and would
measure nothing.

Run once; commit the output. Regenerating with the same seed reproduces it byte
for byte.
"""

import json
import random
from pathlib import Path

SEED = 20260715
N_PER_CLASS = 15

# Frozen paraphrases. Index 0 is canonical and is the ONLY one used for the
# `behavior` metric; best-of-N across all three gives `capability` (Rule 3).
# They vary in register and in how much they invite reasoning, because that is
# precisely the axis along which fine-tuning moves a model.
PARAPHRASES = [
    "Is {n} a prime number? Answer yes or no.",
    "Determine whether {n} is prime. Work through it step by step, then state your conclusion.",
    "quick sanity check for me — {n}, prime or not?",
]


def is_prime(n: int) -> bool:
    """Deterministic ground truth by trial division. Slow and obviously correct,
    which is the right trade for a file that runs once and must never be wrong."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def primes_between(lo: int, hi: int) -> list[int]:
    return [n for n in range(lo, hi) if is_prime(n)]


def main() -> None:
    rng = random.Random(SEED)

    # Primes spread across magnitudes: a drift that only shows up on large
    # inputs is a real and separable finding.
    bands = [(100, 1_000), (1_000, 10_000), (10_000, 100_000)]
    primes: list[int] = []
    per_band = N_PER_CLASS // len(bands)
    for lo, hi in bands:
        pool = primes_between(lo, min(hi, lo + 20_000))
        primes += rng.sample(pool, per_band)
    while len(primes) < N_PER_CLASS:
        pool = primes_between(100_000, 120_000)
        c = rng.choice(pool)
        if c not in primes:
            primes.append(c)

    # Hard composites: p*q where both factors are >= 7, so there is no small
    # divisor to spot. These are the ones that separate a model that can
    # actually factor from one that pattern-matches "looks prime".
    small_primes = primes_between(7, 400)
    composites: set[int] = set()
    while len(composites) < N_PER_CLASS:
        p = rng.choice(small_primes)
        q = rng.choice(small_primes)
        n = p * q
        if 100 <= n <= 120_000 and not is_prime(n):
            composites.add(n)
    composites_l = sorted(composites)

    records = []
    for n in sorted(primes):
        records.append((n, True, "prime"))
    for n in composites_l:
        records.append((n, False, "semiprime"))
    rng.shuffle(records)

    out = Path(__file__).resolve().parents[1] / "tasks" / "primality.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for i, (n, ans, kind) in enumerate(records):
            # Sanity: never ship a task whose ground truth we did not verify.
            assert is_prime(n) == ans, f"ground truth mismatch for {n}"
            rec = {
                "id": f"primality/{i:04d}",
                "family": "primality",
                "prompts": [p.format(n=n) for p in PARAPHRASES],
                "answer": {"type": "boolean", "value": ans},
                "meta": {"n": n, "class": kind, "seed": SEED},
            }
            f.write(json.dumps(rec) + "\n")

    n_pos = sum(1 for _, a, _ in records if a)
    print(f"wrote {len(records)} tasks -> {out}")
    print(f"  positive class (prime):     {n_pos}")
    print(f"  negative class (composite): {len(records) - n_pos}")
    assert n_pos == len(records) - n_pos, "class balance is the whole point"
    print(f"  balance check: PASS")
    print(f"  hardest composites: {composites_l[-3:]}")


if __name__ == "__main__":
    main()
