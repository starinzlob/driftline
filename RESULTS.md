# Baseline — 2026-07-16

First real run. Six frontier models, the full 30-task balanced primality set,
terse + step-by-step, one sample each (k=1), served through the Unify/FluxA proxy.
360 calls, zero errors. Raw responses are all in `runs/2026-07-16/`.

**This is a baseline, not a drift measurement.** k=1 means point estimates with
real sampling noise and no confidence intervals. Nothing here is called drift —
drift detection needs a second run to compare against. Read the numbers as "the
structure the instrument sees on day one," not "model X is good/bad."

## Behavior vs capability

| model | behavior (terse) | capability (best-of-N) | gap | answer bias (yes) | recall+ / recall− |
|---|---|---|---|---|---|
| openai/gpt-5.4 | 60.0% | **96.7%** | +36.7 | 30% (→ "not prime") | 40% / 80% |
| anthropic/claude-sonnet-4.6 | 66.7% | 90.0% | +23.3 | 83% (→ "prime") | 100% / 33% |
| google/gemini-3.1-pro-preview | 56.7% | 73.3% | +16.7 | 57% | 67% / 47% |
| google/gemini-3.5-flash | 76.7% | 86.7% | +10.0 | 27% (→ "not prime") | 53% / 100% |
| anthropic/claude-opus-4.6 | 86.7% | 90.0% | +3.3 | 63% (→ "prime") | 100% / 73% |
| openai/gpt-5.5 | 96.7% | 100.0% | +3.3 | 53% | 100% / 93% |

`behavior` = accuracy on the terse canonical prompt (what a user types).
`capability` = best-of-N across the frozen paraphrases (can the model do it at all).

## What day one shows

**The 2023 confound is alive in 2026.** Score gpt-5.4 the way the original
["GPT-4 is getting worse"](https://news.ycombinator.com/item?id=36815594) paper did
— terse prompt, primes only — and you get 40% (the recall+ column). It looks broken.
Its actual capability is 96.7%. The gap between the terse behavior and the reasoned
capability is exactly the artifact that made the 2023 paper wrong, reproduced here in
live data by an instrument built to separate the two.

**Vendor answer-priors diverge sharply.** On the terse prompt, Anthropic's models
lean toward calling a number prime (bias 63–83% yes) while OpenAI's and Google's
cheaper models lean the other way (27–30% yes). That is a prior, not a capability —
and telling those apart is the entire point of balanced classes plus a separate
answer-bias metric. A prime-only test set could not see it.

**Snapshot swap detection is blind here.** Through this proxy path, all six vendors
echo the requested alias rather than returning a dated snapshot, so a silent
alias→weights swap could not be detected from the returned model string. Recorded as
a limitation, not worked around.

## Reproduce

```bash
python3 scripts/report.py --date 2026-07-16   # re-score from raw responses
```

Or throw out our graders entirely and score `runs/2026-07-16/*/*.json` yourself.
That is the point (METHODOLOGY.md Rule 5).

## Honest limits on this run

- **k=1.** No confidence intervals. The large behavior/capability gaps (20–37 pts)
  are almost certainly real; individual point values are noisy. Rule 7 is not
  satisfied by this run and it is labeled accordingly.
- **`capability` saturates** (METHODOLOGY.md § Known defects) — trustworthy as
  evidence a capability is intact, weak as evidence one is lost.
- **Proxy-served.** See METHODOLOGY.md § The proxy caveat.
- **30 tasks, one domain.** Small and narrow by design for a first run.
