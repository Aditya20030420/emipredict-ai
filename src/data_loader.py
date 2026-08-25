"""Load, clean, and validate the raw EMI dataset.

Cleaning steps (driven by real-data profiling on 2026-08-26):
  1. Fix corrupted numeric strings ("58.0.0" -> 58.0) in DIRTY_NUMERIC_COLS.
  2. Normalize gender's 8 raw variants -> Male / Female.
  3. Enforce dtypes.
  4. Emit a data-quality report (nulls, duplicates, out-of-range,
     per-scenario bound violations).

Run directly to print/save the report:
    python -m src.data_loader
"""
from __future__ import annotations

import re
import pandas as pd

from . import config as C

_NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _fix_dirty_number(val):
    """Extract the first valid float from a corrupted string like '64300.0.0.0'."""
    if pd.isna(val):
        return float("nan")
    if isinstance(val, (int, float)):
        return float(val)
    m = _NUM_RE.match(str(val).strip())
    return float(m.group()) if m else float("nan")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Corrupted numerics stored as object.
    for col in C.DIRTY_NUMERIC_COLS:
        if col in df.columns:
            df[col] = df[col].map(_fix_dirty_number).astype("float64")

    # 2. Normalize gender.
    if "gender" in df.columns:
        df["gender"] = (
            df["gender"].astype(str).str.strip().str.lower().map(C.GENDER_MAP)
        )

    # 3. Strip whitespace on remaining object/categorical columns.
    for col in C.CATEGORICAL_FEATURES + list(C.ORDINAL_FEATURES):
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].str.strip()

    return df


def load_raw(path=C.DATA_RAW) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def load_clean(path=C.DATA_RAW) -> pd.DataFrame:
    return clean(load_raw(path))


def data_quality_report(df: pd.DataFrame) -> str:
    """Build a markdown data-quality report from an ALREADY-CLEANED frame."""
    lines: list[str] = ["# Data Quality Report", ""]
    lines.append(f"- Rows: **{len(df):,}**  |  Columns: **{df.shape[1]}**")
    lines.append(f"- Duplicate rows: **{df.duplicated().sum():,}**")
    lines.append("")

    # Missing values
    nulls = df.isna().sum()
    nulls = nulls[nulls > 0].sort_values(ascending=False)
    lines.append("## Missing values")
    if nulls.empty:
        lines.append("- None.")
    else:
        for col, n in nulls.items():
            lines.append(f"- `{col}`: {n:,} ({n / len(df):.2%})")
    lines.append("")

    # Target balance
    lines.append("## Class balance (`emi_eligibility`)")
    vc = df[C.TARGET_CLF].value_counts(normalize=True)
    for cls, frac in vc.items():
        lines.append(f"- {cls}: {frac:.2%}")
    lines.append("")

    # Numeric out-of-range
    lines.append("## Out-of-range numeric values")
    for col, (lo, hi) in C.NUMERIC_BOUNDS.items():
        if col in df.columns:
            bad = ((df[col] < lo) | (df[col] > hi)).sum()
            lines.append(f"- `{col}` outside [{lo:,}, {hi:,}]: {bad:,}")
    lines.append("")

    # Per-scenario bound violations
    lines.append("## Per-scenario `requested_amount` / `requested_tenure` violations")
    for scen, b in C.SCENARIO_BOUNDS.items():
        sub = df[df["emi_scenario"] == scen]
        if sub.empty:
            continue
        alo, ahi = b["amount"]; tlo, thi = b["tenure"]
        a_bad = ((sub["requested_amount"] < alo) | (sub["requested_amount"] > ahi)).sum()
        t_bad = ((sub["requested_tenure"] < tlo) | (sub["requested_tenure"] > thi)).sum()
        lines.append(f"- {scen} (n={len(sub):,}): amount OOB {a_bad:,}, tenure OOB {t_bad:,}")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    df = load_clean()
    report = data_quality_report(df)
    C.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = C.REPORTS_DIR / "data_quality.md"
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved -> {out}")
