# -*- coding: utf-8 -*-

import json, os, time, datetime, math
from app.BinanceAPI import BinanceAPI

from app.authorization import api_key,api_secret
from app.dingding import Message
from DoubleAverageLines_static import DoubleAverageLines
import schedule
from strategyConfig import sellStrategy1, sellStrategy2, sellStrategy3 , ma_x, ma_y, isOpenSellStrategy, kLine_type


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

    def __init__(self, coinBase, coinBaseCount , tradeCoin, market):
        self.coin_base = coinBase # 基础币，例如USDT
        self.coin_base_count = coinBaseCount # 买币时最多可用资金量
        self.trade_coin = tradeCoin #买卖币种，例如 DOGER
        self.market = market #市场，例如：现货 "SPOT"
        self.symbol = tradeCoin+coinBase #交易符号，例如"DOGEUSDT"
        self.exchangeRule = None
        self.orderInfoSavePath = "./"+ self.symbol +"_buyOrderInfo.json" #订单信息存储路径

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
        print("马上卖出 " + str(symbol)+" "+ str(quantity)+ " 个，单价："+str(cur_price))

        #如果总价值小于10
        if (quantity*cur_price)<10:
            quantity = self.format_trade_quantity(11.0/cur_price)
            if (quantity * cur_price) < 10:
                quantity = self.format_trade_quantity(13.0 / cur_price)
                if (quantity * cur_price) < 10:
                    quantity = self.format_trade_quantity(16.0 / cur_price)
                    if (quantity * cur_price) < 10:
                        quantity = self.format_trade_quantity(20.0 / cur_price)

        # 卖出
        res_order_sell = binan.sell_limit(symbol, quantity, cur_price)
        print("出售部分结果：")
        print("量："+str(quantity)+", 价格："+str(cur_price)+", 总价值："+str(quantity*cur_price))
        print(res_order_sell)
        order_result_str = self.printOrderJsonInfo(res_order_sell)
        msgInfo = "卖出结果：\n" + str(order_result_str)

        return msgInfo

    #分批出售策略
    def sellStrategy(self, filePath):
        msgInfo = ""
        dictOrder = self.readOrderInfo(filePath)
        if dictOrder is None:
            return msgInfo

        # 读取上次买入的价格
        buyPrice = self.priceOfPreviousOrder(self.orderInfoSavePath)
        if buyPrice > 0:
            # 查询当前价格
            cur_price = binan.get_ticker_price(self.symbol)
            print("当前 "+str(self.symbol)+" 价格："+str(cur_price))
            #查询当前资产
            asset_coin = binan.get_spot_asset_by_symbol(self.trade_coin)
            print(self.trade_coin + " 资产2：")
            print(asset_coin)

            if "sellStrategy3" in dictOrder:
                print("sellStrategy--sellStrategy3--1")
                tmpSellStrategy = dictOrder['sellStrategy3']
                print("买入价格："+str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(buyPrice * tmpSellStrategy['profit'])+" 和 当前价格：" + str(cur_price)+" 比较")
                if buyPrice * tmpSellStrategy['profit'] <= cur_price:
                    print("sellStrategy--sellStrategy3--2")

                    quantity = self.format_trade_quantity(float(asset_coin["free"])*tmpSellStrategy['sell'])
                    # 卖出
                    msgInfo= msgInfo + self.doSellFunc(self.symbol,quantity,cur_price)
                    del dictOrder['sellStrategy3']
                    self.writeOrderInfo(filePath, dictOrder)
                    dictOrder = self.readOrderInfo(filePath)
                    print("部分卖出--sellStrategy3")

            if "sellStrategy2" in dictOrder:
                tmpSellStrategy = dictOrder['sellStrategy2']
                print("sellStrategy--sellStrategy2--1")
                print("买入价格："+str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(buyPrice * tmpSellStrategy['profit'])+" 和 当前价格：" + str(cur_price)+" 比较")

                if buyPrice * tmpSellStrategy['profit'] <= cur_price:
                    print("sellStrategy--sellStrategy2--2")

                    quantity = self.format_trade_quantity(float(asset_coin["free"]) * tmpSellStrategy['sell'])
                    # 卖出
                    msgInfo = msgInfo + self.doSellFunc(self.symbol, quantity, cur_price)
                    del dictOrder['sellStrategy2']
                    self.writeOrderInfo(filePath, dictOrder)
                    dictOrder = self.readOrderInfo(filePath)
                    print("部分卖出--sellStrategy2")

            if "sellStrategy1" in dictOrder:
                tmpSellStrategy = dictOrder['sellStrategy1']
                print("sellStrategy--sellStrategy1--1")
                print("买入价格：" + str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(
                    buyPrice * tmpSellStrategy['profit']) + " 和 当前价格：" + str(cur_price) + " 比较")

                if buyPrice * tmpSellStrategy['profit'] <= cur_price:
                    print("sellStrategy--sellStrategy1--2")

                    quantity = self.format_trade_quantity(float(asset_coin["free"]) * tmpSellStrategy['sell'])
                    # 卖出
                    msgInfo = msgInfo + self.doSellFunc(self.symbol, quantity, cur_price)
                    del dictOrder['sellStrategy1']
                    self.writeOrderInfo(filePath, dictOrder)
                    dictOrder = self.readOrderInfo(filePath)
                    print("部分卖出--sellStrategy1")

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

    # 比较本次买入提示的str是否重复
    def judgeToBuyCommand(self, filePath, theToBuyCommand):
        orderDict = self.readOrderInfo(filePath)

        if orderDict is None:
            return True # 购买

        if "toBuy" in orderDict:
            if orderDict["toBuy"] == theToBuyCommand:
                print('本次购买时间是 '+str(theToBuyCommand)+' ，重复，不执行购买')
                return False #不执行购买，因为重复

        return True




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

                if "buy," in trade_direction:

                    isToBuy = self.judgeToBuyCommand(self.orderInfoSavePath, trade_direction)

                    if isToBuy is False:
                        msgInfo = msgInfo + "服务正常3"
                        isDefaultToken = True
                    else:
                        isDefaultToken = False

                        # coin_base = "USDT"
                        asset_coin = binan.get_spot_asset_by_symbol(self.coin_base)
                        print(self.coin_base + " 资产："+str(asset_coin))

                        # 购买，所用资金量
                        coin_base_count = float(asset_coin["free"])
                        if self.coin_base_count <= coin_base_count:
                            coin_base_count = self.coin_base_count

                        print("binance_func--可用资金量coin_base_count= "+str(coin_base_count))
                        # 查询当前价格
                        cur_price = binan.get_ticker_price(self.symbol)
                        # 购买量
                        quantity = self.format_trade_quantity(coin_base_count / float(cur_price))
                        # 购买
                        res_order_buy = binan.buy_limit(self.symbol, quantity, cur_price)
                        print("购买结果：")
                        print(res_order_buy)


                        # 存储买入订单信息
                        if res_order_buy is not None and "symbol" in res_order_buy:
                            res_order_buy["toBuy"] = trade_direction
                            self.writeOrderInfoWithSellStrategy(self.orderInfoSavePath, res_order_buy)

                        order_result_str = self.printOrderJsonInfo(res_order_buy)
                        msgInfo = "购买结果：\n" + order_result_str

                elif trade_direction == "sell":
                    dictOrder = self.readOrderInfo(self.orderInfoSavePath)


                    if dictOrder is None:
                        msgInfo = msgInfo + "服务正常4--已无可售"
                        isDefaultToken = True
                    else:

                        asset_coin = binan.get_spot_asset_by_symbol(self.trade_coin)
                        print(self.trade_coin + " 资产：")
                        print(asset_coin)

                        quantity = self.format_trade_quantity(float(asset_coin["free"]))

                        # 查询当前价格
                        cur_price = binan.get_ticker_price(self.symbol)

                        if quantity<=0:
                            msgInfo = msgInfo + "服务正常5--已无可售"
                            isDefaultToken = True
                        else:
                            isDefaultToken = False
                            # 卖出
                            res_order_sell = binan.sell_limit(self.symbol, quantity, cur_price)
                            # 清理本地订单信息
                            self.clearOrderInfo(self.orderInfoSavePath)
                            print("出售结果：")
                            print(res_order_sell)
                            order_result_str = self.printOrderJsonInfo(res_order_sell)
                            msgInfo = "卖出结果：\n" + str(order_result_str)

            else:
                if isOpenSellStrategy:
                    print("开启卖出策略---1")
                    msgInfo = self.sellStrategy(self.orderInfoSavePath)

                if msgInfo == "":
                    msgInfo = msgInfo + str(ts) + "\n"
                    print("暂不执行任何交易2")
                    msgInfo = msgInfo + "服务正常2"
                    isDefaultToken = True

            print("-----------------------------------------------\n")
        except Exception as ex:
            err_str = "出现如下异常：%s" % ex
            print(err_str)
            msgInfo = msgInfo + str(err_str) + "\n"

        finally:
            if "服务正常" in msgInfo:
                pass
            else:
                msg.dingding_warn(msgInfo, isDefaultToken)
