import hmac
import global_params
import time
import requests


def CalculateSignature(urlPath, data, shopName):
    # 构造签名因子：urlPath

    # 构造签名因子：拼装参数
    params = list()
    for key in data.keys():
        params.append(key + str(data[key]))
    params.sort()
    sortedParams = params
    assembedParams = str()
    for param in sortedParams:
        assembedParams = assembedParams + param

    # 合并签名因子
    mergedParams = urlPath + assembedParams
    mergedParams = bytes(mergedParams, "utf8")

    # 执行hmac_sha1算法 && 转为16进制
    hex_res1 = hmac.new(global_params.AppSecret[shopName], mergedParams, digestmod="sha1").hexdigest()

    # 转为全大写字符
    hex_res1 = hex_res1.upper()

    return hex_res1


# 交易数据获取  默认1页
def GetTradeData(data, shopName):
    data["access_token"] = global_params.access_token[shopName]
    _aop_signature = CalculateSignature(
        global_params.request_type["trade"] + "alibaba.trade.getSellerOrderList/" + global_params.AppKey[shopName],
        data,
        shopName,
    )
    data["_aop_signature"] = _aop_signature
    url = (
            global_params.base_url
            + global_params.request_type["trade"]
            + "alibaba.trade.getSellerOrderList/"
            + global_params.AppKey[shopName]
    )
    try:
        time.sleep(0.2)
        res = requests.post(url, data=data)
    except Exception as e:
        print("post error ", e)

    return res.json()


# 已发货物流信息
def GetDeliveryData(data, shopName):
    data["access_token"] = global_params.access_token[shopName]
    _aop_signature = CalculateSignature(
        global_params.request_type["delivery"]
        + "alibaba.trade.getLogisticsInfos.sellerView/"
        + global_params.AppKey[shopName],
        data,
        shopName,
    )
    data["_aop_signature"] = _aop_signature

    url = (
            global_params.base_url
            + global_params.request_type["delivery"]
            + "alibaba.trade.getLogisticsInfos.sellerView/"
            + global_params.AppKey[shopName]
    )

    res = requests.post(url, data=data)

    return res.json()


# 已发货物流信息+单号信息
def GetDeliveryTraceData(data, shopName):
    data["access_token"] = global_params.access_token[shopName]
    tmp = CalculateSignature(
        "param2/1/com.alibaba.logistics/alibaba.trade.getLogisticsInfos.sellerView/"
        + global_params.AppKey[shopName],
        data,
        shopName,
    )
    _aop_signature = CalculateSignature(
        global_params.request_type["delivery"]
        + "alibaba.trade.getLogisticsTraceInfo.sellerView/"
        + global_params.AppKey[shopName],
        data,
        shopName,
    )
    data["_aop_signature"] = _aop_signature
    url = (
            global_params.base_url
            + global_params.request_type["delivery"]
            + "alibaba.trade.getLogisticsTraceInfo.sellerView/"
            + global_params.AppKey[shopName]
    )

    response = requests.post(url, data=data)

    return response.json()

def GetSingleTradeData(data, shopName):
    data["access_token"] = global_params.access_token[shopName]
    _aop_signature = CalculateSignature(
        global_params.request_type["trade"] + "alibaba.trade.get.sellerView/" + global_params.AppKey[shopName],
        data,
        shopName,
    )
    data["_aop_signature"] = _aop_signature
    url = (
            global_params.base_url
            + global_params.request_type["trade"]
            + "alibaba.trade.get.sellerView/"
            + global_params.AppKey[shopName]
    )
    res = requests.post(url, data=data)

    return res.json()
