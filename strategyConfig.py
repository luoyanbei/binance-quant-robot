# -*- coding: utf-8 -*-


#订单存储路径
orderInfo_path = "./buyOrderInfo.json"



# 均线, ma_x 要大于 ma_y
ma_x = 5
ma_y = 60

# 币安
binance_market = "SPOT"#现货市场
binance_coinBase = "USDT"#使用USDT作为基础币种，用于购买其他货币；
# 允许使用账户中的 binance_coinBase 对应个数，每次买入 最多使用 binance_coinBase_count 个 binance_coinBase
binance_coinBase_count = 50
binance_tradeCoin = "DOGE"#交易目标是 DOGE 币，
kLine_type = '5m' # 5分钟k线类型，你可以设置为15分钟K线：15m;1小时为：1h;1天为：1d