import time

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from src.data_cleaning import clean_stock_data
from src.data_loader import download_stock_data
from src.features import add_features

# Same feature rule you used in the notebook
FEATURE_PREFIXES = ("ret_", "sma_", "vol_", "rsi", "macd")

# Results from your walk-forward test (2023-2026). Update these if you re-run it.
MODEL_ACCURACY = 0.526
ALWAYS_UP_ACCURACY = 0.546

CACHE_SECONDS = 60 * 60  # keep each ticker's result for 1 hour
_cache = {}


def _describe(name: str, v: float) -> str:
    """Turn one feature value into a plain-English sentence."""
    if name == "ret_1":
        return f"Today's price change was {v * 100:+.2f}%."
    if name.startswith("ret_lag_"):
        days = int(name.split("_")[-1])
        when = "yesterday" if days == 1 else f"{days} trading days ago"
        return f"The price change {when} was {v * 100:+.2f}%."
    if name.startswith("sma_"):
        window = name.split("_")[1]
        side = "above" if v >= 0 else "below"
        return f"The price is {abs(v) * 100:.1f}% {side} its {window}-day average."
    if name.startswith("vol_chg"):
        return f"Trading volume changed {v * 100:+.0f}% since yesterday."
    if name.startswith("vol_"):
        return f"Over the last {name.split('_')[1]} days, daily price swings averaged {v * 100:.2f}%."
    if name == "rsi_14":
        if v > 70:
            note = "often called overbought: the price rose fast"
        elif v < 30:
            note = "often called oversold: the price fell fast"
        else:
            note = "a neutral zone"
        return f"The RSI (a speed-of-change gauge) is {v:.0f}, {note}."
    if name == "macd":
        trend = "stronger" if v >= 0 else "weaker"
        return f"The short-term trend is {trend} than the longer-term trend."
    return name


def _reasons(model, x, medians, predicted: float, cols) -> list:
    """Find the 3 inputs that pushed this guess the most.

    For the 5 most important inputs, swap the value for a typical (median) day and
    see how the guess changes. The change is how much that input pushed it up or down.
    """
    top = pd.Series(model.feature_importances_, index=cols).nlargest(5).index
    found = []
    for c in top:
        alt = x.copy()
        alt[c] = medians[c]
        push = predicted - float(model.predict(alt)[0])
        found.append((
            abs(push),
            {"text": _describe(c, float(x[c].iloc[0])), "effect": "up" if push > 0 else "down"},
        ))
    found.sort(key=lambda t: -t[0])
    return [item for _, item in found[:3]]


def get_prediction(ticker: str) -> dict:
    ticker = ticker.upper().strip()

    cached = _cache.get(ticker)
    if cached and time.time() - cached["time"] < CACHE_SECONDS:
        return cached["result"]

    raw = download_stock_data(ticker)
    df = clean_stock_data(raw, ticker)

    train = add_features(df)                       # has targets, last day dropped
    latest = add_features(df, training=False)      # keeps the most recent day
    cols = [c for c in train.columns if c.startswith(FEATURE_PREFIXES)]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=4,
        min_samples_leaf=20,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train[cols], train["target_ret"])

    x = latest[cols].iloc[[-1]]
    predicted = float(model.predict(x)[0])
    baseline = float(train["target_ret"].mean())
    reasons = _reasons(model, x, train[cols].median(), predicted, cols)

    history = df["Adj Close"].tail(90)

    result = {
        "ticker": ticker,
        "as_of": history.index[-1].strftime("%Y-%m-%d"),
        "last_close": round(float(history.iloc[-1]), 2),
        "predicted_return": predicted,
        "baseline_return": baseline,
        "lean": "up" if predicted > baseline else "down",
        "reasons": reasons,
        "history": {
            "dates": [d.strftime("%Y-%m-%d") for d in history.index],
            "prices": [round(float(p), 2) for p in history],
        },
        "model_accuracy": MODEL_ACCURACY,
        "always_up_accuracy": ALWAYS_UP_ACCURACY,
    }

    _cache[ticker] = {"time": time.time(), "result": result}
    return result