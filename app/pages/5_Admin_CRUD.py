"""Admin CRUD for saved applicant records (SQLite)."""
import streamlit as st

from utils import (create_record, delete_record, init_db, read_records,
                   update_record, applicant_form)

from theme import setup_page, page_header, guard

setup_page("Admin", "🗂️")
page_header("Admin — Applicant Records",
            "Manage saved applicant records (SQLite-backed CRUD).",
            icon="database")
st.caption("On Streamlit Cloud the database resets on redeploy (demo storage).")

with guard("Admin — Applicant Records"):
    init_db()

    tab_list, tab_create, tab_edit = st.tabs(["Browse", "Create", "Edit / Delete"])

    with tab_list:
        df = read_records()
        st.metric("Total records", len(df))
        if df.empty:
            st.info("No records yet. Add one in the Create tab, or save a prediction.")
        else:
            st.dataframe(df, use_container_width=True)
            st.download_button("Download as CSV", df.to_csv(index=False),
                               "applicants.csv", "text/csv")

    with tab_create:
        with st.form("create_rec"):
            row = applicant_form("crud")
            submitted = st.form_submit_button("Create record", type="primary")
        if submitted:
            rec_id = create_record(row.iloc[0].to_dict())
            st.success(f"Created record #{rec_id}.")
            st.rerun()

    with tab_edit:
        df = read_records()
        if df.empty:
            st.info("No records to edit.")
        else:
            rec_id = st.selectbox("Select record id", df["id"].tolist())
            rec = df[df["id"] == rec_id].iloc[0]

            st.write("**Edit a field**")
            editable = [c for c in df.columns
                        if c not in ("id", "created_at")]
            col = st.selectbox("Field", editable)
            new_val = st.text_input("New value", value=str(rec[col]))
            c1, c2 = st.columns(2)
            if c1.button("Update", type="primary"):
                update_record(int(rec_id), {col: new_val})
                st.success(f"Updated record #{rec_id}: {col} = {new_val}")
                st.rerun()
            if c2.button("Delete record", type="secondary"):
                delete_record(int(rec_id))
                st.warning(f"Deleted record #{rec_id}.")
                st.rerun()
