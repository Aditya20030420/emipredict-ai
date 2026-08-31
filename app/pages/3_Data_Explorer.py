"""Interactive data exploration."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from src import config as C  # noqa: E402
from src.data_loader import clean  # noqa: E402
from theme import setup_page, page_header, callout  # noqa: E402

setup_page("Data Explorer", "📊")
page_header("Data Explorer",
            "Browse the data the models learned from — filter it and see the patterns.",
            icon="database")

callout("Use the <b>filters</b> to narrow the data by loan type or eligibility. "
        "The numbers and charts below update to match your selection.")


@st.cache_data(show_spinner="Loading the dataset — this takes a few seconds the first time…")
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

# --- Filters (on the page) ----------------------------------------------
with st.container(border=True):
    st.markdown("**Filters** — tap a pill to include or exclude it.")
    fc1, fc2 = st.columns([3, 2])
    with fc1:
        scen = st.pills("Loan type", C.CATEGORY_OPTIONS["emi_scenario"],
                        selection_mode="multi",
                        default=C.CATEGORY_OPTIONS["emi_scenario"])
    with fc2:
        elig = st.pills("Eligibility", C.CLF_CLASSES, selection_mode="multi",
                        default=C.CLF_CLASSES,
                        format_func=lambda x: x.replace("_", " "))

scen = scen or C.CATEGORY_OPTIONS["emi_scenario"]
elig = elig or C.CLF_CLASSES
f = df[df["emi_scenario"].isin(scen) & df[C.TARGET_CLF].isin(elig)]
if f.empty:
    st.warning("No records match the selected filters.")
    st.stop()

st.markdown("##### Overview of the selected records")
c1, c2, c3 = st.columns(3)
c1.metric("Applicants", f"{len(f):,}",
          help="Number of records matching your filters.")
c2.metric("Average credit score", f"{f['credit_score'].mean():.0f}",
          help="Out of 300–850; higher is safer.")
c3.metric("Average safe EMI", f"₹{f[C.TARGET_REG].mean():,.0f}",
          help="Mean of the maximum safe monthly EMI.")

tab1, tab2, tab3 = st.tabs(["Feature distributions", "By loan type",
                            "Records table"])

# Friendly label <-> column maps for the selector.
_num_cols = [c for c in C.NUMERIC_FEATURES if c in f] + [C.TARGET_REG]
_label_of = {c: C.FIELD_LABELS.get(c, c) for c in _num_cols}
_label_of[C.TARGET_REG] = "Maximum safe EMI (₹)"

with tab1:
    st.caption("Pick a field to see how its values are spread across the "
               "selected applicants.")
    _labels = [_label_of[c] for c in _num_cols]
    # Default to a continuous field with a natural smooth distribution.
    _default = next((_label_of[c] for c in ("monthly_salary", "credit_score",
                     C.TARGET_REG) if c in _num_cols), _labels[0])
    label = st.selectbox("Field to chart", _labels,
                         index=_labels.index(_default))
    col = next(c for c in _num_cols if _label_of[c] == label)

    series = f[col].dropna()
    counts, edges = np.histogram(series, bins=60)
    centers = ((edges[:-1] + edges[1:]) / 2).round(0)
    # Smooth the counts (moving average) into a clean density-style curve,
    # so genuinely spiky/clustered fields still read as a shape.
    k = 7
    smooth = np.convolve(counts, np.ones(k) / k, mode="same")
    dens = pd.DataFrame({"Applicants": smooth}, index=centers)
    dens.index.name = label
    st.area_chart(dens, height=280, color="#1565C0")
    st.caption(f"Smoothed distribution — the curve is higher where more "
               f"applicants share that {label.lower()}.")

    st.markdown("**How many applicants fall into each eligibility class**")
    bal = f[C.TARGET_CLF].value_counts().rename(
        {"Not_Eligible": "Not Eligible", "High_Risk": "High Risk"})
    st.bar_chart(bal, height=240)

with tab2:
    st.caption("Key numbers broken down by the five loan types.")
    grp = f.groupby("emi_scenario").agg(
        Applicants=("emi_scenario", "size"),
        **{"Eligible %": (C.TARGET_CLF, lambda s: round((s == "Eligible").mean() * 100, 1))},
        **{"Avg safe EMI (₹)": (C.TARGET_REG, lambda s: round(s.mean()))},
        **{"Avg requested (₹)": ("requested_amount", lambda s: round(s.mean()))},
    )
    grp.index.name = "Loan type"
    st.dataframe(grp, use_container_width=True)

with tab3:
    st.caption("The raw applicant records behind the charts (first 500 shown).")
    st.dataframe(f.head(500), use_container_width=True)
