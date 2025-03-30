import requests
import pandas as pd
import time
import os
from datetime import datetime

# データ格納ディレクトリ
DATA_DIR = "data/minute"
LOG_FILE = "errors.log"

# ディレクトリがなければ作成
os.makedirs(DATA_DIR, exist_ok=True)

# 取得したい銘柄リスト（100銘柄を想定）
symbols =[
    "7012.T", "7011.T", "6146.T", "6857.T", "7203.T", "8306.T", "5803.T", "2432.T", "8316.T", "8035.T",
    "6758.T", "9983.T", "7013.T", "9984.T", "8411.T", "6501.T", "6098.T", "7974.T", "8136.T", "6861.T",
    "6920.T", "9104.T", "7267.T", "4676.T", "8058.T", "8725.T", "8766.T", "4063.T", "9101.T", "9432.T",
    "285A.T", "7182.T", "8001.T", "4502.T", "9749.T", "8031.T", "2914.T", "7741.T", "7936.T", "6702.T",
    "6981.T", "5016.T", "6503.T", "6752.T", "6902.T", "6273.T", "9433.T", "9434.T", "6723.T", "4568.T",
    "6954.T", "4755.T", "8630.T", "5401.T", "4751.T", "6367.T", "6532.T", "7751.T", "4661.T", "6701.T",
    "8604.T", "8002.T", "7261.T", "7201.T", "4519.T", "8053.T", "6762.T", "8801.T", "9021.T", "8309.T",
    "1605.T", "5108.T", "4543.T", "9020.T", "7735.T", "7003.T", "9107.T", "7270.T", "7269.T", "8802.T",
    "8308.T", "4004.T", "9501.T", "5411.T", "6301.T", "6201.T", "7832.T", "5801.T", "8591.T", "4503.T",
    "6526.T", "5406.T", "4901.T", "4578.T", "8750.T", "5838.T", "6594.T", "2502.T", "5802.T", "^N225"
] # ここに100銘柄入れる

# 取得するデータの設定
interval = "5m"  # 5分足
range_period = "60d"  # 60日分

# Yahoo! APIからデータを取得する関数
def fetch_stock_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_period}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生
        data = response.json()

        # データが取得できない場合
        if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
            raise ValueError(f"⚠ データなし: {symbol}")

        chart = data["chart"]["result"][0]
        timestamps = chart.get("timestamp")
        ohlc = chart.get("indicators", {}).get("quote", [{}])[0]

        if timestamps is None or not all(k in ohlc for k in ["close","high","low","open","volume"]):
            raise ValueError(f"❌ データ不完全: {symbol}")

        # データフレームを作成
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(timestamps, unit="s")  # UNIX時間を変換
                .tz_localize("UTC")  # UTCとして認識
                .tz_convert("Asia/Tokyo"),  # 日本時間に変換
            "open": ohlc["open"],
            "high": ohlc["high"],
            "low": ohlc["low"],
            "close": ohlc["close"],
            "volume": ohlc["volume"]
        })

        return df

    except Exception as e:
        error_message = f"{datetime.now()} - {symbol} - {str(e)}\n"
        print(f"🚨 エラー: {error_message.strip()}")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(error_message)
        return None

# 100銘柄のデータを取得
for i, symbol in enumerate(symbols):
    print(f"📊 {i+1}/{len(symbols)}: {symbol} のデータ取得中...")
    df = fetch_stock_data(symbol)

    if df is not None:
        # ファイルパスを指定
        file_path = os.path.join(DATA_DIR, f"{symbol}_minute.csv")
        temp_file_path = file_path + ".tmp"

        try:
            # 一時ファイルに保存してからリネーム（書き込みエラー防止）
            df.to_csv(temp_file_path, index=False)
            if os.path.exists(file_path):
                os.remove(file_path)
            os.rename(temp_file_path, file_path)

            print(f"✅ {symbol} のデータを {file_path} に保存しました！")

        except Exception as e:
            error_message = f"{datetime.now()} - {symbol} - ファイル保存エラー: {str(e)}\n"
            print(f"🚨 エラー: {error_message.strip()}")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(error_message)

    # API制限対策のため1秒待つ
    time.sleep(1)

print("✅ 全銘柄のデータ取得処理が完了しました！")
