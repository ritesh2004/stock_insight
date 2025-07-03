import os
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime

MEDIA_DIR = "media/"
MODEL_PATH = os.path.dirname(__file__) + "/stock_prediction_model.keras"

def save_plot(path):
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path

def fetch_ohlcv_data(ticker: str) -> pd.DataFrame:
    df = yf.download(ticker, period="10y", interval="1d")
    if df is None or df.empty:
        raise ValueError(f"No data for ticker: {ticker}")
    return df

def predict_with_plot(ticker: str):
    df = fetch_ohlcv_data(ticker)

    # Split data
    train = df.Close[0:int(len(df)*0.7)]
    test = df.Close[int(len(df)*0.7):]

    scaler = MinMaxScaler(feature_range=(0, 1))
    model = load_model(MODEL_PATH)

    past_100 = train.tail(100)
    final_df = pd.concat([past_100, test], ignore_index=True)
    input_data = scaler.fit_transform(final_df.values.reshape(-1, 1))

    x_test, y_test = [], []
    for i in range(100, len(input_data)):
        x_test.append(input_data[i-100:i])
        y_test.append(input_data[i, 0])
    x_test, y_test = np.array(x_test), np.array(y_test)

    y_pred = model.predict(x_test)
    y_pred = scaler.inverse_transform(y_pred)
    y_test = scaler.inverse_transform(y_test.reshape(-1, 1))

    # Plot prediction
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(MEDIA_DIR, f"{ticker}_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    plt.figure(figsize=(12, 5))
    plt.plot(y_test, 'b', label='Original Price')
    plt.plot(y_pred, 'r', label='Predicted Price')
    plt.title(f'Final Prediction for {ticker}')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.legend()
    pred_path = os.path.join(out_dir, "predicted.png")
    save_plot(pred_path)

    # Plot historical prices
    plt.figure(figsize=(12, 5))
    df['Close'].plot(title=f"{ticker} Closing Price History")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend(['Close Price'])
    history_path = os.path.join(out_dir, "history.png")
    save_plot(history_path)

    return {
        "next_day_price": float(y_pred[-1][0]),
        "plot_urls": [history_path, pred_path],
        "metrics": {
            "mse": float(mean_squared_error(y_test, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "r2": float(r2_score(y_test, y_pred))
        }
    }
    