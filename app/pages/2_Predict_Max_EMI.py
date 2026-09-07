"""Predict maximum safe monthly EMI (regression)."""
import streamlit as st

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src import config as C  # noqa: E402
from theme import (setup_page, page_header, result_card, callout, factor_rows,
                   guard, PRIMARY)
from utils import (applicant_form, apply_example, create_record, load_models,
                   predict_max_emi, affordability_factors)

setup_page("Predict Max EMI", "💰")
page_header("Predict Maximum Monthly EMI",
            "Estimate the largest monthly EMI an applicant can safely afford.",
            icon="rupee")

with guard("Predict Max EMI"):
    callout("Load an <b>example applicant</b> below, or enter a profile and press "
            "<b>Predict max EMI</b> to see the highest instalment they can afford.")

    st.markdown("###### Quick start — load an example applicant")
    ex_cols = st.columns(len(C.EXAMPLE_APPLICANTS))
    for col, (name, profile) in zip(ex_cols, C.EXAMPLE_APPLICANTS.items()):
        if col.button(name, key=f"exemi_{name}", use_container_width=True):
            apply_example("emi", profile)
            st.rerun()

    _, reg = load_models()

    with st.form("max_emi"):
        row = applicant_form("emi")
        save = st.checkbox("Save this applicant to the database")
        submitted = st.form_submit_button("Predict max EMI", type="primary")

    if submitted:
        emi = predict_max_emi(reg, row)
        result_card("Estimated maximum safe monthly EMI", f"₹{emi:,.0f}",
                    PRIMARY, "#E0F2FE")

        requested = float(row["requested_amount"].iloc[0])
        tenure = int(row["requested_tenure"].iloc[0])
        naive_emi = requested / max(tenure, 1)
        c1, c2 = st.columns(2)
        c1.metric("Safe monthly EMI (estimated)", f"₹{emi:,.0f}",
                  help="The most the applicant can comfortably pay each month.")
        c2.metric("This loan's monthly instalment", f"₹{naive_emi:,.0f}",
                  help="Requested amount divided by the repayment period.")
        if naive_emi > emi:
            st.warning("The requested loan's monthly outflow exceeds the estimated "
                       "safe EMI — consider a longer tenure or a smaller amount.")
        else:
            st.success("The requested loan appears within the estimated safe EMI capacity.")

        st.markdown("##### Key factors")
        st.caption("How the applicant's finances compare to healthy lending bands.")
        factor_rows(affordability_factors(row))

        if save:
            rec_id = create_record(row.iloc[0].to_dict(), pred_emi=emi)
            st.toast(f"Saved as record #{rec_id}")
            st.caption(f"Saved as record #{rec_id} — see Admin CRUD.")
