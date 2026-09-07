"""Model performance dashboard (MLflow-tracked results)."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"

from theme import setup_page, page_header, guard  # noqa: E402

setup_page("Model Dashboard", "📈")
page_header("Model Performance Dashboard",
            "Model comparison and MLflow-tracked metrics across both tasks.",
            icon="chart")
st.caption("All models tracked in MLflow across two experiments "
           "(emi_classification, emi_regression).")


def _read(name):
    p = REPORTS / name
    return pd.read_csv(p) if p.exists() else None


with guard("Model Dashboard"):
    clf = _read("classification_results.csv")
    tune = _read("classification_tuning.csv")
    reg = _read("regression_results.csv")

    st.header("Classification — EMI eligibility")
    if clf is not None:
        st.dataframe(clf.round(4), use_container_width=True)
        st.bar_chart(clf.set_index("model")[["accuracy", "f1_macro", "recall_High_Risk"]])
        st.caption("Accuracy is high across models, but **High_Risk recall** separates "
                   "a usable model from one that ignores the rare risky class.")
    else:
        st.info("Classification results not found — run the training pipeline to generate them.")
    if tune is not None:
        st.subheader("Tuning: High_Risk recall vs accuracy")
        st.dataframe(tune.round(4), use_container_width=True)
        st.line_chart(tune.set_index("factor")[["accuracy", "recall_High_Risk", "f1_macro"]])

    st.header("Regression — maximum monthly EMI")
    if reg is not None:
        st.dataframe(reg.round(3), use_container_width=True)
        st.bar_chart(reg.set_index("model")[["rmse", "mae"]])
    else:
        st.info("Regression results not found — run the training pipeline to generate them.")

    st.header("Selected champion models")
    st.markdown(
        """
| Task | Model | Key metric | Registry |
|---|---|---|---|
| Classification | XGBoost (balanced) | 94.5% acc, **0.93 High_Risk recall** | `emi_eligibility_clf` @champion |
| Regression | XGBoost (log1p target) | **RMSE 705**, R² 0.99 | `emi_max_emi_reg` @champion |

Run `mlflow ui --backend-store-uri sqlite:///mlflow.db` locally to browse all runs.
"""
    )
