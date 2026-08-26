"""Predict EMI eligibility (classification)."""
import streamlit as st

from theme import setup_page, page_header, result_card, RISK
from utils import applicant_form, create_record, load_models, predict_eligibility

setup_page("Predict Eligibility", "✅")
page_header("Predict EMI Eligibility",
            "Assess an applicant's loan eligibility with class probabilities.",
            icon="check")

clf, _ = load_models()

with st.form("eligibility"):
    row = applicant_form("elig")
    save = st.checkbox("Save this applicant to the database")
    submitted = st.form_submit_button("Predict eligibility", type="primary")

if submitted:
    label, proba = predict_eligibility(clf, row)
    style = RISK.get(label, {"fg": "#1565C0", "bg": "#E0F2FE", "label": label})
    result_card("Predicted eligibility", style["label"], style["fg"], style["bg"])

    if proba:
        st.markdown("##### Class probabilities")
        cols = st.columns(len(proba))
        for c, cls in zip(cols, ["Not_Eligible", "Eligible", "High_Risk"]):
            if cls in proba:
                c.metric(RISK[cls]["label"], f"{proba[cls]:.1%}")
        st.bar_chart({RISK[k]["label"]: v for k, v in proba.items()})

    if save:
        rec_id = create_record(row.iloc[0].to_dict(), pred_elig=label)
        st.toast(f"Saved as record #{rec_id}", icon="💾")
        st.caption(f"Saved as record #{rec_id} — see Admin CRUD.")

st.caption(
    "High-Risk indicates a marginal applicant who may need higher interest "
    "rates; Not Eligible indicates the loan is not recommended."
)
