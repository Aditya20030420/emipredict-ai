"""Deterministic 70/15/15 train/val/test split, stratified on emi_eligibility.

Same split feeds both classification and regression so results are comparable.
Saves parquet-free CSVs to data/processed/.

    python -m src.split_data
"""
from __future__ import annotations

from sklearn.model_selection import train_test_split

from . import config as C
from .data_loader import load_clean


def main() -> None:
    df = load_clean()
    strat = df[C.TARGET_CLF]

    # First carve off test (15%), then val (15% of full = ~0.1765 of remaining).
    train_val, test = train_test_split(
        df, test_size=C.TEST_SIZE, random_state=C.RANDOM_STATE, stratify=strat
    )
    val_frac = C.VAL_SIZE / (1 - C.TEST_SIZE)
    train, val = train_test_split(
        train_val,
        test_size=val_frac,
        random_state=C.RANDOM_STATE,
        stratify=train_val[C.TARGET_CLF],
    )

    C.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    for name, part in [("train", train), ("val", val), ("test", test)]:
        path = C.DATA_PROCESSED / f"{name}.csv"
        part.to_csv(path, index=False)
        dist = part[C.TARGET_CLF].value_counts(normalize=True).round(4).to_dict()
        print(f"{name:5s} n={len(part):>7,}  ->  {path.name}   {dist}")


if __name__ == "__main__":
    main()
