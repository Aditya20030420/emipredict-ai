"""EMIPredict AI - Streamlit entry page."""
import streamlit as st

from theme import (setup_page, page_header, render_footer, nav_row, ICONS,
                   PRIMARY, NAVY, MUTED, BORDER, INK)
from utils import load_models

setup_page("Home", "💳")
page_header("EMIPredict AI",
            "AI-powered loan risk assessment for faster, fairer lending decisions.",
            icon="shield")

# --- What is this for? ---------------------------------------------------
st.markdown(
    f"""
    <div style="border:1px solid {BORDER};border-radius:14px;padding:22px 26px;
                background:#F8FAFC;margin-bottom:20px;">
      <div style="font-size:1.1rem;font-weight:600;color:{NAVY};margin-bottom:8px;">
        Why EMIPredict AI?
      </div>
      <div style="color:{INK};font-size:.95rem;line-height:1.6;">
        <b>EMIPredict AI tells lenders, in seconds, whether an applicant can handle
        a loan — and how much they can safely repay each month.</b> Too many
        borrowers default because affordability is judged slowly and by hand.
        Trained on 400,000 real financial profiles, the platform turns that
        guesswork into an instant, consistent, data-driven decision.
      </div>
      <div style="color:{MUTED};font-size:.88rem;line-height:1.6;margin-top:12px;">
        <b>Built for:</b> loan officers who need fast approvals · banks &amp; credit
        agencies pricing risk and preventing defaults · FinTech apps running instant
        eligibility checks.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Two questions it answers, as clear side-by-side cards.
q1, q2 = st.columns(2)
for col, num, q in [
    (q1, "1", "Is this applicant <b>Eligible</b>, <b>High-Risk</b>, or "
     "<b>Not Eligible</b> for the loan?"),
    (q2, "2", "What is the <b>largest monthly EMI</b> they can safely afford?"),
]:
    col.markdown(
        f"""
        <div style="border:1px solid {BORDER};border-left:4px solid {PRIMARY};
                    border-radius:10px;padding:14px 18px;margin-bottom:16px;
                    background:#fff;min-height:78px;">
          <div style="display:flex;gap:10px;align-items:flex-start;">
            <span style="background:{PRIMARY};color:#fff;font-weight:700;
                         border-radius:50%;width:24px;height:24px;flex:none;
                         display:flex;align-items:center;justify-content:center;
                         font-size:.85rem;">{num}</span>
            <span style="color:{INK};font-size:.92rem;line-height:1.5;">{q}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- KPI row -------------------------------------------------------------
st.markdown("##### Model performance at a glance")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Accuracy", "94.5%", "target > 90%")
k2.metric("High-Risk recall", "0.93", "+0.39 vs untuned")
k3.metric("Max-EMI error (RMSE)", "₹705", "target < ₹2000")
k4.metric("Records analysed", "404.8K", "5 loan types")

st.write("")

# --- Quick launch --------------------------------------------------------
st.markdown("##### Tools")
nav_row([
    ("Predict_Eligibility", "check", "Predict Eligibility"),
    ("Predict_Max_EMI", "rupee", "Predict Max EMI"),
    ("Data_Explorer", "database", "Data Explorer"),
    ("Model_Dashboard", "chart", "Model Dashboard"),
])
st.write("")

# --- Feature cards -------------------------------------------------------
CARDS = [
    ("check", "Predict Eligibility", "Instantly classify an applicant as "
     "Eligible, High-Risk, or Not Eligible — with confidence scores and the "
     "reasons behind the decision.", "#1565C0", "#E7F0FE"),
    ("rupee", "Predict Max EMI", "See the highest monthly EMI an applicant can "
     "comfortably afford, and how it compares to the loan requested.",
     "#0D9488", "#D8F3EE"),
    ("database", "Data Explorer", "Filter and visualise the 404K-profile "
     "dataset by loan type and eligibility.", "#7C3AED", "#EFE7FD"),
    ("chart", "Model Dashboard", "Compare every model and review the metrics "
     "behind the chosen champions.", "#D97706", "#FDEFD8"),
]
cols = st.columns(2)
for i, (icon, title, desc, fg, bg) in enumerate(CARDS):
    with cols[i % 2]:
        st.markdown(
            f"""
            <div style="border:1px solid {BORDER};border-radius:14px;padding:20px 22px;
                        margin-bottom:16px;background:#fff;min-height:124px;
                        box-shadow:0 2px 8px rgba(15,23,42,.05);">
              <div style="display:flex;align-items:center;gap:13px;margin-bottom:10px;">
                <span style="display:flex;align-items:center;justify-content:center;
                             width:42px;height:42px;border-radius:11px;
                             background:{bg};color:{fg};">{ICONS[icon]}</span>
                <span style="font-size:1.05rem;font-weight:600;color:{NAVY};">{title}</span>
              </div>
              <div style="color:{MUTED};font-size:.9rem;line-height:1.5;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- Model status --------------------------------------------------------
try:
    load_models()
    st.success("Ready — champion models loaded (XGBoost classifier + regressor).")
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

render_footer()
