"""Select best runs from MLflow and register them + export for the app.

Picks:
  - classification: highest High_Risk recall among runs with accuracy >= floor
    (falls back to macro-F1) -> registered as 'emi_eligibility_clf'
  - regression: lowest RMSE -> registered as 'emi_max_emi_reg'

Also exports the fitted pipelines to models/*.pkl for direct app loading
(avoids depending on the MLflow server at serving time).

    python -m src.registry
"""
from __future__ import annotations

import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient

from . import config as C

CLF_MODEL_NAME = "emi_eligibility_clf"
REG_MODEL_NAME = "emi_max_emi_reg"
ACC_FLOOR = 0.93


def _best_clf_run(client: MlflowClient):
    exp = client.get_experiment_by_name("emi_classification")
    runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
    # Prefer runs that logged High_Risk recall (tuned + baseline).
    runs = runs[runs["metrics.accuracy"].notna()]
    ok = runs[runs["metrics.accuracy"] >= ACC_FLOOR]
    pool = ok if not ok.empty else runs
    if "metrics.recall_High_Risk" in pool.columns and pool["metrics.recall_High_Risk"].notna().any():
        pool = pool.sort_values("metrics.recall_High_Risk", ascending=False)
    else:
        pool = pool.sort_values("metrics.f1_macro", ascending=False)
    return pool.iloc[0]


def _best_reg_run(client: MlflowClient):
    exp = client.get_experiment_by_name("emi_regression")
    runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
    runs = runs[runs["metrics.rmse"].notna()].sort_values("metrics.rmse")
    return runs.iloc[0]


def _register_and_export(client, run, registered_name, out_file):
    run_id = run["run_id"]
    uri = f"runs:/{run_id}/model"
    mv = mlflow.register_model(uri, registered_name)
    client.set_registered_model_alias(registered_name, "champion", mv.version)
    # Export the fitted pipeline for the app.
    model = mlflow.sklearn.load_model(uri)
    import joblib
    C.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, C.MODELS_DIR / out_file)
    return mv.version


def main() -> None:
    mlflow.set_tracking_uri(C.MLFLOW_TRACKING_URI)
    client = MlflowClient()

    clf = _best_clf_run(client)
    reg = _best_reg_run(client)

    print("Best classification run:")
    print(f"  run_name={clf.get('tags.mlflow.runName')} acc={clf['metrics.accuracy']:.4f} "
          f"macro-F1={clf['metrics.f1_macro']:.4f} "
          f"High_Risk recall={clf.get('metrics.recall_High_Risk', float('nan')):.4f}")
    print("Best regression run:")
    print(f"  run_name={reg.get('tags.mlflow.runName')} rmse={reg['metrics.rmse']:.1f} "
          f"r2={reg['metrics.r2']:.4f}")

    v1 = _register_and_export(client, clf, CLF_MODEL_NAME, "clf_champion.pkl")
    v2 = _register_and_export(client, reg, REG_MODEL_NAME, "reg_champion.pkl")
    print(f"\nRegistered {CLF_MODEL_NAME} v{v1} (alias 'champion') -> models/clf_champion.pkl")
    print(f"Registered {REG_MODEL_NAME} v{v2} (alias 'champion') -> models/reg_champion.pkl")


if __name__ == "__main__":
    main()
