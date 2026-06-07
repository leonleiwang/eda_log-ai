from __future__ import annotations

import argparse
from pathlib import Path

from eda_log_ai.analyzer import analyze_file
from eda_log_ai.render import to_json, to_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze EDA logs with local rules and case retrieval.")
    parser.add_argument("log_file", type=Path, help="Path to an EDA log file.")
    parser.add_argument("--cases", type=Path, default=None, help="Optional path to cases.json.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = analyze_file(args.log_file, case_path=args.cases)
    print(to_json(result) if args.json else to_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
