import argparse
import asyncio
import sys
from pathlib import Path

from evaluation.dataset import load_golden_dataset
from evaluation.pipeline import run_ragas_evaluation


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run Ragas evaluation pipeline")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--corpus-id", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--fail-on-threshold", action="store_true")
    args = parser.parse_args()

    dataset = load_golden_dataset(args.dataset)
    report = await run_ragas_evaluation(dataset, args.corpus_id)
    report.save(args.output_dir)
    report.print_summary()

    if args.fail_on_threshold and not report.passed:
        print("Evaluation failed: one or more metrics below threshold")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
