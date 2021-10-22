# -*- coding: utf-8 -*
import requests, time, hmac, hashlib
from app.authorization import recv_window,api_secret,api_key

try:
    from urllib import urlencode
# python3
except ImportError:
    from urllib.parse import urlencode

class BinanceAPI(object):
    BASE_URL = "https://www.binance.com/api/v1"
    FUTURE_URL = "https://fapi.binance.com"
    BASE_URL_V3 = "https://api.binance.com/api/v3"
    PUBLIC_URL = "https://www.binance.com/exchange/public/product"


    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def ping(self):
        path = "%s/ping" % self.BASE_URL_V3
        return requests.get(path, timeout=180, verify=True).json()

    # 服务器时间
    def serverTime(self):
        path = "%s/time" % self.BASE_URL_V3
        return requests.get(path, timeout=180, verify=True).json()

    # 获取交易规则和交易对信息, GET /api/v3/exchangeInfo
    def exchangeInfo(self):
        path = "%s/exchangeInfo" % self.BASE_URL_V3
        return requests.get(path, timeout=180, verify=True).json()

    # 获取最新价格
    def get_ticker_price(self,market):
        path = "%s/ticker/price" % self.BASE_URL_V3
        params = {"symbol":market}
        res =  self._get_no_sign(path,params)
        print("get_ticker_price=")
        print(res)
        time.sleep(2)
        return float(res['price'])

    # 24hr 价格变动情况
    def get_ticker_24hour(self,market):
        path = "%s/ticker/24hr" % self.BASE_URL_V3
        params = {"symbol":market}
        res =  self._get_no_sign(path,params)
        return res

    #获取K线 https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=15m&startTime=1619761128000&endTime=1619764848000
    def get_klines(self, market, interval, limit=0, startTime=None, endTime=None):
        path = "%s/klines" % self.BASE_URL_V3
        params = None
        if startTime is None:
            params = {"symbol": market, "interval":interval}    
        else:    
            params = {"symbol": market, "interval":interval, "startTime":startTime, "endTime":endTime}

        if limit is None or limit <=0 or limit >1000:
            limit = 500

        params['limit'] = limit

        return self._get_no_sign(path, params)


    # 现货，账户信息，GET /api/v3/account
    def get_Spot_UserData_account(self):
        stamp_now = int(round(time.time() * 1000))
        path = "%s/account" % self.BASE_URL_V3
        params = {"timestamp": stamp_now,"recvWindow":recv_window}
        res = self._get_with_sign(path, params)
        return res

    def get_spot_asset_by_symbol(self, symbol):
        ud_account = self.get_Spot_UserData_account()

        if ud_account is not None and "balances" in ud_account.keys():
            balances = ud_account["balances"]
            if balances is not None and type(balances).__name__=='list':
                for balance in balances:
                    if str(balance["asset"])==symbol:
                        return balance



    # 查询每日资产快照，/sapi/v1/accountSnapshot
    def get_UserData_accountSnapshot(self):
        stamp_now = int(round(time.time() * 1000))
        path = "https://www.binance.com/sapi/v1/accountSnapshot"
        params = {"type":"SPOT","timestamp":stamp_now,"limit":5}

        # res = self._post(path, params)
        res = self._get_with_sign(path, params).json()
        return res

    def buy_limit(self, market, quantity, rate):
        print("购买 "+ market +"\t"+'%f 个, ' % quantity + "价格：%f"%rate)
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "BUY", rate)
        return self._post(path, params)

    # 测试专用，买入
    def buy_limit_test(self, market, quantity, rate):
        tStamp = int(1000 * time.time())
        dict = {'symbol': market, 'orderId': 924538226, 'orderListId': -1, 'clientOrderId': 'wtswxN4L8O6hZiWNiOxuaN',\
                'transactTime': tStamp, 'price': str(round(rate,8)), 'origQty': str(round(quantity,8)), 'executedQty': str(round(quantity,8)),\
                'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'fills': []}
        return dict

    # 测试专用，卖出
    def sell_limit_test(self, market, quantity, rate):
        tStamp = int(1000 * time.time())
        dict = {'symbol': market, 'orderId': 933997128, 'orderListId': -1, 'clientOrderId': 'uepwnRSgfVioZlBhXqTr03', \
                'transactTime': tStamp, 'price': str(round(rate,8)), 'origQty': str(round(quantity,8)), 'executedQty': '0.00000000', \
                'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'fills': []}
        return dict



    def sell_limit(self, market, quantity, rate):
        print("出售 "+ market +"\t"+'%f 个, ' % quantity + "价格：%f"%rate)

        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "SELL", rate)
        return self._post(path, params)

    ### ----私有函数---- ###
    def _order(self, market, quantity, side, price=None):
        '''
        :param market:币种类型。如：BTCUSDT、ETHUSDT
        :param quantity: 购买量
        :param side: 订单方向，买还是卖
        :param price: 价格
        :return:
        '''
        params = {}

        if price is not None:
            params["type"] = "LIMIT"
            params["price"] = self._format(price)
            params["timeInForce"] = "GTC"
        else:
            params["type"] = "MARKET"

        params["symbol"] = market
        params["side"] = side
        params["quantity"] = '%.8f' % quantity

        return params

    def _get_no_sign(self, path, params={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        return requests.get(url, timeout=180, verify=True).json()

    def _get_no_sign_header(self, path, params={},header={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        return requests.get(url, headers=header,timeout=180, verify=True).json()

    def _get_with_sign(self, path, params={}):
        tmp_signature = self._signature(params)
        params.update({"signature": tmp_signature})
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        header = {"Content-Type":"application/json","X-MBX-APIKEY": self.key}

        return requests.get(url,headers=header, timeout=180, verify=True).json()

    # 生成 signature
    def _signature(self, params={}):
        data = params.copy()
        # ts = int(1000 * time.time())
        # data.update({"timestamp": ts})
        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        return signature

    def _sign(self, params={}):
        data = params.copy()

        ts = int(1000 * time.time())
        data.update({"timestamp": ts})
        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        data.update({"signature": signature})
        return data

    def _post(self, path, params={}):
        params.update({"recvWindow": recv_window})
        query = urlencode(self._sign(params))
        url = "%s" % (path)
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(url, headers=header, data=query, \
            timeout=180, verify=True).json()

    def _format(self, price):
        return "{:.8f}".format(price)


    # 合约
    def market_future_order(self, side, symbol, quantity,positionSide):

        ''' 合约市价单
            :param side: 做多or做空 BUY SELL
            :param symbol:币种类型。如：BTCUSDT、ETHUSDT
            :param quantity: 购买量
            :param positionSide: 双向持仓 BUY-LONG 开多 SELL-SHORT 开空
            :param price: 开仓价格
        '''
        path = "%s/fapi/v1/order" % self.FUTURE_URL
        params = self._order(symbol, quantity, side, positionSide)
        return self._post(path, params)



if __name__ == "__main__":
    instance = BinanceAPI(api_key,api_secret)
    # print(instance.buy_limit("EOSUSDT",5,2))
    # print(instance.get_ticker_price("WINGUSDT"))
    print(instance.get_ticker_24hour("WINGUSDT"))