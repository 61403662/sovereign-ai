from __future__ import annotations

import re
from enum import Enum

MATERIAL_CODE_PATTERN = re.compile(r"M-[A-Z0-9\-]+", re.I)


class BomIntent(str, Enum):
    LIST_BOM = "list_bom"
    LIST_MODELS = "list_models"
    ESTIMATE_COST = "estimate_cost"
    CHEAPEST_SUPPLIER = "cheapest_supplier"
    UNKNOWN = "unknown"


def classify_bom_question(question: str) -> BomIntent:
    q = (question or "").strip()
    if not q:
        return BomIntent.UNKNOWN
    lower = q.lower()
    if MATERIAL_CODE_PATTERN.search(q) and any(
        k in q for k in ("便宜", "最低价", "哪家", "供应商")
    ):
        return BomIntent.CHEAPEST_SUPPLIER
    if re.search(r"哪些.{0,8}型号|型号列表|都有哪些型号", q):
        return BomIntent.LIST_MODELS
    if "型号" in q and any(k in q for k in ("风机型号", "样例库")):
        return BomIntent.LIST_MODELS
    if any(k in q for k in ("多少钱", "材料费", "材料费用", "成本", "总价", "估算", "价格")):
        return BomIntent.ESTIMATE_COST
    if "bom" in lower or "物料" in q or "有哪些料" in q or "清单" in q:
        return BomIntent.LIST_BOM
    if re.search(r"XF-\d{3}", q, re.I) and any(k in q for k in ("料", "BOM", "bom", "组成")):
        return BomIntent.LIST_BOM
    return BomIntent.UNKNOWN


def extract_material_code(question: str) -> str | None:
    m = MATERIAL_CODE_PATTERN.search(question or "")
    return m.group(0).upper() if m else None