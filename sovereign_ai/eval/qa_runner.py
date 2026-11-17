"""Run questions from eval/*.jsonl against ask_question and check expectations."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Callable

from sovereign_ai.eval.grading import QaCase, QaVerdict, grade_case, load_jsonl
from sovereign_ai.paths import repo_root


def run_qa_file(
    path: Path,
    ask_fn: Callable[[str], dict[str, Any]] | None = None,
) -> list[QaVerdict]:
    if ask_fn is None:
        from sovereign_ai.ask.runner import ask_question

        ask_fn = ask_question
    cases = load_jsonl(path)
    return [grade_case(c, ask_fn(c.question)) for c in cases]


def _run_paths(paths: list[Path], quiet: bool) -> int:
    total_passed = 0
    total_cases = 0
    exit_code = 0
    for path in paths:
        if not path.is_file():
            print(f"missing file: {path}", file=sys.stderr)
            return 2
        verdicts = run_qa_file(path)
        passed = sum(1 for v in verdicts if v.passed)
        failed = len(verdicts) - passed
        total_passed += passed
        total_cases += len(verdicts)
        if failed:
            exit_code = 1
        for v in verdicts:
            status = "PASS" if v.passed else "FAIL"
            if not quiet or not v.passed:
                print(f"[{status}] L{v.case.line_no}: {v.case.question}")
                if not v.passed:
                    print(f"        {v.detail}")
        print(f"\n{passed}/{len(verdicts)} passed, {failed} failed — {path.name}\n")
    print(f"=== total {total_passed}/{total_cases} passed ===")
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run eval/*.jsonl against local RAG")
    parser.add_argument(
        "jsonl",
        nargs="?",
        default=None,
        help="Path to qa JSONL (default: eval/qa.sample.jsonl)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run eval/qa.sample.jsonl then eval/fan_qa.example.jsonl",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Only print summary")
    args = parser.parse_args(argv)

    root = repo_root()
    if args.all:
        paths = [root / "eval" / "qa.sample.jsonl", root / "eval" / "fan_qa.example.jsonl"]
        return _run_paths(paths, args.quiet)

    path = Path(args.jsonl) if args.jsonl else root / "eval" / "qa.sample.jsonl"
    return _run_paths([path], args.quiet)