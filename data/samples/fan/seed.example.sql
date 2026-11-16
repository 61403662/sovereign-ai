-- Fictional seed for demos. Loaded into storage/sqlite/fan_bom.db by bom-init.
INSERT OR REPLACE INTO fan_model (model_code, name, revision) VALUES
  ('XF-120', '小型桌面风扇 120mm', 'A'),
  ('XF-200', '小型桌面风扇 200mm', 'B');

INSERT OR REPLACE INTO material (material_code, name, unit) VALUES
  ('M-BLADE-ABS', 'ABS 扇叶', 'pcs'),
  ('M-MOTOR-DC', '直流电机组件', 'pcs'),
  ('M-GRILLE-PP', '前网罩 PP', 'pcs'),
  ('M-SCREW-M3', 'M3 自攻螺钉', 'pcs'),
  ('M-CABLE-1M', '电源线 1m', 'pcs');

INSERT OR REPLACE INTO bom_line (model_code, material_code, qty_per_unit) VALUES
  ('XF-120', 'M-BLADE-ABS', 1),
  ('XF-120', 'M-MOTOR-DC', 1),
  ('XF-120', 'M-GRILLE-PP', 1),
  ('XF-120', 'M-SCREW-M3', 4),
  ('XF-120', 'M-CABLE-1M', 1),
  ('XF-200', 'M-BLADE-ABS', 1),
  ('XF-200', 'M-MOTOR-DC', 1),
  ('XF-200', 'M-GRILLE-PP', 1),
  ('XF-200', 'M-SCREW-M3', 6),
  ('XF-200', 'M-CABLE-1M', 1);

INSERT OR REPLACE INTO supplier (supplier_code, name, contact) VALUES
  ('SUP-ALPHA', '阿尔法塑件', 'demo-alpha@example.com'),
  ('SUP-BETA', '贝塔机电', 'demo-beta@example.com');

DELETE FROM supplier_offer;
INSERT INTO supplier_offer (material_code, supplier_code, unit_price, currency, valid_from, valid_to) VALUES
  ('M-BLADE-ABS', 'SUP-ALPHA', 2.80, 'CNY', '2025-01-01', NULL),
  ('M-BLADE-ABS', 'SUP-BETA', 3.10, 'CNY', '2025-06-01', NULL),
  ('M-MOTOR-DC', 'SUP-BETA', 18.50, 'CNY', '2025-01-01', NULL),
  ('M-GRILLE-PP', 'SUP-ALPHA', 1.20, 'CNY', '2025-01-01', NULL),
  ('M-SCREW-M3', 'SUP-ALPHA', 0.05, 'CNY', '2025-01-01', NULL),
  ('M-CABLE-1M', 'SUP-BETA', 4.00, 'CNY', '2025-01-01', NULL);