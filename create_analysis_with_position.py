import os
import pandas as pd
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent

DATA2_DIR = os.path.join(BASE, "data2")
ARIMAX_FILE = os.path.join(
    BASE, "arimax_results", "total_summary_arimax.csv"
)

OUTPUT_DIR = os.path.join(BASE, "analysis_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Load the ARIMAX summary.
arimax = pd.read_csv(ARIMAX_FILE)

# 2. Build a mapping between players and their positions.
position_records = []

for fname in os.listdir(DATA2_DIR):
    if fname.endswith(".csv"):
        full_path = os.path.join(DATA2_DIR, fname)
        df = pd.read_csv(full_path)

        # Extract the player identifier from the filename.
        # Example: A_Bastoni_237383_processed_data.csv
        base = fname.replace("_processed_data.csv", "")
        player = base

        # Extract the trailing numeric SoFIFA ID.
        m = re.search(r"_(\d+)$", player)
        if m:
            pid = m.group(1)
        else:
            continue

        # Use the first row's position, assuming it is constant.
        if "position" in df.columns:
            pos = df["position"].iloc[0]
        else:
            pos = None

        position_records.append([player, pid, pos])

position_map = pd.DataFrame(
    position_records,
    columns=["player", "sofifa_id", "position"]
)

# 3. Merge position information into the ARIMAX summary.
merged = arimax.merge(position_map, on="player", how="left")

merged.to_csv(
    os.path.join(OUTPUT_DIR, "final_arimax_with_position.csv"),
    index=False
)
print("Saved final_arimax_with_position.csv")

# 4. Calculate mean coefficients by position.
ability_cols = [c for c in arimax.columns if c.startswith("coef_")]

position_stats = merged.groupby("position")[ability_cols].mean()
position_stats.to_csv(
    os.path.join(OUTPUT_DIR, "correct_position_summary.csv")
)
print("Saved correct_position_summary.csv")

# 5. Flag players with any coefficient whose absolute value exceeds 3.
mask = (merged[ability_cols].abs() > 3).any(axis=1)
outliers = merged[mask]
outliers.to_csv(
    os.path.join(OUTPUT_DIR, "outlier_players.csv"),
    index=False
)
print("Saved outlier_players.csv")

print("Analysis complete.")