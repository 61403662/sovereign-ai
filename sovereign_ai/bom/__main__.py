from __future__ import annotations

import argparse
import sys

from sovereign_ai.bom.db import init_database
from sovereign_ai.bom.import_csv import import_csv_directory, resolve_csv_dir
from sovereign_ai.bom.runner import answer_bom_question
from sovereign_ai.paths import repo_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 2 BOM/SQL answers (read-only SQLite)")
    parser.add_argument("question", nargs="?", help="Question in Chinese")
    parser.add_argument("--init", action="store_true", help="Create storage/sqlite/fan_bom.db from schema + sample seed")
    parser.add_argument(
        "--import-csv",
        nargs="?",
        const="",
        metavar="DIR",
        help="Load schema + CSVs (default: SOVEREIGN_BOM_CSV_DIR or data/samples/fan/csv)",
    )
    parser.add_argument("--reset", action="store_true", help="With --init / --import-csv, delete existing DB first")
    args = parser.parse_args(argv)

    if args.import_csv is not None:
        csv_dir = resolve_csv_dir() if args.import_csv == "" else args.import_csv
        path = import_csv_directory(csv_dir, reset=args.reset)
        print(f"Imported CSV → {path}")
        return 0

    if args.init:
        path = init_database(repo_root(), reset=args.reset)
        print(f"Initialized: {path}")
        return 0

    if not args.question:
        parser.error("question is required unless --init")

    result = answer_bom_question(args.question)
    if not result["ok"]:
        print(result.get("error") or "failed", file=sys.stderr)
        return 1
    print(result["answer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())