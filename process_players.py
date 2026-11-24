from pathlib import Path

import pandas as pd
import numpy as np

# Define paths relative to this script.
BASE = Path(__file__).resolve().parent
data_path = BASE / "data"
output_path = BASE / "data2"

output_path.mkdir(parents=True, exist_ok=True)

# Collect input CSV files.
files = sorted(data_path.glob("*.csv"))

for file_path in files:
    df = pd.read_csv(file_path)

    # Convert monthly date strings to the first day of each month.
    df["date"] = df["date"].astype(str).str.replace("'", "", regex=False)
    df["date"] = df["date"].apply(
        lambda x: x.replace(".", "-") + "-01"
    )
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    # Approximate age in completed years using 365 days per year.
    df["dob"] = pd.to_datetime(df["dob"])
    df["age"] = np.floor((df["date"] - df["dob"]).dt.days / 365)

    # Use the first listed position as the primary position.
    df["position"] = df["positions"].astype(str).apply(
        lambda x: x.split(",")[0].strip()
    )

    # Identify individual attributes within each category.
    attacking_cols = [c for c in df.columns if c.startswith("attacking_")]
    skill_cols = [c for c in df.columns if c.startswith("skill_")]
    movement_cols = [c for c in df.columns if c.startswith("movement_")]
    power_cols = [c for c in df.columns if c.startswith("power_")]
    mentality_cols = [c for c in df.columns if c.startswith("mentality_")]
    defending_cols = [c for c in df.columns if c.startswith("defending_")]

    # Calculate category averages, excluding missing values.
    df["attacking"] = df[attacking_cols].mean(axis=1, skipna=True)
    df["skill"] = df[skill_cols].mean(axis=1, skipna=True)
    df["movement"] = df[movement_cols].mean(axis=1, skipna=True)
    df["power"] = df[power_cols].mean(axis=1, skipna=True)
    df["mentality"] = df[mentality_cols].mean(axis=1, skipna=True)
    df["defending"] = df[defending_cols].mean(axis=1, skipna=True)

    # Calculate the natural logarithm of Transfermarkt values.
    # Input values must be positive.
    df["log_tm"] = np.log(df["transfermarkt_value"])

    # Select columns for the processed dataset.
    output_cols = [
        "date",
        "name",
        "transfermarkt_value",
        "log_tm",
        "overall_rating",
        "potential",
        "age",
        "position",
        "attacking",
        "skill",
        "movement",
        "power",
        "mentality",
        "defending"
    ]

    df_out = df[output_cols]

    # Save each player's processed data to a separate CSV file.
    base_name = file_path.name.split("_sofifa_ratings")[0]
    new_name = base_name + "_processed_data.csv"

    df_out.to_csv(
        output_path / new_name,
        index=False,
        encoding="utf-8"
    )

    print("Saved:", new_name)

print("Processing complete. Results saved to:", output_path)