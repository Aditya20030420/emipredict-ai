"""EMIPredict AI - Streamlit entry page."""
import streamlit as st

from utils import load_models

st.set_page_config(page_title="EMIPredict AI", page_icon="💳", layout="wide")

st.title("💳 EMIPredict AI")
st.caption("Intelligent Financial Risk Assessment Platform — FinTech / Banking")

st.markdown(
    """
Welcome to **EMIPredict AI**, a dual-ML platform for data-driven loan decisions.

**What it does**
- **Predict Eligibility** — classify an applicant as *Eligible*, *High_Risk*, or
  *Not_Eligible* (with class probabilities).
- **Predict Max EMI** — estimate the maximum safe monthly EMI (INR).
- **Data Explorer** — explore the underlying 400K-record dataset.
- **Model Dashboard** — model comparison & MLflow-tracked metrics.
- **Admin CRUD** — manage saved applicant records (SQLite).

Use the sidebar to navigate. 👈
"""
)

col1, col2, col3 = st.columns(3)
col1.metric("Classification accuracy", "94.5%", "target > 90%")
col2.metric("High_Risk recall", "0.93", "up from 0.54 untuned")
col3.metric("Regression RMSE", "705 INR", "target < 2000")

st.divider()
try:
    load_models()
    st.success("Champion models loaded successfully (XGBoost classifier + regressor).")
except Exception as e:  # pragma: no cover
    st.error(f"Could not load models: {e}")

with st.expander("About the models"):
    st.markdown(
        """
- **Classifier:** XGBoost with balanced class weighting — chosen for its high
  **High_Risk recall (0.93)**, since missing a risky applicant is the costly
  error in lending. Accuracy alone is misleading given ~77% class imbalance.
- **Regressor:** XGBoost on `log1p(max_monthly_emi)` — RMSE 705 INR, R² 0.99.
- Both wrap the **same preprocessing pipeline** used in training (no serving skew).
"""
    )
