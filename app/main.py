from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.model_service import get_prediction

BASE_DIR = Path(__file__).parent

app = FastAPI(title="Stock Price Predictor")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/predict/{ticker}")
def predict(ticker: str):
    ticker = ticker.strip()
    if not ticker.replace(".", "").replace("-", "").isalnum() or len(ticker) > 10:
        raise HTTPException(status_code=400, detail="Invalid ticker symbol.")
    try:
        return get_prediction(ticker)
    except Exception as exc:
        print(f"Prediction failed for {ticker}: {exc}")
        raise HTTPException(
            status_code=404,
            detail=f"Could not load enough data for '{ticker.upper()}'.",
        )


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")