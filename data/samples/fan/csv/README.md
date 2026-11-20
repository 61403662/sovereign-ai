# Fan BOM CSV (fictional sample)

Filenames (load order): `fan_model.csv`, `material.csv`, `supplier.csv`, `bom_line.csv`, `supplier_offer.csv`.

Sample import (repo):

```powershell
.\scripts\bom-import.cmd
```

**Private exports (real data, gitignored):** copy the same five files into `data\private\fan\csv\`, then:

```powershell
.\scripts\bom-import-private.cmd
```

Do not commit `data/private/`.