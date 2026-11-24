from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Define paths relative to this script.
BASE = Path(__file__).resolve().parent

ARIMA_FILE = BASE / "arima_results" / "total_summary.csv"
ARIMAX_FILE = BASE / "arimax_results" / "total_summary_arimax.csv"

OUTPUT_DIR = BASE / "plot_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load model summaries.
df_arima = pd.read_csv(ARIMA_FILE)
df_arimax = pd.read_csv(ARIMAX_FILE)

# Figure 1: Distribution of ARIMA AIC values.
plt.figure(figsize=(10, 6))
plt.hist(df_arima["AIC"], bins=30, edgecolor="black")
plt.title("Distribution of ARIMA AIC")
plt.xlabel("AIC")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "arima_AIC_distribution.png")
plt.close()

# Figure 2: Distribution of ARIMAX AIC values.
plt.figure(figsize=(10, 6))
plt.hist(
    df_arimax["AIC"],
    bins=30,
    edgecolor="black",
    color="green"
)
plt.title("Distribution of ARIMAX AIC")
plt.xlabel("AIC")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "arimax_AIC_distribution.png")
plt.close()

# Figure 3: Boxplots of ARIMAX coefficients.
coef_cols = [
    "coef_overall",
    "coef_age",
    "coef_attacking",
    "coef_skill",
    "coef_movement",
    "coef_power",
    "coef_mentality",
    "coef_defending"
]

plt.figure(figsize=(12, 7))
df_arimax[coef_cols].boxplot()
plt.title("Distribution of ARIMAX Coefficients")
plt.ylabel("Coefficient Value")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "arimax_coeff_boxplot.png")
plt.close()

print("All plots saved to:", OUTPUT_DIR)