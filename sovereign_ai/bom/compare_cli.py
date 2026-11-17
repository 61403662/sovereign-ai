"""Print template vs LLM-formatted SQL answers side by side (screenshot-friendly)."""

from __future__ import annotations

import argparse
import sys

from sovereign_ai.bom.nl_format import compare_template_and_nl


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare BOM template answer vs Ollama natural-language (sql_nl_format)"
    )
    parser.add_argument("question", help='e.g. "做一台 XF-120 材料费多少钱？"')
    args = parser.parse_args(argv)

    result = compare_template_and_nl(args.question)
    if not result.get("ok"):
        print(result.get("error") or "BOM query failed", file=sys.stderr)
        return 1

    print("[route: sql]")
    print()
    print("—— 模板（sql_nl_format: false / python -m sovereign_ai.bom）——")
    print(result["template"])
    print()
    print("—— 自然语言（Ollama 润色，数字仍以 DB 为准）——")
    print(result["natural"])
    if result.get("same_template_fallback"):
        print()
        print("（注意：润色未生效或 Ollama 失败，已回退为模板。请检查 ollama list / chat 模型。）")
    elif result.get("nl_looks_like_template"):
        print()
        print(
            "（注意：Ollama 有响应，但仍是清单体，与模板几乎一样。"
            "请 git pull 最新 prompt 后再试；或换更大 chat 模型。）"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())