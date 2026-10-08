import pandas as pd

from src.config import PROCESSED_DIR


def clean_stock_data(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    df = df.copy()

    # 1. Make sure the index is a sorted DatetimeIndex with no duplicates
    df.index = pd.to_datetime(df.index)
    df = df[~df.index.duplicated(keep="first")].sort_index()

    # 2. Keep only the columns we need
    cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    df = df[cols]

    # 3. Report missing values
    missing = df.isna().sum()
    if missing.any():
        print("Missing values:\n", missing[missing > 0])

    # 4. Forward-fill small gaps only (never back-fill: that leaks future data)
    df = df.ffill(limit=3).dropna()

    # 5. Sanity checks
    assert (df["High"] >= df["Low"]).all(), "High < Low found"
    assert (df["Volume"] >= 0).all(), "Negative volume found"
    assert (df[["Open", "High", "Low", "Close"]] > 0).all().all(), "Non-positive price found"

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_DIR / f"{ticker}_clean.parquet")
    return df