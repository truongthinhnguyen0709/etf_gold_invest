import polars as pl
import numpy as np
import pandas as pd
import yfinance as yf
import httpx
from datetime import date, datetime
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Send telegram function
def send_telegram_msg(ticker, price, peak, zone, benchmark,  percentile):
    token = TELEGRAM_BOT_TOKEN
    chat_id = TELEGRAM_CHAT_ID

    message = (
        f"""
🚀 Stock Alert
------------------
1. Ticker: {ticker}
2. Price: {price:.2f}
3. Peak: {peak:.2f}
4. Zone: {zone}
5. Benchmark: {benchmark:.2f}
6. Percentile: {percentile:.2f}
        """
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = httpx.post(url,data=payload)
    return response.json()



def yfinance_tele(ticker):
    df_raw = yf.download(ticker,period='10y', multi_level_index=False).reset_index()
    
    df_ticker_polars = pl.from_pandas(df_raw)
    
    df_output_clean = (
        df_ticker_polars
        .select('Date','Close')
            
        # 1. Tính z-price trong 50 ngày
        .with_columns(
            mean_avg = pl.col('Close').rolling_mean(window_size =50),
            std = pl.col('Close').rolling_std(window_size=50),
            
        )
        .with_columns(
            z_price = (pl.col('Close')-pl.col('mean_avg'))/pl.col('std')
        )
        
    
        # 2. Tính Peak và drawdown
        .with_columns(
            peak = pl.col('Close').cum_max()
        )
        .with_columns(
            drawdown = (pl.col('Close') - pl.col('peak'))/ pl.col('peak') *100
        )
        .with_columns(
            drawdown_percentile = (
                (pl.col('drawdown').rank(method='average'))/pl.col('drawdown').count()
            )*100
        ) # chỗ này tính vị trí percentile của drawdown
        
    
        # 3. Tạo zone
        .with_columns(
        zone=pl.when(pl.col("drawdown_percentile") >= 75)
          .then(pl.lit("Floor_4"))
          .when(pl.col("drawdown_percentile") >= 50)
          .then(pl.lit("Floor_3"))
          .when(pl.col("drawdown_percentile") >= 25)
          .then(pl.lit("Floor_2"))
          .otherwise(pl.lit("Floor_1")),
    
        p25_price=pl.col("peak") * (1 + pl.col("drawdown").quantile(0.25) / 100)
        )
        
    
        
    )
    
    row_dict = df_output_clean.tail(1).to_dicts()[0]

    result_dict = {
    "ticker": ticker, # Thay mã cổ phiếu thực tế của bạn vào đây
    "price": row_dict.get("Close"),
    "peak": row_dict.get("peak"),
    "zone": row_dict.get("zone"),
    "benchmark": row_dict.get('p25_price'), # Hoặc điền giá trị benchmark nếu có
    "percentile": row_dict.get("drawdown_percentile")
    }
    
    return result_dict

if __name__ == '__main__':
    # Vietnamese ETFs use the Yahoo ".VN" suffix
    tickers = ['FUEVFVND.VN', 'E1VFVN30.VN', 'FUEVN100.VN', 'FUESSVFL.VN', 'XAUT-USD']

    for symbol in tickers:
        try:
            payload_msg = yfinance_tele(symbol)
            send_telegram_msg(**payload_msg)
        except Exception as e:
            print(symbol, e)
