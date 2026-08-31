"""Shared helpers for the Streamlit app: model loading, input form, CRUD."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

# Make `src` importable when Streamlit runs from the repo root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import config as C  # noqa: E402

DB_PATH = ROOT / "data" / "emi_records.db"
FEATURE_ORDER = (
    C.NUMERIC_FEATURES + C.CATEGORICAL_FEATURES + list(C.ORDINAL_FEATURES.keys())
)


# --- Models --------------------------------------------------------------
@st.cache_resource(show_spinner="Loading the prediction models…")
def load_models():
    clf = joblib.load(C.MODELS_DIR / "clf_champion.pkl")
    reg = joblib.load(C.MODELS_DIR / "reg_champion.pkl")
    return clf, reg


def predict_eligibility(clf, row: pd.DataFrame):
    """Return (label, proba_dict). Model outputs integer-encoded labels."""
    idx = int(clf.predict(row)[0])
    label = C.CLF_CLASSES[idx] if 0 <= idx < len(C.CLF_CLASSES) else str(idx)
    proba = {}
    if hasattr(clf, "predict_proba"):
        p = clf.predict_proba(row)[0]
        proba = {C.CLF_CLASSES[i]: float(p[i]) for i in range(len(p))}
    return label, proba


def predict_max_emi(reg, row: pd.DataFrame) -> float:
    return float(max(0.0, reg.predict(row)[0]))


# --- Input form ----------------------------------------------------------
def apply_example(prefix: str, profile: dict):
    """Load an example applicant into the form (bumps a version to reset widgets)."""
    st.session_state[f"{prefix}_preset"] = dict(profile)
    st.session_state[f"{prefix}_ver"] = st.session_state.get(f"{prefix}_ver", 0) + 1


def applicant_form(key_prefix: str = "f") -> pd.DataFrame:
    """Render grouped inputs; return a single-row DataFrame in FEATURE_ORDER.

    Supports one-click example loading via apply_example(): a version counter
    in session_state forces fresh widgets that honour the preset values.
    """
    vals = {}
    ver = st.session_state.get(f"{key_prefix}_ver", 0)
    preset = st.session_state.get(f"{key_prefix}_preset", {})
    groups = {
        "Demographics": ["age", "gender", "marital_status", "education"],
        "Employment & Income": ["monthly_salary", "employment_type",
                                 "years_of_employment", "company_type"],
        "Housing & Family": ["house_type", "monthly_rent", "family_size", "dependents"],
        "Monthly Obligations": ["school_fees", "college_fees", "travel_expenses",
                                "groceries_utilities", "other_monthly_expenses"],
        "Credit & Status": ["existing_loans", "current_emi_amount", "credit_score",
                            "bank_balance", "emergency_fund"],
        "Loan Request": ["emi_scenario", "requested_amount", "requested_tenure"],
    }
    for group, fields in groups.items():
        st.subheader(group)
        if group in C.GROUP_HELP:
            st.caption(C.GROUP_HELP[group])
        cols = st.columns(2)
        for i, f in enumerate(fields):
            col = cols[i % 2]
            k = f"{key_prefix}_{f}_{ver}"
            label = C.FIELD_LABELS.get(f, f)
            help_txt = C.FIELD_HELP.get(f)
            if f in C.CATEGORY_OPTIONS:
                opts = C.CATEGORY_OPTIONS[f]
                idx = opts.index(preset[f]) if f in preset and preset[f] in opts else 0
                vals[f] = col.selectbox(label, opts, index=idx, key=k, help=help_txt)
            else:
                default, lo, hi, step = C.NUMERIC_INPUT_SPEC[f]
                val = preset.get(f, default)
                vals[f] = col.number_input(label, min_value=lo, max_value=hi,
                                           value=val, step=step, key=k,
                                           help=help_txt)
    return pd.DataFrame([vals])[FEATURE_ORDER]


def affordability_factors(row: pd.DataFrame) -> list[dict]:
    """Plain-language 'why' factors from the applicant's ratios vs healthy bands.

    Returns dicts: {label, value, status in good|warn|bad, note}.
    """
    from src.features import add_derived_features
    r = add_derived_features(row).iloc[0]
    out = []

    def band(v, good_below, warn_below, fmt, note_g, note_b, higher_bad=True):
        if higher_bad:
            status = "good" if v <= good_below else ("warn" if v <= warn_below else "bad")
        else:
            status = "good" if v >= good_below else ("warn" if v >= warn_below else "bad")
        return status

    dti = float(r["debt_to_income"]) if pd.notna(r["debt_to_income"]) else 0.0
    out.append({"label": "Existing debt-to-income",
                "value": f"{dti:.0%}",
                "status": band(dti, .15, .35, None, None, None),
                "note": "Share of income already going to EMIs."})

    eti = float(r["expense_to_income"]) if pd.notna(r["expense_to_income"]) else 0.0
    out.append({"label": "Expenses-to-income",
                "value": f"{eti:.0%}",
                "status": band(eti, .5, .75, None, None, None),
                "note": "Total monthly outgoings vs income."})

    cs = float(row["credit_score"].iloc[0])
    out.append({"label": "Credit score",
                "value": f"{cs:.0f}",
                "status": "good" if cs >= 720 else ("warn" if cs >= 650 else "bad"),
                "note": "Higher is safer (300–850)."})

    efm = float(r["emergency_fund_months"]) if pd.notna(r["emergency_fund_months"]) else 0.0
    out.append({"label": "Emergency fund",
                "value": f"{efm:.1f} months",
                "status": "good" if efm >= 6 else ("warn" if efm >= 3 else "bad"),
                "note": "Months of expenses covered by savings."})

    return out


# --- SQLite CRUD ---------------------------------------------------------
def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    cols = ", ".join(f'"{c}" TEXT' for c in FEATURE_ORDER)
    with _conn() as con:
        con.execute(f"""
            CREATE TABLE IF NOT EXISTS applicants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {cols},
                predicted_eligibility TEXT,
                predicted_max_emi REAL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)


def create_record(row: dict, pred_elig=None, pred_emi=None):
    init_db()
    fields = FEATURE_ORDER + ["predicted_eligibility", "predicted_max_emi"]
    values = [str(row.get(c)) for c in FEATURE_ORDER] + [pred_elig, pred_emi]
    placeholders = ", ".join("?" for _ in fields)
    collist = ", ".join(f'"{c}"' for c in fields)
    with _conn() as con:
        cur = con.execute(
            f"INSERT INTO applicants ({collist}) VALUES ({placeholders})", values)
        return cur.lastrowid


def read_records() -> pd.DataFrame:
    init_db()
    with _conn() as con:
        return pd.read_sql_query(
            "SELECT * FROM applicants ORDER BY id DESC", con)


def update_record(rec_id: int, updates: dict):
    if not updates:
        return
    sets = ", ".join(f'"{k}" = ?' for k in updates)
    with _conn() as con:
        con.execute(f"UPDATE applicants SET {sets} WHERE id = ?",
                    list(updates.values()) + [rec_id])


def delete_record(rec_id: int):
    with _conn() as con:
        con.execute("DELETE FROM applicants WHERE id = ?", (rec_id,))
