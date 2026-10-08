"""Run the reproducible RATC baseline comparison."""

import argparse
from pathlib import Path

from packages.ratc.experiment import MODES, RESEARCH_MODES, run_comparison


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare federated privacy policies.")
    parser.add_argument(
        "--research",
        action="store_true",
        help="Also run the reactive, predictive, and bandit policies.",
    )
    args = parser.parse_args()
    modes = RESEARCH_MODES if args.research else MODES
    summary = run_comparison(
        Path("experiments/logs"),
        seeds=(7,) if args.research else (7, 11),
        rounds=2,
        modes=modes,
    )
    for mode, accuracy in summary.items():
        print(f"{mode}: mean accuracy {accuracy:.4f}")


if __name__ == "__main__":
    main()
