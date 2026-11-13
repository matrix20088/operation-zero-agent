# Operation Zero — Moonlight Teacup

An independently generated, original illustration of a sleeping fox and a bunny curled inside a teacup under the moon.

**Bounty candidate:** [Make the cutest picture](https://make.fun/bounty/cutest-picture-01) — a competitive pool of **250 USDC (Solana)** for the 20 best judged submissions, **not** a guaranteed payment.

## Reproduce the entry

Requires **Python 3.13** (standard library only; works on Python 3.12 as well). Network access is not required.

```sh
MAKEFUN_OUTPUT_DIR=. python main.py
python -m unittest -v test_entry
```

The entry writes a deterministic `entry.png` (640×640 pixels, 30,846 bytes, SHA-256 `91c38983d18f04fa88dd2b60948ac0b7879ff9f85fee4a9d5e7ca203e3ec767b`). In the bounty sandbox it writes to `/output/entry.png` by default. The output is below 1 MiB.

The public repository is licensed under MIT; the picture is original work. An optional [GitHub Actions check](.github/workflows/test-entry.yml) runs the offline unit test and commits a preview PNG if repository permissions allow.

## Status and authenticity

**Candidate code ready, not submitted to make.fun. Actual received payout: 0.00 USDC.**

The bounty requires authentic coding-agent session logs with usage records and a signed account submission; exports of ChatGPT conversations are **not accepted** according to its [official instructions](https://make.fun/skill.md). No fake logs, credentials or payout claims are included. See [experiment log](EXPERIMENT_LOG.md).

The account holder created this repository; the code was authored and moved here by the ChatGPT assistant with the owner's approval. No private business data, keys, payments or paid services were used.
