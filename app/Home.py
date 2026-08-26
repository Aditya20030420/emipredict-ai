"""EMIPredict AI - Streamlit entry page."""
import streamlit as st

from theme import setup_page, page_header, ICONS, PRIMARY, NAVY, MUTED, BORDER, INK
from utils import load_models

setup_page("Home", "💳")
page_header("EMIPredict AI",
            "Intelligent Financial Risk Assessment Platform — FinTech & Banking",
            icon="shield")

# --- What is this for? ---------------------------------------------------
st.markdown(
    f"""
    <div style="border:1px solid {BORDER};border-radius:14px;padding:22px 26px;
                background:#F8FAFC;margin-bottom:20px;">
      <div style="font-size:1.1rem;font-weight:600;color:{NAVY};margin-bottom:8px;">
        What is this for?
      </div>
      <div style="color:{INK};font-size:.95rem;line-height:1.6;">
        <b>EMIPredict AI helps lenders decide whether to approve a loan and how
        much a person can safely repay each month.</b> Many borrowers struggle
        with EMIs because affordability isn't assessed properly. This platform
        uses machine learning trained on 400,000 financial profiles to give an
        instant, data-driven risk assessment — replacing slow, manual underwriting.
      </div>
      <div style="color:{MUTED};font-size:.88rem;line-height:1.6;margin-top:12px;">
        <b>Who uses it:</b> loan officers and underwriters for quick approval
        decisions · banks &amp; credit agencies for risk-based pricing and
        default prevention · FinTech apps for instant eligibility checks.
      </div>
      <div style="color:{MUTED};font-size:.88rem;line-height:1.6;margin-top:12px;">
        <b>It answers two questions:</b>
        1) Is this applicant <i>Eligible</i>, <i>High-Risk</i>, or
        <i>Not Eligible</i>?  2) What is the largest monthly EMI they can safely afford?
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- KPI row -------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Classification accuracy", "94.5%", "target > 90%")
k2.metric("High-Risk recall", "0.93", "+0.39 vs untuned")
k3.metric("Regression RMSE", "₹705", "target < 2000")
k4.metric("Records analysed", "404,800", "5 EMI scenarios")

st.write("")

# --- Feature cards -------------------------------------------------------
CARDS = [
    ("check", "Predict Eligibility", "Classify an applicant as Eligible, "
     "High-Risk, or Not Eligible, with calibrated class probabilities."),
    ("rupee", "Predict Max EMI", "Estimate the maximum safe monthly EMI (₹) "
     "for an applicant's financial profile."),
    ("database", "Data Explorer", "Explore the 404K-record dataset with live "
     "filters, distributions, and per-scenario breakdowns."),
    ("chart", "Model Dashboard", "Compare all trained models and review "
     "MLflow-tracked metrics and tuning results."),
]
cols = st.columns(2)
for i, (icon, title, desc) in enumerate(CARDS):
    with cols[i % 2]:
        st.markdown(
            f"""
            <div style="border:1px solid {BORDER};border-radius:14px;padding:20px 22px;
                        margin-bottom:16px;background:#fff;box-shadow:0 1px 2px rgba(15,23,42,.04);">
              <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                <span style="color:{PRIMARY};">{ICONS[icon]}</span>
                <span style="font-size:1.05rem;font-weight:600;color:{NAVY};">{title}</span>
              </div>
              <div style="color:{MUTED};font-size:.9rem;line-height:1.5;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.info("Use the sidebar to navigate between tools. →", icon="👈")

# --- Model status --------------------------------------------------------
try:
    load_models()
    st.success("Champion models loaded (XGBoost classifier + regressor).")
except Exception as e:  # pragma: no cover
    st.error(f"Could not load models: {e}")

with st.expander("About the models & methodology"):
    st.markdown(
        """
- **Classifier — XGBoost with balanced class weighting.** Chosen for its high
  **High-Risk recall (0.93)**: in lending, failing to flag a risky applicant is
  the costly error. Raw accuracy alone is misleading given ~77% class imbalance,
  so selection prioritised macro-F1 and per-class recall.
- **Regressor — XGBoost on `log1p(max_monthly_emi)`.** RMSE ₹705, R² 0.99.
- Both models wrap the **same preprocessing pipeline** used in training, so the
  app applies identical transforms at inference (no training/serving skew).
- All experiments are tracked in **MLflow** with a versioned model registry.
"""
    )
