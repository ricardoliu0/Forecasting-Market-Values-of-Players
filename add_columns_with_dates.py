import pandas as pd
from pathlib import Path

data_dir = Path(__file__).resolve().parent / "data"

# Generate 24 monthly dates from September 2023 to August 2025.
dates = []
year, month = 2023, 9
while not (year == 2025 and month == 9):
    # Prefix with an apostrophe for text display in Excel.
    dates.append("'" + f"{year}.{month:02d}")
    month += 1
    if month == 13:
        month = 1
        year += 1

csv_files = sorted(data_dir.glob("*.csv"))
print("Found CSV files:", len(csv_files))

for idx, file_path in enumerate(csv_files, start=1):
    print(f"[{idx}/{len(csv_files)}] Checking {file_path.name} ...")

    df = pd.read_csv(file_path, encoding="utf-8")

    # Skip files that already contain a date column.
    if "date" in df.columns:
        print("  → Already modified. SKIP.\n")
        continue

    print("  → Not modified. Applying changes...")

    n = len(df)

    # Prepare dates and an empty column for Transfermarkt values.
    date_col = dates[:n] + [""] * (n - len(dates))
    tm_col = [""] * n

    # Insert the two new columns.
    df.insert(1, "date", date_col)
    df.insert(3, "transfermarkt_value", tm_col)

    df.to_csv(file_path, index=False, encoding="utf-8")

    print("  → Done.\n")

print("\n=== FINISHED: Only untouched files were modified ===")