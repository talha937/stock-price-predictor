import numpy as np
import pandas as pd


def add_features(df: pd.DataFrame, price_col: str = "Adj Close", training: bool = True) -> pd.DataFrame:
    out = df.copy()
    p = out[price_col]

    # Returns and lagged returns
    out["ret_1"] = p.pct_change()
    for lag in (1, 2, 3, 5, 10):
        out[f"ret_lag_{lag}"] = out["ret_1"].shift(lag)

    # Trend: price relative to moving averages
    for w in (5, 10, 20, 50):
        out[f"sma_{w}_ratio"] = p / p.rolling(w).mean() - 1

    # Volatility
    out["vol_10"] = out["ret_1"].rolling(10).std()
    out["vol_30"] = out["ret_1"].rolling(30).std()

    # RSI (14)
    delta = p.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    out["rsi_14"] = 100 - 100 / (1 + gain / loss)

    # MACD (normalized by price)
    ema12 = p.ewm(span=12, adjust=False).mean()
    ema26 = p.ewm(span=26, adjust=False).mean()
    out["macd"] = (ema12 - ema26) / p

    # Volume change
    out["vol_chg"] = out["Volume"].pct_change()

    # Targets: next-day return and direction
    out["target_ret"] = p.pct_change().shift(-1)
    out["target_dir"] = (out["target_ret"] > 0).astype(int)

    out = out.replace([np.inf, -np.inf], np.nan)

    # For the API: keep the newest day (it has no "tomorrow" yet)
    if not training:
        return out.drop(columns=["target_ret", "target_dir"]).dropna()

    # For training: normal behavior, same as before
    return out.dropna()