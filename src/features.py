"""Feature engineering: derived ratios + risk score, plus a serializable
preprocessing pipeline (imputation, encoding, scaling).

Everything lives inside one sklearn Pipeline so training and the Streamlit app
apply IDENTICAL transforms (no serving skew). The derived-feature step is a
FunctionTransformer, so it serializes with the model too.

    from src.features import build_preprocessor, add_derived_features
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    FunctionTransformer, OneHotEncoder, OrdinalEncoder, StandardScaler,
)

from . import config as C

# Expense components summed into a monthly-outflow figure.
_EXPENSE_COLS = [
    "monthly_rent", "school_fees", "college_fees", "travel_expenses",
    "groceries_utilities", "other_monthly_expenses", "current_emi_amount",
]

# Derived numeric features added by add_derived_features().
DERIVED_NUMERIC = [
    "total_monthly_expenses", "disposable_income", "expense_to_income",
    "debt_to_income", "requested_to_income", "requested_to_balance",
    "emergency_fund_months", "affordability", "risk_score",
]


def _safe_div(a, b):
    """Element-wise a / b with 0-safe denominator; inf/-inf -> NaN."""
    out = a / b.replace(0, np.nan)
    return out.replace([np.inf, -np.inf], np.nan)


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add financial ratios + a composite risk score. Pure & deterministic.

    NaNs from source nulls propagate here and are handled downstream by the
    imputer in the ColumnTransformer.
    """
    df = df.copy()
    salary = df["monthly_salary"]

    exp = df[_EXPENSE_COLS].sum(axis=1, min_count=1)
    df["total_monthly_expenses"] = exp
    df["disposable_income"] = salary - exp
    df["expense_to_income"] = _safe_div(exp, salary)
    df["debt_to_income"] = _safe_div(df["current_emi_amount"], salary)
    df["requested_to_income"] = _safe_div(df["requested_amount"], salary)
    df["requested_to_balance"] = _safe_div(df["requested_amount"], df["bank_balance"])
    df["emergency_fund_months"] = _safe_div(df["emergency_fund"], exp)
    df["affordability"] = _safe_div(df["disposable_income"], salary)

    # Composite risk score (higher = riskier). Blends normalized credit,
    # employment stability, and existing debt burden. Kept simple/interpretable.
    credit_norm = (850 - df["credit_score"].clip(300, 850)) / 550       # 0 good..1 bad
    emp_norm = 1 - (df["years_of_employment"].clip(0, 30) / 30)          # 0 stable..1 new
    dti = df["debt_to_income"].clip(0, 2) / 2                            # 0..1
    df["risk_score"] = (0.5 * credit_norm + 0.2 * emp_norm + 0.3 * dti)

    return df


def build_preprocessor() -> Pipeline:
    """Return a Pipeline: derive features -> impute/encode/scale.

    Output is a dense numeric matrix ready for any sklearn/XGBoost estimator.
    """
    numeric = [c for c in C.NUMERIC_FEATURES] + DERIVED_NUMERIC
    categorical = list(C.CATEGORICAL_FEATURES)
    ordinal_cols = list(C.ORDINAL_FEATURES.keys())
    ordinal_categories = [C.ORDINAL_FEATURES[c] for c in ordinal_cols]

    numeric_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    ordinal_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("ordinal", OrdinalEncoder(categories=ordinal_categories,
                                   handle_unknown="use_encoded_value",
                                   unknown_value=-1)),
        ("scale", StandardScaler()),
    ])

    ct = ColumnTransformer([
        ("num", numeric_pipe, numeric),
        ("cat", categorical_pipe, categorical),
        ("ord", ordinal_pipe, ordinal_cols),
    ], remainder="drop")

    return Pipeline([
        ("derive", FunctionTransformer(add_derived_features)),
        ("prep", ct),
    ])


if __name__ == "__main__":
    from .data_loader import clean
    df = clean(pd.read_csv(C.DATA_PROCESSED / "train.csv", low_memory=False))
    pre = build_preprocessor()
    X = pre.fit_transform(df)
    print("Fitted preprocessor. Output shape:", X.shape)
    print("Derived feature sample (train head):")
    print(add_derived_features(df.head())[DERIVED_NUMERIC].round(3).to_string())
