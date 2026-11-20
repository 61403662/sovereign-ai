from __future__ import annotations

from typing import Any

from sovereign_ai.bom.db import connect, database_ready
from sovereign_ai.bom.queries import (
    cheapest_supplier_for_material,
    estimate_material_cost,
    extract_model_code,
    list_bom,
    list_fan_models,
)
from sovereign_ai.bom.router import BomIntent, classify_bom_question, extract_material_code
from sovereign_ai.paths import repo_root as _repo_root


def answer_bom_question(question: str, root=None) -> dict[str, Any]:
    root = root or _repo_root()
    if not database_ready(root):
        return {
            "ok": False,
            "route": "sql",
            "error": "BOM 库未初始化。请运行: python -m sovereign_ai.bom --init",
            "answer": "",
        }

    intent = classify_bom_question(question)
    conn = connect(root)
    try:
        if intent == BomIntent.CHEAPEST_SUPPLIER:
            code = extract_material_code(question)
            if not code:
                return {"ok": False, "route": "sql", "error": "未识别材料编码（如 M-BLADE-ABS）", "answer": ""}
            result = cheapest_supplier_for_material(conn, code)
            if not result["ok"]:
                return {"ok": False, "route": "sql", "error": result["error"], "answer": ""}
            ans = (
                f"材料 {result['material_name']}（{code}）截至 {result['as_of']} 最低报价："
                f"{result['supplier_name']}（{result['supplier_code']}）"
                f" {result['unit_price']} {result['currency']}/单位。"
            )
            return {"ok": True, "route": "sql", "intent": intent.value, "answer": ans, "data": result}

        if intent == BomIntent.LIST_MODELS:
            models = list_fan_models(conn)
            if not models:
                return {"ok": False, "route": "sql", "error": "fan_model 表为空", "answer": ""}
            body = ["样例库当前型号："]
            for m in models:
                body.append(f"- {m['model_code']} {m['name']}（rev {m['revision']}）")
            body.append("（数据来源：本机 SQLite）")
            return {
                "ok": True,
                "route": "sql",
                "intent": intent.value,
                "answer": "\n".join(body),
                "data": {"models": models},
            }

        model = extract_model_code(question)
        if not model:
            return {
                "ok": False,
                "route": "sql",
                "error": "未识别型号（如 XF-120）。BOM/SQL 问题请写明型号或材料编码。",
                "answer": "",
            }

        if intent == BomIntent.ESTIMATE_COST:
            result = estimate_material_cost(conn, model)
            if not result["ok"]:
                return {"ok": False, "route": "sql", "error": result["error"], "answer": "", "data": result}
            lines = result["lines"]
            body = [f"型号 {model} 单机材料费（按各料最低有效报价 × 用量，截至 {result['as_of']}）："]
            for ln in lines:
                body.append(
                    f"- {ln['material_name']} × {ln['qty']}{ln['unit']} @ {ln['unit_price']} → {ln['line_cost']} {ln['currency']}"
                )
            body.append(f"合计：{result['total']} {result['currency']}（虚构样例数据，仅供演示）。")
            return {
                "ok": True,
                "route": "sql",
                "intent": intent.value,
                "answer": "\n".join(body),
                "data": result,
            }

        if intent == BomIntent.LIST_BOM:
            rows = list_bom(conn, model)
            if not rows:
                return {"ok": False, "route": "sql", "error": f"无 BOM: {model}", "answer": ""}
            body = [f"{model} BOM（单机用量）："]
            for r in rows:
                body.append(f"- {r.material_code} {r.material_name}: {r.qty_per_unit} {r.unit}")
            body.append("（数据来源：本机 SQLite，非模型臆测）")
            return {
                "ok": True,
                "route": "sql",
                "intent": BomIntent.LIST_BOM.value,
                "answer": "\n".join(body),
                "data": {"model_code": model, "lines": [r.__dict__ for r in rows]},
            }

        return {
            "ok": False,
            "route": "sql",
            "error": "无法处理此 BOM 问题（请写明型号 XF-xxx 或材料编码 M-…）",
            "answer": "",
        }
    finally:
        conn.close()