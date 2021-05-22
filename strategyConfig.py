# -*- coding: utf-8 -*-


#订单存储路径
orderInfo_path = "./buyOrderInfo.json"

# 是否分批卖出
isOpenSellStrategy = True
#分批卖出，盈利百分比
sellStrategy1 = {"profit":1.03, "sell":0.1}#盈利3%时，卖出10%的仓位
sellStrategy2 = {"profit":1.10, "sell":0.2}
sellStrategy3 = {"profit":1.20, "sell":0.3}


# 均线, ma_x 要大于 ma_y
ma_x = 5
ma_y = 60

# 币安
binance_market = "SPOT"#现货市场
binance_coinBase = "USDT"#使用USDT作为基础币种，用于购买其他货币；
binance_tradeCoin = "DOGE"#交易目标是 DOGE 币，
kLine_type = '5m' # 15分钟k线类型，你可以设置为5分钟K线：5m;1小时为：1h;1天为：1d