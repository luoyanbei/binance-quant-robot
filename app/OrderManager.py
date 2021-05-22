# -*- coding: utf-8 -*-

import json, os, time, datetime, math
from app.BinanceAPI import BinanceAPI

from app.authorization import api_key,api_secret
from app.dingding import Message
from DoubleAverageLines_static import DoubleAverageLines
import schedule
from strategyConfig import orderInfo_path, sellStrategy1, sellStrategy2, sellStrategy3 , ma_x, ma_y, isOpenSellStrategy, kLine_type


binan = BinanceAPI(api_key,api_secret)
msg = Message()

dALines = DoubleAverageLines()


class ExchangeRule(object):
    def __init__(self, dict):
        if dict is not None and 'symbol' in dict:
            self.symbol = dict['symbol']
            self.baseAsset = dict['baseAsset']
            self.baseAssetPrecision = dict['baseAssetPrecision']
            self.quoteAsset = dict['quoteAsset']
            self.quoteAssetPrecision = dict['quoteAssetPrecision']

            filters = dict['filters']
            for filter in filters:
                if filter['filterType'] == 'PRICE_FILTER':
                    # "minPrice": "0.00001000",
                    # "maxPrice": "1000.00000000",
                    # "tickSize": "0.00001000"
                    self.minPrice = filter['minPrice']
                    self.maxPrice = filter['maxPrice']
                    self.tickSize = filter['tickSize']

                if filter['filterType'] == 'LOT_SIZE':
                    # "minQty": "0.10000000",
                    # "maxQty": "9000000.00000000",
                    # "stepSize": "0.10000000"
                    self.minQty = filter['minQty']
                    self.maxQty = filter['maxQty']
                    self.stepSize = filter['stepSize']




class OrderManager(object):

    def __init__(self, coinBase, tradeCoin, market):
        self.coin_base = coinBase # 基础币，例如USDT
        self.trade_coin = tradeCoin #买卖币种，例如 DOGER
        self.market = market #市场，例如：现货 "SPOT"
        self.symbol = tradeCoin+coinBase #交易符号，例如"DOGEUSDT"
        self.exchangeRule = None


    def gain_exchangeRule(self, theSymbol):
        if self.exchangeRule is None:
            dict = binan.exchangeInfo()
            if dict is not None and 'symbols' in dict:
                symbol_list = dict['symbols']
                for tmp_symbol in symbol_list:
                    if tmp_symbol['symbol']==theSymbol:
                        self.exchangeRule = ExchangeRule(tmp_symbol)
                        break;

        # return self.exchangeRule

    #  执行卖出
    def doSellFunc(self,symbol ,quantity, cur_price):
        # 卖出
        res_order_sell = binan.sell_limit(symbol, quantity, cur_price)
        print("出售部分结果：")
        print(res_order_sell)
        order_result_str = self.printOrderJsonInfo(res_order_sell)
        msgInfo = "卖出部分结果：\n" + str(order_result_str)

        return msgInfo


    # 格式化交易信息结果
    def printOrderJsonInfo(self, orderJson):
        str_result = ""
        if type(orderJson).__name__ == 'dict':
            all_keys = orderJson.keys()
            if 'symbol' in orderJson and 'orderId' in orderJson:

                time_local = time.localtime(orderJson['transactTime'] / 1000)
                time_str = time.strftime('%Y-%m-%d %H:%M:%S', time_local)

                str_result = str_result + "时间：" + str(time_str) + "\n"
                str_result = str_result + "币种：" + str(orderJson['symbol']) + "\n"
                str_result = str_result + "价格：" + str(orderJson['price']) + "\n"
                str_result = str_result + "数量：" + str(orderJson['origQty']) + "\n"
                str_result = str_result + "方向：" + str(orderJson['side']) + "\n"
            else:
                str_result = str(orderJson)
        else:
            str_result = str(orderJson)

        return str_result

    # 读取本地存储的买入订单信息
    def readOrderInfo(self, filePath):
        if os.path.exists(filePath) is False:
            return None

        with open(filePath, 'r') as f:
            data = json.load(f)
            print("读取--买入信息：")
            print(data)
            if 'symbol' in data and 'orderId' in data and 'price' in data:
                return data
            else:
                return None

    # 获取 上次买入订单中的价格Price
    def priceOfPreviousOrder(self, filePath):
        dataDict = self.readOrderInfo(filePath)
        thePrice = 0.0

        if dataDict is not None and 'price' in dataDict:
            thePrice = float(dataDict['price'])

        return thePrice

    # 清理 本地存储的买入订单信息
    def clearOrderInfo(self, filePath):
        if os.path.exists(filePath) is True:
            os.remove(filePath)
            print("清理订单信息---do")

    # 存储 买入订单信息
    def writeOrderInfo(self, filePath, dictObj):

        self.clearOrderInfo(filePath)
        print("写入--买入信息：")
        print(dictObj)
        with open(filePath, 'w') as f:
            json.dump(dictObj, f)


    def writeOrderInfoWithSellStrategy(self,filePath, dictObj):

        if isOpenSellStrategy:
            dictObj["sellStrategy1"] = sellStrategy1
            dictObj["sellStrategy2"] = sellStrategy2
            dictObj["sellStrategy3"] = sellStrategy3

        self.writeOrderInfo(filePath, dictObj)


    # 获取K线列表
    def gain_kline(self, symbol, timeInterval='15m'):
        # 结束时间
        millis_stamp = int(round(time.time() * 1000))

        # 如何处理虚假买点和虚假卖点，1000条数据中，第一条可能产生虚假的买点和卖点
        kline_json = binan.get_klines(symbol, timeInterval, 1000, None, millis_stamp)
        if type(kline_json).__name__ == 'list':
            return kline_json
        else:
            return None

    # 根据交易规则，格式化交易量
    def format_trade_quantity(self, originalQuantity):
        minQty = float(self.exchangeRule.minQty)
        print(self.symbol + " 原始交易量= "+str(originalQuantity))
        print(self.symbol + " 最小交易量限制= "+str(minQty))

        if self.exchangeRule is not None and minQty>0:
            newQuantity = (originalQuantity//minQty)*minQty
        else:
            newQuantity = math.floor(originalQuantity)
        print(self.symbol + " 交易量格式化= "+str(newQuantity))
        return newQuantity

    def binance_func(self):
        print("币种= "+self.trade_coin)
        try:
            self.gain_exchangeRule(self.symbol)

            msgInfo = ""  # 钉钉消息
            isDefaultToken = False

            # 记录执行时间
            now = datetime.datetime.now()
            ts = now.strftime('%Y-%m-%d %H:%M:%S')
            print('do func time：', ts)
            msgInfo = msgInfo + str(ts) + "\n"

            # 获取K线数据
            kline_list = self.gain_kline(self.symbol, kLine_type)
            # k线数据转为 DataFrame格式
            kline_df = dALines.klinesToDataFrame(kline_list)

            # 判断交易方向
            trade_direction = dALines.release_trade_stock(ma_x, ma_y, self.symbol, kline_df)

            if trade_direction is not None:
                if trade_direction == "buy":
                    # coin_base = "USDT"
                    asset_coin = binan.get_spot_asset_by_symbol(self.coin_base)
                    print(self.coin_base + " 资产：")
                    print(asset_coin)

                    # 查询当前价格
                    cur_price = binan.get_ticker_price(self.symbol)
                    # 购买量
                    quantity = self.format_trade_quantity(float(asset_coin["free"]) / float(cur_price))
                    # 购买
                    res_order_buy = binan.buy_limit(self.symbol, quantity, cur_price)
                    print("购买结果：")
                    print(res_order_buy)

                    # 存储买入订单信息
                    if res_order_buy is not None and "symbol" in res_order_buy:
                        self.writeOrderInfoWithSellStrategy(orderInfo_path, res_order_buy)

                    order_result_str = self.printOrderJsonInfo(res_order_buy)
                    msgInfo = "购买结果：\n" + order_result_str

                elif trade_direction == "sell":
                    # coin_base = "DOGE"
                    asset_coin = binan.get_spot_asset_by_symbol(self.trade_coin)
                    print(self.trade_coin + " 资产：")
                    print(asset_coin)

                    quantity = self.format_trade_quantity(float(asset_coin["free"]))

                    # 查询当前价格
                    cur_price = binan.get_ticker_price(self.symbol)

                    # 卖出
                    res_order_sell = binan.sell_limit(self.symbol, quantity, cur_price)
                    # 清理本地订单信息
                    self.clearOrderInfo(orderInfo_path)
                    print("出售结果：")
                    print(res_order_sell)
                    order_result_str = self.printOrderJsonInfo(res_order_sell)
                    msgInfo = "卖出结果：\n" + str(order_result_str)

            else:
                # msgInfo = msgInfo + str(ts) + "\n"
                print("暂不执行任何交易2")
                msgInfo = msgInfo + "服务正常2"
                isDefaultToken = True

            print("-----------------------------------------------\n")
        except Exception as ex:
            err_str = "出现如下异常：%s" % ex
            print(err_str)
            msgInfo = msgInfo + str(err_str) + "\n"

        finally:
            msg.dingding_warn(msgInfo, isDefaultToken)
