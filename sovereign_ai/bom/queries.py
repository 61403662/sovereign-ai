from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Any

MODEL_PATTERN = re.compile(r"XF-\d{3}", re.I)


@dataclass
class BomRow:
    material_code: str
    material_name: str
    unit: str
    qty_per_unit: float


def extract_model_code(question: str) -> str | None:
    m = MODEL_PATTERN.search(question or "")
    return m.group(0).upper() if m else None


def list_bom(conn: sqlite3.Connection, model_code: str) -> list[BomRow]:
    rows = conn.execute(
        """
        SELECT b.material_code, m.name AS material_name, m.unit, b.qty_per_unit
        FROM bom_line b
        JOIN material m ON m.material_code = b.material_code
        WHERE b.model_code = ?
        ORDER BY b.material_code
        """,
        (model_code,),
    ).fetchall()
    return [
        BomRow(
            material_code=r["material_code"],
            material_name=r["material_name"],
            unit=r["unit"],
            qty_per_unit=float(r["qty_per_unit"]),
        )
        for r in rows
    ]


def _today() -> str:
    return date.today().isoformat()


def estimate_material_cost(
    conn: sqlite3.Connection,
    model_code: str,
    as_of: str | None = None,
) -> dict[str, Any]:
    """Per-material min valid offer * qty; sum for total (fictional demo rule)."""
    as_of = as_of or _today()
    lines = list_bom(conn, model_code)
    if not lines:
        return {"ok": False, "error": f"未知型号或无 BOM: {model_code}", "lines": [], "total": 0.0}

    detail: list[dict[str, Any]] = []
    total = 0.0
    missing: list[str] = []

    for line in lines:
        offer = conn.execute(
            """
            SELECT o.unit_price, o.currency, o.supplier_code, s.name AS supplier_name
            FROM supplier_offer o
            JOIN supplier s ON s.supplier_code = o.supplier_code
            WHERE o.material_code = ?
              AND o.valid_from <= ?
              AND (o.valid_to IS NULL OR o.valid_to >= ?)
            ORDER BY o.unit_price ASC
            LIMIT 1
            """,
            (line.material_code, as_of, as_of),
        ).fetchone()
        if not offer:
            missing.append(line.material_code)
            continue
        unit_price = float(offer["unit_price"])
        line_cost = unit_price * line.qty_per_unit
        total += line_cost
        detail.append(
            {
                "material_code": line.material_code,
                "material_name": line.material_name,
                "qty": line.qty_per_unit,
                "unit": line.unit,
                "unit_price": unit_price,
                "currency": offer["currency"],
                "supplier_code": offer["supplier_code"],
                "supplier_name": offer["supplier_name"],
                "line_cost": round(line_cost, 4),
            }
        )

    if missing:
        return {
            "ok": False,
            "error": f"缺少有效报价: {', '.join(missing)}",
            "lines": detail,
            "total": round(total, 2),
            "model_code": model_code,
            "as_of": as_of,
        }

    return {
        "ok": True,
        "error": None,
        "model_code": model_code,
        "as_of": as_of,
        "currency": detail[0]["currency"] if detail else "CNY",
        "lines": detail,
        "total": round(total, 2),
    }


def cheapest_supplier_for_material(
    conn: sqlite3.Connection,
    material_code: str,
    as_of: str | None = None,
) -> dict[str, Any]:
    as_of = as_of or _today()
    row = conn.execute(
        """
        SELECT o.unit_price, o.currency, o.supplier_code, s.name AS supplier_name,
               m.name AS material_name
        FROM supplier_offer o
        JOIN supplier s ON s.supplier_code = o.supplier_code
        JOIN material m ON m.material_code = o.material_code
        WHERE o.material_code = ?
          AND o.valid_from <= ?
          AND (o.valid_to IS NULL OR o.valid_to >= ?)
        ORDER BY o.unit_price ASC
        LIMIT 1
        """,
        (material_code, as_of, as_of),
    ).fetchone()
    if not row:
        return {"ok": False, "error": f"无有效报价: {material_code}"}
    return {
        "ok": True,
        "material_code": material_code,
        "material_name": row["material_name"],
        "supplier_code": row["supplier_code"],
        "supplier_name": row["supplier_name"],
        "unit_price": float(row["unit_price"]),
        "currency": row["currency"],
        "as_of": as_of,
    }