# Week3 BSM Chooser Option 全局参数配置（对齐论文标准）
CONFIG = {
    # 期权时间参数
    "T2_total_expiry": 1.0,    # 总到期期限 1年
    "T1_choice_date": 0.5,     # 选择日距离现在0.5年
    # 行权参数
    "strike_K": 150,
    # 数据映射列名（对接Week2特征数据集）
    "underlying_price": "Close",
    "volatility_series": "vol_20d",
    "risk_free_rate_series": "10Y_Treasury",
    # 百分比利率转小数除数
    "rate_divisor": 100
}
