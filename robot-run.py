# -*- coding: utf-8 -*-
from app.BinanceAPI import BinanceAPI
from app.authorization import api_key,api_secret
from app.dingding import Message
from app.OrderManager import OrderManager

import time
import datetime
import schedule
import math
import json,os
from strategyConfig import binance_market,binance_coinBase,binance_tradeCoin, binance_coinBase_count

msgDing = Message()
orderManagers = []

for market in binance_tradeCoin:
    orderManager = OrderManager(binance_coinBase, binance_coinBase_count, market, binance_market)
    orderManagers.append(orderManager)

# 发送消息通知
def sendInfoToDingDing( message, isDefaultToken):
    # 记录执行时间
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    message = str(ts) + "\n" + message
    msgDing.dingding_warn(message, isDefaultToken)


def binance_func():
    """
    该函数用于遍历orderManagers列表中的每个orderManager对象，并调用其binance_func方法。
    每次调用binance_func方法后，程序会暂停5秒。
    """
    for orderManager in orderManagers:
        orderManager.binance_func()
        time.sleep(5)


def sendServiceInfo():
    str = "服务正常--ok"
    sendInfoToDingDing(str, True)

# 创建循环任务
def tasklist():
    #清空任务
    schedule.clear()
    #创建一个按秒间隔执行任务
    # schedule.every().hours.at("04:05").do(binance_func)

    #
    schedule.every(15).seconds.do(binance_func)

    schedule.every(20).minutes.do(sendServiceInfo)


    while True:
        schedule.run_pending()
        time.sleep(1)


# 调试看报错运行下面，正式运行用上面
if __name__ == "__main__":

    # 启动，先从币安获取交易规则， https://api.binance.com/api/v3/exchangeInfo
    tasklist()

    # binance_func()

