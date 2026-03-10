# -*- coding: utf-8 -*-
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Find "Выгрузка XLSX (2).xlsx" (рассылка from 1C) — stem contains "XLSX (2)"
candidates = list(PROJECT_ROOT.glob("*.xlsx"))
target = None
for f in candidates:
    if "XLSX (2)" in f.name:  # exact pattern in filename (not just .xlsx)
        target = f
        break
if not target:
    target = max(candidates, key=lambda p: p.stat().st_mtime)

print("Using file:", target.name, "path:", target)

import pandas as pd
xl = pd.ExcelFile(target)
print("SHEETS:", len(xl.sheet_names))
print(xl.sheet_names)

for sh in xl.sheet_names:
    df = pd.read_excel(target, sheet_name=sh, header=0)
    print()
    print("=== ", sh, " ===", df.shape[0], "x", df.shape[1])
    print("COLUMNS:", list(df.columns))
    print("Sample row 1:", df.iloc[0].astype(str).tolist())
    print("Sample row -2:", df.iloc[-2].astype(str).tolist())
