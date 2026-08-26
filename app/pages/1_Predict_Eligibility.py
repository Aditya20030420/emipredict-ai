"""Predict EMI eligibility (classification)."""
import streamlit as st

from utils import applicant_form, create_record, load_models, predict_eligibility

st.set_page_config(page_title="Predict Eligibility", page_icon="✅", layout="wide")
st.title("✅ Predict EMI Eligibility")

clf, _ = load_models()

with st.form("eligibility"):
    row = applicant_form("elig")
    save = st.checkbox("Save this applicant to the database")
    submitted = st.form_submit_button("Predict eligibility", type="primary")

if submitted:
    label, proba = predict_eligibility(clf, row)
    color = {"Eligible": "success", "High_Risk": "warning",
             "Not_Eligible": "error"}.get(label, "info")
    getattr(st, color)(f"### Prediction: **{label.replace('_', ' ')}**")

    if proba:
        st.write("Class probabilities:")
        st.bar_chart(proba)
        cols = st.columns(len(proba))
        for c, (cls, p) in zip(cols, proba.items()):
            c.metric(cls.replace("_", " "), f"{p:.1%}")

    if save:
        rec_id = create_record(row.iloc[0].to_dict(), pred_elig=label)
        st.info(f"Saved as record #{rec_id} (see Admin CRUD).")

st.caption(
    "Note: High_Risk means a marginal applicant who may need higher interest "
    "rates; Not_Eligible means the loan is not recommended."
)
