-- Fictional small-fan BOM schema (Phase 2). Safe to commit.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS fan_model (
  model_code TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  revision TEXT NOT NULL DEFAULT 'A'
);

CREATE TABLE IF NOT EXISTS material (
  material_code TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  unit TEXT NOT NULL DEFAULT 'pcs'
);

CREATE TABLE IF NOT EXISTS bom_line (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_code TEXT NOT NULL REFERENCES fan_model(model_code),
  material_code TEXT NOT NULL REFERENCES material(material_code),
  qty_per_unit REAL NOT NULL CHECK (qty_per_unit > 0),
  UNIQUE (model_code, material_code)
);

CREATE TABLE IF NOT EXISTS supplier (
  supplier_code TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  contact TEXT
);

CREATE TABLE IF NOT EXISTS supplier_offer (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  material_code TEXT NOT NULL REFERENCES material(material_code),
  supplier_code TEXT NOT NULL REFERENCES supplier(supplier_code),
  unit_price REAL NOT NULL CHECK (unit_price >= 0),
  currency TEXT NOT NULL DEFAULT 'CNY',
  valid_from TEXT NOT NULL,
  valid_to TEXT,
  UNIQUE (material_code, supplier_code, valid_from)
);

CREATE INDEX IF NOT EXISTS idx_bom_model ON bom_line(model_code);
CREATE INDEX IF NOT EXISTS idx_offer_material ON supplier_offer(material_code);