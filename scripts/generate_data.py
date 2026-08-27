import argparse

from app.domain.synthetic.generator import DatasetGenerator
from app.domain.synthetic.serialization import write_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic reconciliation dataset."
    )

    parser.add_argument(
        "--records",
        type=int,
        default=400,
        help="Number of settlement records to generate.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible dataset generation.",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="data",
        help="Directory where generated dataset files will be written.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    generator = DatasetGenerator(
        records=args.records,
        seed=args.seed,
    )

    dataset = generator.generate()

    write_dataset(
        dataset,
        args.output,
    )

    print(f"Generated {len(dataset.settlements)} settlements.")
    print(f"Generated {len(dataset.ledger_records)} ledger records.")
    print(f"Output directory: {args.output}")


if __name__ == "__main__":
    main()