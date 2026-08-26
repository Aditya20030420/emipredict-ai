"""Train >=3 classification models for emi_eligibility, log all to MLflow.

    python -m src.train_classification            # full train set
    python -m src.train_classification --sample 20000   # smoke test

Metrics: accuracy, macro-F1, per-class recall (esp. High_Risk), ROC-AUC (OvR).
Each model = build_preprocessor() + estimator in one Pipeline, logged as an
MLflow artifact with params + metrics.
"""
from __future__ import annotations

import argparse
import warnings

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from . import config as C
from .data_loader import clean
from .evaluate import classification_metrics
from .features import build_preprocessor

warnings.filterwarnings("ignore")
EXPERIMENT = "emi_classification"


def _load(split: str, sample: int | None) -> pd.DataFrame:
    df = clean(pd.read_csv(C.DATA_PROCESSED / f"{split}.csv", low_memory=False))
    if sample:
        df = df.groupby(C.TARGET_CLF, group_keys=False).apply(
            lambda g: g.sample(min(len(g), max(1, sample // 3)),
                               random_state=C.RANDOM_STATE)
        )
    return df


def _models():
    return {
        "logreg": LogisticRegression(max_iter=1000, class_weight="balanced",
                                     n_jobs=-1),
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=None, class_weight="balanced_subsample",
            n_jobs=-1, random_state=C.RANDOM_STATE),
        "xgboost": XGBClassifier(
            n_estimators=400, max_depth=6, learning_rate=0.1, subsample=0.9,
            colsample_bytree=0.9, tree_method="hist", eval_metric="mlogloss",
            n_jobs=-1, random_state=C.RANDOM_STATE),
    }


def main(sample: int | None = None) -> None:
    train = _load("train", sample)
    val = _load("val", sample)
    labels = C.CLF_CLASSES

    # XGBoost needs integer-encoded labels.
    label_to_int = {lab: i for i, lab in enumerate(labels)}
    ytr = train[C.TARGET_CLF]; yva = val[C.TARGET_CLF]

    mlflow.set_tracking_uri(C.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    results = []
    for name, est in _models().items():
        with mlflow.start_run(run_name=name):
            pipe = Pipeline([("prep", build_preprocessor()), ("clf", est)])
            if name == "xgboost":
                pipe.fit(train, ytr.map(label_to_int))
                pred_int = pipe.predict(val)
                y_pred = pd.Series(pred_int).map({v: k for k, v in label_to_int.items()})
                proba = pipe.predict_proba(val)
            else:
                pipe.fit(train, ytr)
                y_pred = pipe.predict(val)
                proba = pipe.predict_proba(val)
                # align proba column order to `labels`
                proba = pd.DataFrame(proba, columns=pipe.named_steps["clf"].classes_)[labels].values

            m = classification_metrics(yva, y_pred, proba, labels=labels)
            mlflow.log_param("model", name)
            mlflow.log_param("n_train", len(train))
            mlflow.log_params({k: v for k, v in est.get_params().items()
                               if isinstance(v, (int, float, str, bool)) and v is not None})
            mlflow.log_metrics(m)
            mlflow.sklearn.log_model(pipe, name="model", serialization_format="cloudpickle")
            results.append({"model": name, **m})
            print(f"[{name}] acc={m['accuracy']:.4f} f1_macro={m['f1_macro']:.4f} "
                  f"recall_High_Risk={m.get('recall_High_Risk', float('nan')):.4f}")

    res = pd.DataFrame(results).sort_values("f1_macro", ascending=False)
    C.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    res.to_csv(C.REPORTS_DIR / "classification_results.csv", index=False)
    print("\n", res.to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=None)
    main(ap.parse_args().sample)
