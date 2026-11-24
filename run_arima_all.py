import itertools
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")

# Define paths relative to this script.
BASE = Path(__file__).resolve().parent
data2_path = BASE / "data2"
output_path = BASE / "arima_results"

output_path.mkdir(parents=True, exist_ok=True)

# Collect processed player datasets.
files = sorted(data2_path.glob("*_processed_data.csv"))
total_files = len(files)

summary_rows = []

for idx, file_path in enumerate(files, start=1):
    progress = f"{idx}/{total_files} ({idx / total_files:.2%})"
    print("Processing:", file_path.name, "Progress:", progress)

    # Load the player's log market value series.
    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    y = df["log_tm"]

    # Define candidate ARIMA orders.
    p = range(0, 4)
    d = range(0, 2)
    q = range(0, 4)

    best_aic = np.inf
    best_order = None
    best_model = None

    # Fit candidate models and select the lowest AIC.
    for order in itertools.product(p, d, q):
        try:
            model = SARIMAX(
                y,
                order=order,
                seasonal_order=(0, 0, 0, 0),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            result = model.fit(disp=False)

            if result.aic < best_aic:
                best_aic = result.aic
                best_order = order
                best_model = result

        except Exception:
            continue

    # Skip this player if no candidate model could be selected.
    if best_model is None:
        print(
            f"Skipping {file_path.name}: "
            "no candidate model returned a usable AIC."
        )
        continue

    player_name = file_path.name.replace("_processed_data.csv", "")
    out_file = output_path / f"{player_name}_arima_model.csv"

    # Save parameters and model selection results.
    params = best_model.params
    param_df = pd.DataFrame({
        "parameter": params.index,
        "value": params.values
    })
    param_df["p"] = best_order[0]
    param_df["d"] = best_order[1]
    param_df["q"] = best_order[2]
    param_df["AIC"] = best_aic
    param_df.to_csv(out_file, index=False, encoding="utf-8")

    # Add the selected model to the combined summary.
    summary_rows.append([
        player_name,
        best_order[0],
        best_order[1],
        best_order[2],
        best_aic
    ])

# Save the combined summary for all successfully processed players.
summary_df = pd.DataFrame(
    summary_rows,
    columns=["player", "p", "d", "q", "AIC"]
)
summary_df.to_csv(
    output_path / "total_summary.csv",
    index=False,
    encoding="utf-8"
)

print("Done. Results saved to:", output_path)