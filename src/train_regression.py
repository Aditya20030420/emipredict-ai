"""Train >=3 regression models for max_monthly_emi, log all to MLflow.

Models predict log1p(target); metrics are computed on back-transformed INR.

    python -m src.train_regression
    python -m src.train_regression --sample 20000
"""
from __future__ import annotations

import argparse
import warnings

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from . import config as C
from .data_loader import clean
from .evaluate import regression_metrics
from .features import build_preprocessor

warnings.filterwarnings("ignore")
EXPERIMENT = "emi_regression"


def _load(split: str, sample: int | None) -> pd.DataFrame:
    df = clean(pd.read_csv(C.DATA_PROCESSED / f"{split}.csv", low_memory=False))
    if sample:
        df = df.sample(min(len(df), sample), random_state=C.RANDOM_STATE)
    return df


def _models():
    return {
        "linear": LinearRegression(n_jobs=-1),
        "random_forest": RandomForestRegressor(
            n_estimators=200, max_depth=None, n_jobs=-1,
            random_state=C.RANDOM_STATE),
        "xgboost": XGBRegressor(
            n_estimators=500, max_depth=7, learning_rate=0.08, subsample=0.9,
            colsample_bytree=0.9, tree_method="hist", n_jobs=-1,
            random_state=C.RANDOM_STATE),
    }


def main(sample: int | None = None) -> None:
    train = _load("train", sample)
    val = _load("val", sample)
    ytr = train[C.TARGET_REG]; yva = val[C.TARGET_REG]

    mlflow.set_tracking_uri(C.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    results = []
    for name, est in _models().items():
        with mlflow.start_run(run_name=name):
            base = Pipeline([("prep", build_preprocessor()), ("reg", est)])
            # Model log1p(target), back-transform with expm1 for real-INR metrics.
            model = TransformedTargetRegressor(
                regressor=base, func=np.log1p, inverse_func=np.expm1)
            model.fit(train, ytr)
            y_pred = np.clip(model.predict(val), 0, None)

            m = regression_metrics(yva, y_pred)
            mlflow.log_param("model", name)
            mlflow.log_param("n_train", len(train))
            mlflow.log_param("target_transform", "log1p")
            mlflow.log_params({k: v for k, v in est.get_params().items()
                               if isinstance(v, (int, float, str, bool)) and v is not None})
            mlflow.log_metrics(m)
            mlflow.sklearn.log_model(model, name="model", serialization_format="cloudpickle")
            results.append({"model": name, **m})
            print(f"[{name}] rmse={m['rmse']:.1f} mae={m['mae']:.1f} "
                  f"r2={m['r2']:.4f} mape={m['mape']:.1f}%")

    res = pd.DataFrame(results).sort_values("rmse")
    C.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    res.to_csv(C.REPORTS_DIR / "regression_results.csv", index=False)
    print("\n", res.to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=None)
    main(ap.parse_args().sample)
