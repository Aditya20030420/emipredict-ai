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
@st.cache_resource
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
def applicant_form(key_prefix: str = "f") -> pd.DataFrame:
    """Render grouped inputs; return a single-row DataFrame in FEATURE_ORDER."""
    vals = {}
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
        cols = st.columns(2)
        for i, f in enumerate(fields):
            col = cols[i % 2]
            k = f"{key_prefix}_{f}"
            if f in C.CATEGORY_OPTIONS:
                vals[f] = col.selectbox(f, C.CATEGORY_OPTIONS[f], key=k)
            else:
                default, lo, hi, step = C.NUMERIC_INPUT_SPEC[f]
                vals[f] = col.number_input(f, min_value=lo, max_value=hi,
                                           value=default, step=step, key=k)
    return pd.DataFrame([vals])[FEATURE_ORDER]


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
