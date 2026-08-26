"""Predict EMI eligibility (classification)."""
import streamlit as st

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src import config as C  # noqa: E402
from theme import setup_page, page_header, result_card, RISK
from utils import applicant_form, create_record, load_models, predict_eligibility

setup_page("Predict Eligibility", "✅")
page_header("Predict EMI Eligibility",
            "Fill in the applicant's details below and click Predict to see "
            "whether they qualify for the loan.",
            icon="check")

st.info("Enter an applicant's profile, then press **Predict eligibility**. "
        "The result shows one of three outcomes and how confident the model is.",
        icon="ℹ️")

clf, _ = load_models()

with st.form("eligibility"):
    row = applicant_form("elig")
    save = st.checkbox("Save this applicant to the database")
    submitted = st.form_submit_button("Predict eligibility", type="primary")

if submitted:
    label, proba = predict_eligibility(clf, row)
    style = RISK.get(label, {"fg": "#1565C0", "bg": "#E0F2FE", "label": label})
    result_card("Result", style["label"], style["fg"], style["bg"])
    st.markdown(f"**What this means:** {C.ELIGIBILITY_MEANING.get(label, '')}")

    if proba:
        conf = max(proba.values())
        st.markdown(f"##### How confident is the model? "
                    f"({conf:.0%} on the predicted outcome)")
        st.caption("Each bar is the chance the applicant falls into that "
                   "category. They add up to 100%.")
        cols = st.columns(len(proba))
        for c, cls in zip(cols, ["Not_Eligible", "Eligible", "High_Risk"]):
            if cls in proba:
                c.metric(RISK[cls]["label"], f"{proba[cls]:.0%}")
        st.bar_chart({RISK[k]["label"]: v for k, v in proba.items()})

    if save:
        rec_id = create_record(row.iloc[0].to_dict(), pred_elig=label)
        st.toast(f"Saved as record #{rec_id}", icon="💾")
        st.caption(f"Saved as record #{rec_id} — see Admin CRUD.")

st.caption(
    "High-Risk indicates a marginal applicant who may need higher interest "
    "rates; Not Eligible indicates the loan is not recommended."
)
