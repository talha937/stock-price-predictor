import pandas as pd  # type: ignore[reportMissingImports]
import yfinance as yf  # type: ignore[reportMissingImports]

from src.config import (  # type: ignore[reportMissingImports]
    END_DATE,
    RAW_DIR,
    START_DATE,
)


def download_stock_data(ticker: str, start=START_DATE, end=END_DATE) -> pd.DataFrame:
    """Download daily OHLCV data and save the raw copy."""
    df = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)

    if df.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'")

    # Newer yfinance versions return MultiIndex columns even for one ticker
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index.name = "Date"
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DIR / f"{ticker}_raw.csv")
    return df


if __name__ == "__main__":
    data = download_stock_data("AAPL")
    print(data.head())
    print(data.shape)