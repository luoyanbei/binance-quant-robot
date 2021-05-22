# binance-quant-robot
数字货币，币安Binance,BTC ETH DOGE SHIB 量化交易系统 火币


## 简介
这是一个数字货币量化交易系统，使用的Binance币安的交易API.

本系统采用双均线交易策略，两条均线出现金叉则买入，出现死叉则卖出。

如果你还没有币安账号：[注册页面](https://accounts.binancezh.io/zh-CN/register?ref=FJO3SX0X)（通过链接注册，享受交易返现优惠政策）


## 为什么选择币安交易所
交易的手续费看起来很少，但是随着交易次数逐步增多，手续费也是一笔不小的开支。
所以我选择了币安，手续费低的大平台交易所
> 火币手续费 Maker 0.2% Taker 0.2%

> 币安手续费 Maker 0.1% Taker 0.1% （加上BNB家持手续费低至0.075%）


如果你还没有币安账号：[注册页面](https://accounts.binancezh.io/zh-CN/register?ref=FJO3SX0X)（通过链接注册，享受交易返现优惠政策）


## 运行环境
python3

由于交易所的api在大陆无法访问，需要科学上网(若无，可用[muncloud](https://www.muncloud.dog/aff.php?aff=2302))


## 快速使用

1、获取币安API的 api_key 和 api_secret

申请api_key地址:

[币安API管理页面](https://www.binance.com/cn/usercenter/settings/api-management)


2、注册钉钉自定义机器人Webhook，用于推送交易信息到指定的钉钉群

[钉钉自定义机器人注册方法](https://m.dingtalk.com/qidian/help-detail-20781541)


3、修改app目录下的authorization文件

```
api_key='你的币安key'
api_secret='你的币安secret'
dingding_token = '申请钉钉群助手的token'   # 强烈建议您使用
```


4、交易策略配置信息 strategyConfig.py
设置你的配置信息：

```
# 均线, ma_x 要大于 ma_y
ma_x = 5
ma_y = 60

# 币安
binance_market = "SPOT"#现货市场
binance_coinBase = "USDT"#使用USDT作为基础币种，用于购买其他货币；
binance_tradeCoin = "DOGE"#交易目标是 DOGE 币，
kLine_type = '5m' # 15分钟k线类型，你可以设置为5分钟K线：5m;1小时为：1h;1天为：1d
```


5、运行程序(记得先开科学上网)
```
python robot-run.py
```



## 部署


