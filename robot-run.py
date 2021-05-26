# -*- coding: utf-8 -*-
from app.BinanceAPI import BinanceAPI
from app.authorization import api_key,api_secret
from app.dingding import Message
from app.OrderManager import OrderManager

import time
# from DoubleAverageLines import DoubleAverageLines
import datetime
import schedule
import math
import json,os
from strategyConfig import binance_market,binance_coinBase,binance_tradeCoin,binance_coinBase_count


orderManager = OrderManager(binance_coinBase, binance_coinBase_count,binance_tradeCoin, binance_market)



def binance_func():
    orderManager.binance_func()


# 创建循环任务
def tasklist():
    #清空任务
    schedule.clear()

    # 每隔1分钟，执行一次，可自行设置为 5 分钟或其他时间；币安的api接口有请求次数限制，不要太频繁
    schedule.every(1).minutes.do(binance_func)


    while True:
        schedule.run_pending()
        time.sleep(1)


# 调试看报错运行下面，正式运行用上面
if __name__ == "__main__":

    # 启动，先从币安获取交易规则， https://api.binance.com/api/v3/exchangeInfo
    tasklist()

    # binance_func()

