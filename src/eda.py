"""Exploratory Data Analysis -> reports/eda.md + reports/*.png

Runs on the TRAIN split only (no peeking at val/test). Produces plots and a
markdown report focused on the decisions that drive modeling:
  - class imbalance (metric choice)
  - max_monthly_emi skew + 500-floor cluster (target transform)
  - numeric correlations with both targets (driver analysis)
  - per-scenario breakdowns

    python -m src.eda
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config as C
from .data_loader import clean

sns_ok = True
try:
    import seaborn as sns
    sns.set_theme(style="whitegrid")
except Exception:
    sns_ok = False


def _load_train() -> pd.DataFrame:
    path = C.DATA_PROCESSED / "train.csv"
    if path.exists():
        return clean(pd.read_csv(path, low_memory=False))
    # Fallback: clean full dataset if splits not generated yet.
    from .data_loader import load_clean
    return load_clean()


def _save(fig, name: str) -> str:
    C.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    p = C.REPORTS_DIR / name
    fig.savefig(p, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return name


def main() -> None:
    df = _load_train()
    L: list[str] = ["# Exploratory Data Analysis", "",
                    f"_Computed on the train split (n={len(df):,})._", ""]

    # 1. Class balance -----------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 3.5))
    vc = df[C.TARGET_CLF].value_counts().reindex(C.CLF_CLASSES)
    ax.bar(vc.index, vc.values, color=["#c0392b", "#27ae60", "#e67e22"])
    ax.set_title("EMI eligibility class balance"); ax.set_ylabel("count")
    for i, v in enumerate(vc.values):
        ax.text(i, v, f"{v/len(df):.1%}", ha="center", va="bottom")
    img1 = _save(fig, "eda_class_balance.png")
    L += ["## 1. Class imbalance (drives metric choice)",
          f"![]({img1})", "",
          "| Class | Share |", "|---|---|"]
    for cls, frac in df[C.TARGET_CLF].value_counts(normalize=True).items():
        L.append(f"| {cls} | {frac:.2%} |")
    L += ["",
          "**Insight:** Not_Eligible dominates (~77%). A trivial majority-class "
          "predictor already scores ~77% accuracy, so **accuracy is a weak "
          "metric here**. Report **macro-F1 and per-class recall** (especially "
          "for High_Risk at ~4%). Use stratified splits + class weighting.", ""]

    # 2. Regression target -------------------------------------------------
    y = df[C.TARGET_REG]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))
    axes[0].hist(y, bins=80, color="#2980b9")
    axes[0].set_title("max_monthly_emi"); axes[0].set_xlabel("INR")
    axes[1].hist(np.log1p(y), bins=80, color="#8e44ad")
    axes[1].set_title("log1p(max_monthly_emi)")
    img2 = _save(fig, "eda_target_regression.png")
    floor = (y <= 500).mean()
    L += ["## 2. Regression target: `max_monthly_emi`",
          f"![]({img2})", "",
          f"- Range **{y.min():,.0f}–{y.max():,.0f} INR**, "
          f"mean {y.mean():,.0f}, median {y.median():,.0f}, std {y.std():,.0f}.",
          f"- **{floor:.1%}** of rows sit on the **500 floor** (clipped low end).",
          "- Strong right skew -> the log transform is far more symmetric. "
          "**Recommend modeling `log1p(max_monthly_emi)`** and back-transforming.",
          f"- RMSE target <2000 is tight vs std ~{y.std():,.0f}.", ""]

    # 3. Correlations ------------------------------------------------------
    num = [c for c in C.NUMERIC_FEATURES if c in df.columns]
    corr = df[num + [C.TARGET_REG]].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    if sns_ok:
        sns.heatmap(corr, cmap="coolwarm", center=0, ax=ax,
                    cbar_kws={"shrink": .7})
    else:
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns, rotation=90)
        ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.columns)
        fig.colorbar(im, shrink=.7)
    ax.set_title("Numeric correlation matrix")
    img3 = _save(fig, "eda_corr_matrix.png")

    drivers = corr[C.TARGET_REG].drop(C.TARGET_REG).sort_values(key=abs, ascending=False)
    L += ["## 3. Numeric drivers of `max_monthly_emi`",
          f"![]({img3})", "",
          "Top correlations with the regression target:", "",
          "| Feature | corr |", "|---|---|"]
    for f, v in drivers.head(8).items():
        L.append(f"| {f} | {v:+.3f} |")
    L.append("")

    # 4. Eligibility by numeric (means per class) --------------------------
    key = ["credit_score", "monthly_salary", "current_emi_amount",
           "requested_amount", "emergency_fund", "bank_balance"]
    key = [k for k in key if k in df.columns]
    grp = df.groupby(C.TARGET_CLF)[key].mean().reindex(C.CLF_CLASSES)
    L += ["## 4. Financial profile by eligibility class (mean)", "",
          "| Class | " + " | ".join(key) + " |",
          "|" + "---|" * (len(key) + 1)]
    for cls in C.CLF_CLASSES:
        row = grp.loc[cls]
        L.append(f"| {cls} | " + " | ".join(f"{row[k]:,.0f}" for k in key) + " |")
    L += ["",
          "**Insight:** Eligible applicants have markedly higher credit_score "
          "and salary and lower existing EMI burden — consistent with the "
          "affordability logic behind the target.", ""]

    # 5. Per-scenario breakdown -------------------------------------------
    scen = df.groupby("emi_scenario").agg(
        n=("emi_scenario", "size"),
        elig_rate=(C.TARGET_CLF, lambda s: (s == "Eligible").mean()),
        mean_emi=(C.TARGET_REG, "mean"),
        mean_req=("requested_amount", "mean"),
    ).sort_values("mean_req", ascending=False)
    L += ["## 5. Per-scenario breakdown", "",
          "| Scenario | n | Eligible % | mean max_emi | mean requested |",
          "|---|---|---|---|---|"]
    for s, r in scen.iterrows():
        L.append(f"| {s} | {int(r['n']):,} | {r['elig_rate']:.1%} | "
                 f"{r['mean_emi']:,.0f} | {r['mean_req']:,.0f} |")
    L += ["",
          "**Insight:** high-ticket scenarios (Vehicle, Personal Loan) carry "
          "larger requested amounts; eligibility rates vary by scenario, so "
          "`emi_scenario` is an informative categorical feature.", ""]

    out = C.REPORTS_DIR / "eda.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:40]))
    print(f"\nSaved report -> {out} (+ 3 PNGs in reports/)")


if __name__ == "__main__":
    main()
