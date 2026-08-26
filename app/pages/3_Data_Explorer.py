"""Interactive data exploration."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src import config as C  # noqa: E402
from src.data_loader import clean  # noqa: E402
from theme import setup_page, page_header  # noqa: E402

setup_page("Data Explorer", "📊")
page_header("Data Explorer",
            "Explore the EMI dataset with live filters and per-scenario views.",
            icon="database")


@st.cache_data
def load_sample() -> pd.DataFrame:
    # Prefer the full raw data locally; fall back to the committed sample.
    for path in (C.DATA_RAW, ROOT / "data" / "sample.csv"):
        if path.exists():
            return clean(pd.read_csv(path, low_memory=False))
    return pd.DataFrame()


df = load_sample()
if df.empty:
    st.error("No data available.")
    st.stop()

st.caption(f"Showing {len(df):,} records "
           f"({'full dataset' if len(df) > 50_000 else 'sample'}).")

# Filters
with st.sidebar:
    st.header("Filters")
    scen = st.multiselect("EMI scenario", C.CATEGORY_OPTIONS["emi_scenario"],
                          default=C.CATEGORY_OPTIONS["emi_scenario"])
    elig = st.multiselect("Eligibility", C.CLF_CLASSES, default=C.CLF_CLASSES)

f = df[df["emi_scenario"].isin(scen) & df[C.TARGET_CLF].isin(elig)]

c1, c2, c3 = st.columns(3)
c1.metric("Records", f"{len(f):,}")
c2.metric("Mean credit score", f"{f['credit_score'].mean():.0f}")
c3.metric("Mean max EMI", f"₹{f[C.TARGET_REG].mean():,.0f}")

tab1, tab2, tab3 = st.tabs(["Distributions", "By scenario", "Raw data"])

with tab1:
    col = st.selectbox("Numeric column",
                       [c for c in C.NUMERIC_FEATURES if c in f] + [C.TARGET_REG])
    st.bar_chart(f[col].value_counts(bins=40, sort=False))
    st.write("**Eligibility class balance**")
    st.bar_chart(f[C.TARGET_CLF].value_counts())

with tab2:
    grp = f.groupby("emi_scenario").agg(
        records=("emi_scenario", "size"),
        eligible_pct=(C.TARGET_CLF, lambda s: (s == "Eligible").mean() * 100),
        mean_max_emi=(C.TARGET_REG, "mean"),
        mean_requested=("requested_amount", "mean"),
    ).round(0)
    st.dataframe(grp, use_container_width=True)

with tab3:
    st.dataframe(f.head(500), use_container_width=True)
