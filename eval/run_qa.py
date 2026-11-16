#!/usr/bin/env python3
"""Thin wrapper: python eval/run_qa.py [eval/qa.sample.jsonl]"""

from sovereign_ai.eval.qa_runner import main

if __name__ == "__main__":
    raise SystemExit(main())