# Stock Price Predictor (AAPL)

A machine learning project that tests whether daily AAPL price movements can be predicted from technical indicators, with a strict focus on avoiding data leakage.

## What I did
1. **EDA:** found that prices are non-stationary (slowly decaying ACF), so I predict next-day returns instead of price levels.
2. **Features:** lagged returns, moving-average ratios, volatility, RSI, MACD. Every feature at day t uses only data up to day t.
3. **Chronological split:** train up to 2021, validation 2022-2023, test 2024 onward. No shuffling.
4. **Baselines:** predict 0, predict the training average, same as today, always predict up.
5. **Models:** Ridge, Random Forest, Gradient Boosting.
6. **Walk-forward evaluation** (2023-2026), retraining each year.
7. **Backtest** vs buy-and-hold with 0.1% trading cost.

## Results
| Model | MAE | RMSE | Up/Down accuracy |
|---|---|---|---|
| Train average (baseline) | 0.01165 | 0.01729 | 0.542 |
| Ridge | 0.01188 | 0.01751 | 0.490 |
| Random Forest | 0.01171 | 0.01735 | 0.520 |
| Gradient Boosting | 0.01188 | 0.01758 | 0.532 |

- Walk-forward Random Forest accuracy averaged 52.6% vs 54.6% for "always up".
- Backtest: strategy ended at $1.85 vs $2.75 for buy-and-hold.

## Conclusion
With these features, no model beat simple baselines. Daily stock direction is very noisy, and results in the 50-54% range are expected. The value of this project is the leakage-free pipeline and honest evaluation, not a trading edge.

## Possible next steps
- Add market-wide features (S&P 500, VIX, sector data)
- Try a direction classifier and probability thresholds
- Try an LSTM

## How to run
pip install -r requirements.txt, then run notebooks/01_eda.ipynb and notebooks/02_modeling.ipynb.