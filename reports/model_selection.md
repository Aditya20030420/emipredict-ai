# Model Selection & Justification

All models tracked in MLflow (SQLite backend) across two experiments —
`emi_classification` and `emi_regression`. Selected models are registered in the
MLflow Model Registry with the `champion` alias and exported to `models/` for the
Streamlit app.

## Classification — `emi_eligibility` (3 classes, severe imbalance)

Validation-set results (n=60,721). **Accuracy alone is misleading** here: the
majority class (Not_Eligible) is ~77%, so a trivial model scores ~77%. The
business-critical metric is **High_Risk recall** — catching risky applicants.

| Model | Accuracy | Macro-F1 | High_Risk recall | Notes |
|---|---|---|---|---|
| xgboost (untuned) | 0.973 | 0.868 | 0.540 | Best accuracy, but misses ~46% of High_Risk |
| random_forest | 0.945 | 0.655 | 0.034 | Accuracy is a mirage — ignores rare class |
| logreg (balanced) | 0.794 | 0.641 | 0.672 | Better minority recall, poor overall |
| xgboost_tuned (factor=3) | 0.923 | 0.805 | 0.959 | Higher recall, more accuracy cost |
| **xgboost_tuned (factor=1)** ✅ | **0.945** | **0.843** | **0.930** | **Selected** |

**Selected: XGBoost with `balanced` sample weighting (factor=1).**
Rationale: balanced sample weights lift High_Risk recall from **0.54 → 0.93**
while keeping accuracy at **94.5%** (well above the 90% target) and the best
macro-F1 among the high-recall configs. In a lending context, a false negative
on a high-risk applicant (approving someone who will default) is far costlier
than a false positive, so we deliberately trade ~2.8 points of accuracy for a
0.39 gain in High_Risk recall.

> The untuned XGBoost has higher raw accuracy (97.3%) but is unsuitable for
> production: catching only 54% of high-risk applicants is a material risk
> exposure. This is the core "best model != highest accuracy" argument.

## Regression — `max_monthly_emi` (INR, right-skewed, log1p-modeled)

Validation-set results. Target < 2000 RMSE.

| Model | RMSE | MAE | R² | MAPE |
|---|---|---|---|---|
| **xgboost** ✅ | **705** | 218 | **0.992** | 3.5% |
| random_forest | 939 | 290 | 0.985 | 4.8% |
| linear | 8,770 | 2,995 | −0.27 | 64.7% |

**Selected: XGBoost regressor** — RMSE 705 (less than half the 2000 budget),
R² 0.99, MAPE 3.5%. RandomForest also clears the target but is slower to train
and larger to serialize; the linear baseline fails, confirming the target's
nonlinearity and validating the `log1p` transform.

## Registered artifacts

| Registry name | Alias | Source run | Export |
|---|---|---|---|
| `emi_eligibility_clf` | champion | xgboost_tuned_hrx1 | `models/clf_champion.pkl` (~5.5 MB) |
| `emi_max_emi_reg` | champion | xgboost | `models/reg_champion.pkl` (~4 MB) |

Both export the full preprocessing + model `Pipeline`, so the app applies
identical transforms to training (no serving skew). Verified: load + predict on
held-out test rows matches actuals closely.

> Note: the classification model outputs integer-encoded labels in the order
> `["Not_Eligible", "Eligible", "High_Risk"]` (see `config.CLF_CLASSES`); the app
> maps them back to names.
