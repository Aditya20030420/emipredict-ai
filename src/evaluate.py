"""Metric helpers for classification and regression."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score,
    mean_absolute_error, mean_squared_error, r2_score,
)


def classification_metrics(y_true, y_pred, y_proba=None, labels=None) -> dict:
    m = {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1_macro": f1_score(y_true, y_pred, average="macro"),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
        "precision_macro": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_true, y_pred, average="macro", zero_division=0),
    }
    # Per-class recall (High_Risk recall is the key business metric).
    if labels is not None:
        rec = recall_score(y_true, y_pred, average=None, labels=labels, zero_division=0)
        for lab, r in zip(labels, rec):
            m[f"recall_{lab}"] = r
    if y_proba is not None:
        try:
            m["roc_auc_ovr"] = roc_auc_score(y_true, y_proba, multi_class="ovr",
                                             average="macro", labels=labels)
        except Exception:
            pass
    return m


def regression_metrics(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    # MAPE with a floor to avoid divide-by-zero on the 500-floor cluster.
    denom = np.clip(np.abs(y_true), 1.0, None)
    mape = float(np.mean(np.abs((y_true - y_pred) / denom)) * 100)
    return {"rmse": rmse, "mae": mae, "r2": r2, "mape": mape}
