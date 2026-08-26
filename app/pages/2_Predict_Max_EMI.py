"""Predict maximum safe monthly EMI (regression)."""
import streamlit as st

from utils import applicant_form, create_record, load_models, predict_max_emi

st.set_page_config(page_title="Predict Max EMI", page_icon="💰", layout="wide")
st.title("💰 Predict Maximum Monthly EMI")

_, reg = load_models()

with st.form("max_emi"):
    row = applicant_form("emi")
    save = st.checkbox("Save this applicant to the database")
    submitted = st.form_submit_button("Predict max EMI", type="primary")

if submitted:
    emi = predict_max_emi(reg, row)
    st.success(f"### Estimated maximum safe monthly EMI: **₹{emi:,.0f}**")

    requested = float(row["requested_amount"].iloc[0])
    tenure = int(row["requested_tenure"].iloc[0])
    naive_emi = requested / max(tenure, 1)
    c1, c2 = st.columns(2)
    c1.metric("Max safe EMI (model)", f"₹{emi:,.0f}")
    c2.metric("Requested amount / tenure", f"₹{naive_emi:,.0f}",
              help="Simple undiscounted EMI for the requested loan (no interest).")
    if naive_emi > emi:
        st.warning("The requested loan's monthly outflow exceeds the estimated "
                   "safe EMI — consider a longer tenure or smaller amount.")
    else:
        st.info("The requested loan appears within the estimated safe EMI capacity.")

    if save:
        rec_id = create_record(row.iloc[0].to_dict(), pred_emi=emi)
        st.info(f"Saved as record #{rec_id} (see Admin CRUD).")
