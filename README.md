# Football Player Valuation Analysis

This independent research project examines the relationship between football players' market valuations and their EA Sports FC/FIFA attributes.

The analysis combines Transfermarkt market valuations with player attributes collected from SoFIFA. Individual ARIMA and ARIMAX models are fitted to log market values, with model orders selected using AIC. The results are summarized across players and playing positions.

## Methods

- ARIMA models describe each player's log market value series.
- ARIMAX models incorporate overall rating, age, and six attribute categories: attacking, skill, movement, power, mentality, and defending.
- Candidate model orders cover p = 0–3, d = 0–1, and q = 0–3.
- Analysis scripts summarize model coefficients by position and generate visualizations.

The coefficients describe model-based associations and should not be interpreted as causal effects.

## Repository Contents

| File | Purpose |
| --- | --- |
| `scrape_player_urls.py` | Collect player profile URLs from SoFIFA |
| `player_scraper.py` | Extract attributes from an individual player page |
| `sofifa_scraper.py` | Collect player attributes across historical roster versions |
| `add_columns_with_dates.py` | Add date and market valuation columns |
| `delete_second_row.py` | Perform a one-time removal of the first data row |
| `process_players.py` | Prepare player datasets for modeling |
| `run_arima_all.py` | Fit and select ARIMA models |
| `run_arimax_all.py` | Fit and select ARIMAX models |
| `create_analysis_with_position.py` | Combine model results with player positions |
| `plot_all_models.py` | Plot model summaries and coefficient distributions |
| `plot_arimax_all.py` | Generate detailed ARIMAX visualizations |
| `requirements.txt` | List Python dependencies |

## Data

Processed player datasets are provided in `data2/`.
Raw player datasets are provided in `data/`.

Each processed CSV contains the following columns:

- `date`
- `name`
- `transfermarkt_value`
- `log_tm`
- `overall_rating`
- `potential`
- `age`
- `position`
- `attacking`
- `skill`
- `movement`
- `power`
- `mentality`
- `defending`

Raw player data belong in `data/`. Raw data are optional for running models with the processed datasets, but are required to rerun preprocessing.

Transfermarkt values must be supplied separately before preprocessing. The SoFIFA scrapers collect game attributes and do not collect Transfermarkt valuations.

## Installation

Install the required Python packages:

```bash
python -m pip install -r requirements.txt
```

To use the optional scraping scripts, also install the Playwright Chromium browser:

```bash
python -m playwright install chromium
```

## Running the Analysis

After the processed CSV files have been placed in `data2/`, run:

```bash
python run_arima_all.py
python run_arimax_all.py
python create_analysis_with_position.py
python plot_all_models.py
python plot_arimax_all.py
```

The scripts create their output directories automatically:

| Directory | Contents |
| --- | --- |
| `arima_results/` | Selected ARIMA models and combined summary |
| `arimax_results/` | Selected ARIMAX models, coefficients, and combined summary |
| `analysis_results/` | Position summaries and flagged coefficient results |
| `plot_results/` | General model visualizations |
| `analysis_plots_ARIMAX/` | Detailed ARIMAX visualizations |

## Optional Data Collection and Preprocessing

The scraping and cleanup scripts document the data preparation process. They do not need to be rerun when using the processed datasets.

- `scrape_player_urls.py` creates `player_urls.csv`.
- `sofifa_scraper.py` reads player URLs and saves historical attributes in `data/`.
- `add_columns_with_dates.py` assigns dates by row order and adds an empty Transfermarkt valuation column. Dates must be checked against the actual roster versions.
- `delete_second_row.py` removes the first data row from each eligible CSV. It is a one-time cleanup operation; repeated runs remove additional records.
- `process_players.py` creates processed datasets in `data2/` after dates and Transfermarkt values have been checked and completed.

The player scraper currently loads at most the first 100 URLs and requests 24 historical roster versions per player. Repeated scraping runs append records and may create duplicates.

## Limitations

- Scraping depends on the source website's structure and availability.
- Historical roster versions must be aligned with the correct observation dates.
- Short time series and correlated attributes can produce unstable coefficient estimates.
- Model selection is based on in-sample AIC; these scripts do not implement out-of-sample forecast evaluation.
- The detailed position boxplots exclude three explicitly listed players. Other plots retain them.

## Data Sources

- Transfermarkt: https://www.transfermarkt.com/
- SoFIFA: https://sofifa.com/

EA Sports FC/FIFA attributes and market valuation data belong to their respective sources.
