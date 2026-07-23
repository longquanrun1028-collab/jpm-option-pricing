import pandas as pd
import numpy as np
import os

def clean_data(df):
    """数据清洗：时间对齐、插值、IQR异常值处理"""
    trading_days = pd.bdate_range(start=df.index.min(), end=df.index.max())
    df = df.reindex(trading_days)
    df = df.interpolate(method="time").ffill().bfill()
    
    def iqr_winsorize(s, factor=1.5):
        Q1 = s.quantile(0.25)
        Q3 = s.quantile(0.75)
        IQR = Q3 - Q1
        return s.clip(lower=Q1 - factor*IQR, upper=Q3 + factor*IQR)
    
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = iqr_winsorize(df[col])
    return df

def build_features(df):
    """特征工程：传统+高级金融特征"""
    df["daily_return"] = df["Close"].pct_change()
    df["vol_20d"] = df["daily_return"].rolling(20).std() * (252**0.5)
    df["vol_60d"] = df["daily_return"].rolling(60).std() * (252**0.5)
    df["vol_120d"] = df["daily_return"].rolling(120).std() * (252**0.5)
    df["dividend_growth"] = (df["Adj Close"] / df["Close"]).pct_change().rolling(20).mean()
    df["vix_jpm_corr_20d"] = df["VIX_Close"].rolling(20).corr(df["Close"])
    df["rate_momentum_5d"] = df["10Y_Treasury"].diff(5)
    df["rate_momentum_20d"] = df["10Y_Treasury"].diff(20)
    vol_norm = (df["Volume"] - df["Volume"].rolling(20).mean()) / df["Volume"].rolling(20).std()
    df["sentiment_score"] = 1 / (1 + np.exp(-(vol_norm * np.sign(df["daily_return"]))))
    return df.dropna()

if __name__ == "__main__":
    df = pd.read_csv("cleaned_dataset.csv")
    df.rename(columns={df.columns[0]: "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    cleaned_df = clean_data(df)
    final_df = build_features(cleaned_df)
    final_df.to_csv("auto_feature_dataset.csv", encoding="utf-8-sig")
    print("✅ 流水线运行完成！数据已更新")