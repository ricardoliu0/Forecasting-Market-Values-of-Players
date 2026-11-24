from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define paths relative to this script.
BASE = Path(__file__).resolve().parent

ARIMAX_FILE = BASE / "analysis_results" / "final_arimax_with_position.csv"
POS_SUMMARY_FILE = BASE / "analysis_results" / "correct_position_summary.csv"
OUT_DIR = BASE / "analysis_plots_ARIMAX"

OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load model results and position summaries.
df = pd.read_csv(ARIMAX_FILE)
pos_summary = pd.read_csv(POS_SUMMARY_FILE)

# Exclude selected players from position boxplots only.
# All other plots retain these players.
excluded_players = [
    "Joan_García_259532",
    "M_Ødegaard_222665",
    "Nico_Williams_256516"
]
df_no_outlier = df[~df["player"].isin(excluded_players)]

# Define the coefficient columns.
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

# Figure 1: Distribution of ARIMAX AIC values.
plt.figure(figsize=(10, 6))
sns.histplot(df["AIC"], bins=30, kde=True)
plt.title("ARIMAX AIC Distribution")
plt.xlabel("AIC")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(OUT_DIR / "arimax_AIC_distribution.png", dpi=300)
plt.close()

# Figure 2: Frequency of selected ARIMAX model orders.
df["model_order"] = (
    df["p"].astype(str)
    + "-"
    + df["d"].astype(str)
    + "-"
    + df["q"].astype(str)
)

plt.figure(figsize=(10, 6))
sns.countplot(
    x="model_order",
    data=df,
    order=df["model_order"].value_counts().index
)
plt.title("ARIMAX (p,d,q) Frequency")
plt.xlabel("(p,d,q)")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUT_DIR / "arimax_pdq_counts.png", dpi=300)
plt.close()

# Figure 3: Coefficient distributions across all players.
plt.figure(figsize=(12, 6))
sns.boxplot(data=df[coef_cols])
plt.title("Coefficient Distribution (All Players)")
plt.ylabel("Coefficient Value")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUT_DIR / "arimax_coef_boxplot.png", dpi=300)
plt.close()

# Figure 4: Coefficient distributions by position.
# The selected players listed above are excluded.
for col in coef_cols:
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="position", y=col, data=df_no_outlier)
    plt.title(f"{col} by Position")
    plt.xlabel("Position")
    plt.ylabel("Coefficient Value")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUT_DIR / f"coef_{col}_by_position.png", dpi=300)
    plt.close()

# Figure 5: Mean coefficients by position.
# Use the original position summary, including all players.
heatmap_data = pos_summary.set_index("position")

plt.figure(figsize=(12, 8))
sns.heatmap(
    heatmap_data,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)
plt.title("Mean Coefficient by Position (Heatmap)")
plt.tight_layout()
plt.savefig(OUT_DIR / "position_coef_heatmap.png", dpi=300)
plt.close()

print("All ARIMAX plots saved to:", OUT_DIR)