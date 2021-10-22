# -*- coding: utf-8 -*-


# 是否分批卖出
isOpenSellStrategy = True
#分批卖出，盈利百分比
sellStrategy1 = {"profit":1.05, "sell":0.1}#盈利5%时，卖出10%的仓位
sellStrategy2 = {"profit":1.10, "sell":0.2}#盈利10%时，卖出20%的仓位
sellStrategy3 = {"profit":1.20, "sell":0.2}#盈利20%时，卖出20%的仓位


# 均线, ma_x 要大于 ma_y
ma_x = 5
ma_y = 60

# 币安
binance_market = "SPOT"#现货市场
binance_coinBase = "USDT"#使用USDT作为基础币种，用于购买其他货币；
# 允许使用账户中的 binance_coinBase 对应个数，每次买入 最多使用 binance_coinBase_count 个 binance_coinBase
binance_coinBase_count = 100 #代表100个USDT
binance_tradeCoin = "DOGE"#交易目标是 DOGE 币，
kLine_type = '1h' # 15分钟k线类型，你可以设置为5分钟K线：5m;1小时为：1h;1天为：1d