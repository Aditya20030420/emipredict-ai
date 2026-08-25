# EMIPredict AI — Implementation Plan (14 Days)

**Project:** Intelligent Financial Risk Assessment Platform
**Domain:** FinTech / Banking
**Stack:** Python, pandas/scikit-learn/XGBoost, MLflow, Streamlit (Cloud), GitHub

---

## 0. Prerequisites (do before Day 1)

- [ ] **Obtain `EMI_dataset` CSV** (400K rows, 22 features + 2 targets). *Not in repo — get it from the orientation / EDA-guide links in the brief.* **This blocks everything.**
- [ ] Create GitHub repo; set up local venv; `pip install` core deps.
- [ ] Confirm the two graded targets are realistic on the actual data: **classification accuracy > 90%** and **regression RMSE < 2000 INR**. Note the regression target `max_monthly_emi` ranges **500–50,000 INR**, so RMSE < 2000 is a tight bar (~4% of full scale) — interpret the metric against this range.
- [ ] **Prepare for a live viva** — the brief references a *"Project Live Evaluation"*, so budget time to walk through data, models, MLflow, and the app end-to-end.

---

## Reference material (from the brief)

Provided by the brief — pull the dataset and guidance from these:
- **Project Live Evaluation** — live viva/demo (grading).
- **EDA Guide** and **Capstone Explanation Guideline**.
- **GitHub Reference** (How to Use GitHub.pptx).
- **Project Orientation** recordings (English + Tamil) — *likely source of the `EMI_dataset` CSV.*
- **Streamlit** special session + install/docs.
- **MLflow** Tutorials 1 & 2 + "Getting Started with MLflow" docs.
- **Project Excellence Series** — ML (supervised + unsupervised) and EDA, English + Tamil.

---

## Proposed repository structure

```
EMIPredict-AI/
├── data/
│   ├── raw/                  # EMI_dataset.csv (gitignored)
│   └── processed/            # train/val/test splits (gitignored)
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_feature_eng.ipynb
├── src/
│   ├── config.py             # paths, feature lists, constants
│   ├── data_loader.py        # load + validate
│   ├── preprocess.py         # cleaning, encoding, scaling pipeline
│   ├── features.py           # derived ratios & risk scores
│   ├── train_classification.py
│   ├── train_regression.py
│   ├── evaluate.py           # metrics + comparison reports
│   └── registry.py           # MLflow model registry helpers
├── app/
│   ├── Home.py               # Streamlit entry
│   └── pages/
│       ├── 1_Predict_Eligibility.py
│       ├── 2_Predict_Max_EMI.py
│       ├── 3_Data_Explorer.py
│       ├── 4_Model_Dashboard.py   # MLflow metrics
│       └── 5_Admin_CRUD.py
├── models/                   # exported best models (or via MLflow registry)
├── mlruns/                   # MLflow tracking (gitignored)
├── reports/                  # EDA + model comparison outputs
├── requirements.txt
├── .gitignore
├── README.md
└── PLAN.md
```

---

## Day-by-day plan

### Days 1–2 · Foundation + Data Loading & Preprocessing (grading: 15%)
- Scaffold repo structure above; `requirements.txt`, `.gitignore`, README skeleton.
- `data_loader.py`: load 400K CSV, dtype enforcement, memory profiling.
- Data quality: missing values, duplicates, inconsistency flags, and out-of-range checks against the brief's documented bounds:
  - Numeric ranges: `age` 25–60, `credit_score` 300–850, `monthly_salary` 15K–200K INR, `max_monthly_emi` (target) 500–50,000 INR.
  - Categorical domains: `gender` (Male/Female), `marital_status` (Single/Married), `education` (High School/Graduate/Post Graduate/Professional — treat as ordinal), `employment_type` (Private/Government/Self-employed), `house_type` (Rented/Own/Family), `emi_scenario` (5 categories).
  - **Per-scenario `requested_amount` / `requested_tenure` bounds** (validate each scenario separately — also a strong EDA angle):
    - E-commerce: 10K–200K, 3–24 mo · Home Appliances: 20K–300K, 6–36 mo · Vehicle: 80K–1500K, 12–84 mo · Personal Loan: 50K–1000K, 12–60 mo · Education: 50K–500K, 6–48 mo.
- Deterministic **train/val/test split** (e.g. 70/15/15, stratified on `emi_eligibility`), saved to `data/processed/`.
- **Deliverable:** clean preprocessing pipeline + a data-quality report.

### Days 3–4 · Exploratory Data Analysis
- Target distributions: 3-class eligibility balance; `max_monthly_emi` distribution + by scenario.
- Correlations (numeric) and driver analysis vs both targets.
- Demographic / risk-factor patterns; scenario-level breakdowns (5 EMI categories).
- **Deliverable:** `reports/eda.md` (or notebook export) with plots + business insights. *(Class imbalance findings here drive metric choice later.)*

### Days 5–6 · Feature Engineering
- Derived ratios: **debt-to-income, expense-to-income, affordability, EMI-to-income**.
- Risk-scoring features from credit score + employment stability + existing EMI burden.
- Categorical encoding (ordinal for education, one-hot for scenario/employment/house) + numeric scaling — all inside a `ColumnTransformer`/`Pipeline` so it serializes with the model.
- A few interaction features (e.g. salary × tenure, credit × requested_amount).
- **Deliverable:** reusable `features.py` transformer; feature dictionary.

### Days 7–9 · Model Development + MLflow (grading: 25% + 15% MLflow)
- **Classification (≥3):** LogisticRegression (baseline), RandomForest, XGBoost (+ optional SVC/DecisionTree/GradientBoosting).
  Metrics: accuracy, precision, recall, F1, ROC-AUC (macro/OvR for 3-class).
- **Regression (≥3):** LinearRegression (baseline), RandomForestRegressor, XGBRegressor (+ optional).
  Metrics: RMSE, MAE, R², MAPE.
- **MLflow** from the first run: log params, hyperparameters, metrics, and artifacts (model, plots) for **every** model. Organize into two experiments (classification / regression).
- Light hyperparameter tuning on the top 1–2 per task.
- **Deliverable:** all runs tracked and comparable in the MLflow UI.

### Day 10 · Model Selection + Registry (grading: 15%)
- Compare runs; select best per task with written justification (metric trade-offs, not just top accuracy).
- Register selected models in **MLflow Model Registry** (versioned); export to `models/` for app loading.
- **Deliverable:** model-comparison report + selection rationale.

### Days 11–12 · Streamlit App (grading: 20%)
- Multi-page app: eligibility prediction, max-EMI prediction, data explorer, MLflow/model dashboard, admin CRUD.
- Load the registered best models; real-time inference on user input using the **same** preprocessing pipeline.
- Input validation, error handling, clear user feedback.
- **Deliverable:** working local app.

### Day 13 · Cloud Deployment (grading: 10%)
- Push to GitHub; deploy on **Streamlit Community Cloud** from the repo.
- Pin `requirements.txt`; ensure model artifacts are loadable in the cloud (size limits — consider registry/download or committing small serialized models).
- Verify public URL, responsiveness, cold-start behavior.
- **Deliverable:** live public URL.

### Day 14 · Documentation, Reports & Buffer
- README: setup, architecture, how to run, live link.
- Four named written deliverables (all required by the brief):
  1. **Technical documentation** — methodology + architecture.
  2. **EDA report** — business insights + visualizations.
  3. **Model-performance / MLflow comparison** — across all trained models.
  4. **Business-impact assessment** — quantify against the brief's claims: ~80% less manual processing time, risk-based pricing across the 5 scenarios, standardized eligibility criteria, scalability for high-volume applications; include recommendations for financial institutions.
- Final QA against the grading rubric; buffer for fixes.
- **Deliverable:** complete, documented, deployed project.

---

## Grading rubric mapping (self-check)

| Weight | Requirement | Covered on |
|---|---|---|
| 15% | Preprocessing completeness + data-quality accuracy | Days 1–2 |
| 25% | ≥3 classification + ≥3 regression models | Days 7–9 |
| 15% | Best-model selection + justification | Day 10 |
| 15% | MLflow tracking (all models) + registry | Days 7–10 |
| 20% | Streamlit app w/ best models, real-time | Days 11–12 |
| 10% | Cloud deployment stability + accessibility | Day 13 |

## Key risks
- **Dataset not yet available** — hard blocker for Day 1.
- **Streamlit Cloud model-size / dependency limits** — validate deployment early (don't leave to Day 13).
- **3-class imbalance** — if `High_Risk` is rare, watch macro-F1, not just accuracy, to hit the >90% target honestly.
- **Preprocessing/serving skew** — keep all transforms in one saved Pipeline so the app applies exactly what training did.
