from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

DEFAULT_TICKER = "AAPL"
START_DATE = "2015-01-01"
END_DATE = None  # None = up to today