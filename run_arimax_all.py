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
output_path = BASE / "arimax_results"
output_path.mkdir(parents=True, exist_ok=True)

# Collect processed player datasets.
files = sorted(data2_path.glob("*_processed_data.csv"))
total_files = len(files)
summary_rows = []

feature_cols = [
    "overall_rating",
    "age",
    "attacking",
    "skill",
    "movement",
    "power",
    "mentality",
    "defending"
]

for idx, file_path in enumerate(files, start=1):
    print("Processing:", file_path.name, f"{idx}/{total_files}")

    # Load the response series and explanatory variables.
    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    y = df["log_tm"]
    X = df[feature_cols]

    # Define candidate ARIMAX orders.
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
                exog=X,
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
    out_file = output_path / f"{player_name}_arimax_model.csv"

    # Save parameters, p-values, and model selection results.
    params = best_model.params
    pvalues = best_model.pvalues
    bic = best_model.bic

    df_param = pd.DataFrame({
        "parameter": params.index,
        "value": params.values,
        "pvalue": pvalues.values
    })
    df_param["p"] = best_order[0]
    df_param["d"] = best_order[1]
    df_param["q"] = best_order[2]
    df_param["AIC"] = best_aic
    df_param["BIC"] = bic
    df_param.to_csv(out_file, index=False, encoding="utf-8")

    # Add the selected model and feature coefficients to the summary.
    coefficients = [
        params[name] if name in params else np.nan
        for name in feature_cols
    ]

    summary_rows.append([
        player_name,
        best_order[0],
        best_order[1],
        best_order[2],
        best_aic,
        bic,
        *coefficients
    ])

# Save the combined summary.
summary_df = pd.DataFrame(
    summary_rows,
    columns=[
        "player",
        "p",
        "d",
        "q",
        "AIC",
        "BIC",
        "coef_overall",
        "coef_age",
        "coef_attacking",
        "coef_skill",
        "coef_movement",
        "coef_power",
        "coef_mentality",
        "coef_defending"
    ]
)
summary_df.to_csv(
    output_path / "total_summary_arimax.csv",
    index=False,
    encoding="utf-8"
)

print("Done. Results saved to:", output_path)