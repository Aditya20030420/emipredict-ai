# EMIPredict AI — Intelligent Financial Risk Assessment Platform

Dual-ML FinTech platform that predicts **EMI eligibility** (3-class classification)
and **maximum safe monthly EMI** (regression) from 22+ financial/demographic
features, with MLflow experiment tracking and a Streamlit Cloud web app.

> Full build plan: [PLAN.md](PLAN.md)

## Status

| Phase | State |
|---|---|
| Data loading + cleaning + quality report | ✅ done |
| Train/val/test split | ✅ done |
| EDA | ⬜ |
| Feature engineering | ⬜ |
| Model development + MLflow | ⬜ |
| Model selection + registry | ⬜ |
| Streamlit app | ⬜ |
| Cloud deployment | ⬜ |

## Dataset (real, profiled 2026-08-26)

- **404,800 rows × 27 cols** (25 features + 2 targets), 5 EMI scenarios (~81K each).
- **Targets:** `emi_eligibility` (Not_Eligible 77% / Eligible 18% / High_Risk 4% —
  **severe imbalance**, lead with macro-F1) and `max_monthly_emi` (500–91K INR, right-skewed).
- **Known data issues (handled in `data_loader.py`):** corrupted numeric strings
  (`"58.0.0"`) in age/monthly_salary/bank_balance; 8 `gender` variants; ~0.6% nulls
  in 5 columns.

The CSV is **not committed** (72 MB, gitignored). Place it at
`data/raw/emi_prediction_dataset.csv`.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements-dev.txt   # full env (training, MLflow, EDA)
# The deployed app only needs the lean requirements.txt.
```

Run the app locally:

```bash
python -m streamlit run app/Home.py
```

## Run the pipeline so far

```bash
python -m src.data_loader     # -> reports/data_quality.md
python -m src.split_data      # -> data/processed/{train,val,test}.csv
```

## Structure

```
src/        config, data loading/cleaning, splitting (models + features to come)
app/        Streamlit multi-page app (to come)
data/       raw/ + processed/ (gitignored)
models/     exported best models
reports/    EDA + quality + model-comparison reports
notebooks/  EDA / feature-engineering exploration
```

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. At [share.streamlit.io](https://share.streamlit.io) → **New app**, pick the repo,
   set **Main file path** to `app/Home.py`, and select **Python 3.12**.
3. It installs `requirements.txt` (lean, app-only) and serves the public URL.

The app is cloud-ready: small committed models (`models/*.pkl`), a 5K-row
`data/sample.csv` for the explorer, and a SQLite CRUD store that self-initializes
(it resets on redeploy — demo storage).

## Grading targets

Classification accuracy > 90% (with honest macro-F1) · Regression RMSE < 2000 INR.
