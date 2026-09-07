"""Predict EMI eligibility (classification) with explainable decision support."""
import streamlit as st

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src import config as C  # noqa: E402
from theme import (setup_page, page_header, result_card, callout, risk_gauge,
                   factor_rows, guard, RISK)
from utils import (applicant_form, apply_example, create_record, load_models,
                   predict_eligibility, predict_max_emi, affordability_factors)

setup_page("Predict Eligibility", "✅")
page_header("Predict EMI Eligibility",
            "Assess loan eligibility with an explainable, data-driven decision.",
            icon="check")

with guard("Predict Eligibility"):
    callout("New here? Load an <b>example applicant</b> below to see it instantly, "
            "or fill in the form and press <b>Predict eligibility</b>.")

    # --- One-click examples ----------------------------------------------
    st.markdown("###### Quick start — load an example applicant")
    ex_cols = st.columns(len(C.EXAMPLE_APPLICANTS))
    for col, (name, profile) in zip(ex_cols, C.EXAMPLE_APPLICANTS.items()):
        if col.button(name, key=f"ex_{name}", use_container_width=True):
            apply_example("elig", profile)
            st.rerun()

    clf, reg = load_models()

    with st.form("eligibility"):
        row = applicant_form("elig")
        save = st.checkbox("Save this applicant to the database")
        submitted = st.form_submit_button("Predict eligibility", type="primary")

    if submitted:
        label, proba = predict_eligibility(clf, row)
        style = RISK.get(label, {"fg": "#1565C0", "bg": "#E0F2FE", "label": label})

        left, right = st.columns([1.4, 1])
        with left:
            result_card("Result", style["label"], style["fg"], style["bg"])
            st.markdown(f"**What this means:** {C.ELIGIBILITY_MEANING.get(label, '')}")
        with right:
            if proba:
                conf = proba.get(label, max(proba.values()))
                risk_gauge(conf, style["fg"], "model confidence")

        # --- Why this decision (explainability) --------------------------
        st.markdown("##### Key factors behind this decision")
        st.caption("How the applicant's finances compare to healthy lending bands.")
        factor_rows(affordability_factors(row))

        # --- Unified recommendation: safe EMI vs requested ---------------
        safe = predict_max_emi(reg, row)
        requested = float(row["requested_amount"].iloc[0])
        tenure = int(row["requested_tenure"].iloc[0])
        this_emi = requested / max(tenure, 1)
        st.markdown("##### Affordability of the requested loan")
        a, b, c = st.columns(3)
        a.metric("Safe monthly EMI", f"₹{safe:,.0f}")
        b.metric("This loan's EMI", f"₹{this_emi:,.0f}")
        headroom = safe - this_emi
        c.metric("Headroom", f"₹{headroom:,.0f}",
                 delta="within capacity" if headroom >= 0 else "over capacity",
                 delta_color="normal" if headroom >= 0 else "inverse")
        if headroom < 0:
            st.warning("The requested instalment exceeds the safe EMI — suggest a "
                       "longer tenure, a smaller amount, or a higher interest rate.")
        else:
            st.success("The requested instalment fits within the applicant's "
                       "estimated safe capacity.")

        # --- Probabilities -----------------------------------------------
        if proba:
            with st.expander("See full class probabilities"):
                pc = st.columns(len(proba))
                for cc, cls in zip(pc, ["Not_Eligible", "Eligible", "High_Risk"]):
                    if cls in proba:
                        cc.metric(RISK[cls]["label"], f"{proba[cls]:.0%}")
                st.bar_chart({RISK[k]["label"]: v for k, v in proba.items()})

        if save:
            rec_id = create_record(row.iloc[0].to_dict(), pred_elig=label,
                                   pred_emi=safe)
            st.toast(f"Saved as record #{rec_id}")
            st.caption(f"Saved as record #{rec_id} — see Admin CRUD.")
