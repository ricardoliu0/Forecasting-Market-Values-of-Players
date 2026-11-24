# One-time cleanup script: each run permanently removes the first data row.

import pandas as pd
from pathlib import Path

data_dir = Path(__file__).resolve().parent / "data"

csv_files = sorted(data_dir.glob("*.csv"))
print("Found CSV files:", len(csv_files))

for idx, file_path in enumerate(csv_files, start=1):
    print(f"[{idx}/{len(csv_files)}] Processing {file_path.name} ...")

    df = pd.read_csv(file_path, encoding="utf-8")

    if len(df) > 1:
        df = df.drop(df.index[0])  # Remove the first data row (CSV row 2 after the header)
        df = df.reset_index(drop=True)

        df.to_csv(file_path, index=False, encoding="utf-8")
        print("  → Deleted row 2.\n")
    else:
        print("  → File too short, skipped.\n")

print("\n=== DONE: Deleted row 2 in all CSV files ===")
