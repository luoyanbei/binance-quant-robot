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
from strategyConfig import binance_market,binance_coinBase,binance_tradeCoin


orderManager = OrderManager(binance_coinBase, binance_tradeCoin, binance_market)


orderManager_SHIB = OrderManager(binance_coinBase, "BTC", binance_market)



def binance_func():
    orderManager.binance_func()
    # time.sleep(10)
    # orderManager_SHIB.binance_func()


# 创建循环任务
def tasklist():
    #清空任务
    schedule.clear()
    #创建一个按秒间隔执行任务
    # schedule.every().hours.at("04:05").do(binance_func)
    # schedule.every().hours.at("09:10").do(binance_func)
    # schedule.every().hours.at("14:10").do(binance_func)
    # schedule.every().hours.at("19:10").do(binance_func)
    # schedule.every().hours.at("24:05").do(binance_func)
    # schedule.every().hours.at("29:10").do(binance_func)
    # schedule.every().hours.at("34:10").do(binance_func)
    # schedule.every().hours.at("39:10").do(binance_func)
    # schedule.every().hours.at("44:05").do(binance_func)
    # schedule.every().hours.at("49:10").do(binance_func)
    # schedule.every().hours.at("54:10").do(binance_func)
    # schedule.every().hours.at("59:10").do(binance_func)

    schedule.every(5).minutes.do(binance_func)

    # schedule.every().hours.at("12:05").do(binance_func)
    # schedule.every().hours.at("27:10").do(binance_func)
    # schedule.every().hours.at("42:15").do(binance_func)
    # schedule.every().hours.at("57:20").do(binance_func)


    while True:
        schedule.run_pending()
        time.sleep(1)


# 调试看报错运行下面，正式运行用上面
if __name__ == "__main__":

    # 启动，先从币安获取交易规则， https://api.binance.com/api/v3/exchangeInfo
    tasklist()

    # binance_func()

