import time

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

    predicted = float(model.predict(latest[cols].iloc[[-1]])[0])
    baseline = float(train["target_ret"].mean())

    history = df["Adj Close"].tail(90)

    result = {
        "ticker": ticker,
        "as_of": history.index[-1].strftime("%Y-%m-%d"),
        "last_close": round(float(history.iloc[-1]), 2),
        "predicted_return": predicted,
        "baseline_return": baseline,
        "lean": "up" if predicted > baseline else "down",
        "history": {
            "dates": [d.strftime("%Y-%m-%d") for d in history.index],
            "prices": [round(float(p), 2) for p in history],
        },
        "model_accuracy": MODEL_ACCURACY,
        "always_up_accuracy": ALWAYS_UP_ACCURACY,
    }

    _cache[ticker] = {"time": time.time(), "result": result}
    return result