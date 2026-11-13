# Operation Zero Human — Moonlight in a Teacup

Original AI-assisted coding contest entry candidate, created 2026-11-13.

Public repository for the [make.fun cutest picture bounty](https://make.fun/bounty/cutest-picture-01). Illustration: an orange fox and a bunny in a pink teacup beneath a starry crescent-moon sky.

## Competition runtime (stdlib-only, Python 3.13, offline)

    python main.py                        # writes /output/entry.png
    MAKEFUN_OUTPUT_DIR=/tmp/demo python main.py

The entrypoint copies a checked-in 1024 × 1024 PNG, does not access a network, needs no pip packages, and writes identical bytes on each run.

## Build artwork / tests (outside sandbox)

    python -m pip install pillow==11.3.0 cairosvg==2.8.2
    python build_art.py                   # generates entry.png and artwork.svg
    python -m unittest -v test_entry.py

A GitHub Actions workflow runs those build and test commands on public GitHub runner and commits generated assets. The contest runtime does not run the build step or require CairoSVG/Pillow.

## Authenticity and submission status

- This is original artwork and an original reproducible code entry. MIT licensed.
- Announced bounty: 250 USDC Solana escrow, to be split among top 20 ranked entries.
- Submission deadline: 2026-11-13 10:00 UTC.
- GitHub upload **does not submit** to make.fun. Platform still requires legitimate login, wallet signature, and actual AI coding-session transcripts. No fabricated transcripts will be supplied.
- No private key, seed phrase, customer data, or Frantic project dependencies.
- Actual owner payout: **0.00 USDC** until a transaction or trusted platform receipt proves otherwise.

See [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md) for funding links, tests, blockers and accurate financial status.
