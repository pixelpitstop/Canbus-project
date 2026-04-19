"""CLI pipeline utilities for CANInsight decoding workflows."""

from __future__ import annotations

import argparse

import pandas as pd

from src.decoder import decode_dataframe


def decode_csv(input_path: str, output_path: str) -> None:
    """Load raw CAN CSV, decode signals, and write decoded CSV."""
    raw_df = pd.read_csv(input_path)
    decoded_df = decode_dataframe(raw_df)
    decoded_df.to_csv(output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Decode raw CAN CSV into signal-level CSV")
    parser.add_argument("--in", dest="input_path", required=True, help="Path to input raw CAN CSV")
    parser.add_argument("--out", dest="output_path", required=True, help="Path to output decoded CSV")
    args = parser.parse_args()

    decode_csv(args.input_path, args.output_path)
    print(f"Decoded {args.input_path} -> {args.output_path}")


if __name__ == "__main__":
    main()
