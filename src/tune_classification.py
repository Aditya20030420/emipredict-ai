"""Tune XGBoost classifier to improve High_Risk recall via sample weighting.

Multiclass XGBoost has no scale_pos_weight, so we pass per-sample weights:
a 'balanced' base weight, with an extra multiplier on the rare High_Risk class.
Each config is logged to MLflow. We pick the config that MAXIMIZES High_Risk
recall while keeping accuracy comfortably above the 0.90 target.

    python -m src.tune_classification
"""
from __future__ import annotations

import warnings

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

from . import config as C
from .data_loader import clean
from .evaluate import classification_metrics
from .features import build_preprocessor

warnings.filterwarnings("ignore")
EXPERIMENT = "emi_classification"
ACC_FLOOR = 0.93            # keep a healthy margin over the 0.90 target
HIGH_RISK_FACTORS = [1, 3, 6, 10]   # extra weight multiplier on High_Risk


def _load(split: str) -> pd.DataFrame:
    return clean(pd.read_csv(C.DATA_PROCESSED / f"{split}.csv", low_memory=False))


def main() -> None:
    train, val = _load("train"), _load("val")
    labels = C.CLF_CLASSES
    l2i = {lab: i for i, lab in enumerate(labels)}
    ytr_int = train[C.TARGET_CLF].map(l2i)
    yva = val[C.TARGET_CLF]

    mlflow.set_tracking_uri(C.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    base_w = compute_sample_weight("balanced", ytr_int)
    hr_mask = (train[C.TARGET_CLF] == "High_Risk").to_numpy()

    results = []
    for factor in HIGH_RISK_FACTORS:
        w = base_w.copy()
        w[hr_mask] *= factor
        with mlflow.start_run(run_name=f"xgboost_tuned_hrx{factor}"):
            est = XGBClassifier(
                n_estimators=400, max_depth=6, learning_rate=0.1, subsample=0.9,
                colsample_bytree=0.9, tree_method="hist", eval_metric="mlogloss",
                n_jobs=-1, random_state=C.RANDOM_STATE)
            pipe = Pipeline([("prep", build_preprocessor()), ("clf", est)])
            pipe.fit(train, ytr_int, clf__sample_weight=w)

            pred_int = pipe.predict(val)
            y_pred = pd.Series(pred_int).map({v: k for k, v in l2i.items()})
            proba = pipe.predict_proba(val)
            m = classification_metrics(yva, y_pred, proba, labels=labels)

            mlflow.log_param("model", "xgboost_tuned")
            mlflow.log_param("high_risk_weight_factor", factor)
            mlflow.log_metrics(m)
            mlflow.sklearn.log_model(pipe, name="model",
                                     serialization_format="cloudpickle")
            results.append({"factor": factor, **m})
            print(f"[hrx{factor}] acc={m['accuracy']:.4f} f1_macro={m['f1_macro']:.4f} "
                  f"recall_High_Risk={m['recall_High_Risk']:.4f} "
                  f"recall_Eligible={m['recall_Eligible']:.4f}")

    res = pd.DataFrame(results)
    # Selection: highest High_Risk recall among configs that keep acc >= floor.
    ok = res[res["accuracy"] >= ACC_FLOOR]
    pool = ok if not ok.empty else res
    best = pool.sort_values("recall_High_Risk", ascending=False).iloc[0]
    res.to_csv(C.REPORTS_DIR / "classification_tuning.csv", index=False)
    print("\n", res.to_string(index=False))
    print(f"\nSelected factor={int(best['factor'])}: acc={best['accuracy']:.4f}, "
          f"High_Risk recall={best['recall_High_Risk']:.4f}, "
          f"macro-F1={best['f1_macro']:.4f}")


if __name__ == "__main__":
    main()
