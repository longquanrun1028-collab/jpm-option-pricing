import math
import pandas as pd
from scipy.stats import norm
from model_config import CONFIG

# 基础BSM欧式看涨/看跌定价函数
def bsm_european(S, K, T, r, sigma, opt_type="call"):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if opt_type == "call":
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# Rubinstein Chooser Option 选择权期权定价公式
def chooser_option_price(S, K, T1, T2, r, sigma):
    """
    S: 标的资产现价
    K: 统一行权价（论文固定K=150）
    T1: 选择日距离当前时间（年）
    T2: 期权总到期时间（论文固定T2=1年）
    r: 无风险年化利率（小数）
    sigma: 标的年化波动率
    定价拆解：Chooser = 长期看涨期权 + 短期看跌期权
    """
    tau = T2 - T1
    call_long = bsm_european(S, K, T2, r, sigma, "call")
    strike_pv = K * math.exp(-r * tau)
    put_short = bsm_european(S, strike_pv, T1, r, sigma, "put")
    return call_long + put_short

if __name__ == "__main__":
    # 读取第二周特征工程数据集
    df = pd.read_csv("auto_feature_dataset.csv", parse_dates=["Date"])
    
    # 从配置文件读取统一参数
    K = CONFIG["strike_K"]
    T2 = CONFIG["T2_total_expiry"]
    T1 = CONFIG["T1_choice_date"]
    rate_div = CONFIG["rate_divisor"]

    # 批量计算每日选择权期权理论价格
    df["Chooser_Price"] = df.apply(
        lambda row: chooser_option_price(
            S=row[CONFIG["underlying_price"]],
            K=K,
            T1=T1,
            T2=T2,
            r=row[CONFIG["risk_free_rate_series"]] / rate_div,
            sigma=row[CONFIG["volatility_series"]]
        ), axis=1
    )

    # 筛选输出核心字段，保存结果数据集
    output_cols = ["Date", "Close", "vol_20d", "10Y_Treasury", "Chooser_Price"]
    result_df = df[output_cols].copy()
    result_df.to_csv("week3_chooser_bsm_result.csv", index=False, encoding="utf-8-sig")
    print("✅ BSM选择权期权批量定价完成，文件：week3_chooser_bsm_result.csv")
    print(result_df.head())

    # 论文基准静态校验（对标文献标准测试值）
    bench_S = 150
    bench_r = 0.04
    bench_sigma = 0.2
    bench_price = chooser_option_price(bench_S, K, T1, T2, bench_r, bench_sigma)
    print(f"\n文献基准校验价格(S=150, r=4%, σ=20%)：{bench_price:.4f}")
