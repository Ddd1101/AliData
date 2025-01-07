# -*- coding: utf-8 -*-

import hmac
import math
from skimage import io

import urllib

import time

AppKey = {"联球制衣厂": "3527689", "朝雄制衣厂": "1850682", "义乌睿得": "3527689"}
AppSecret = {
    "联球制衣厂": b"Zw5KiCjSnL",
    "朝雄制衣厂": b"63K2QGMuZf4",
    "义乌睿得": b"Zw5KiCjSnL",
}
access_token = {
    "联球制衣厂": "999d182a-3576-4aee-97c5-8eeebce5e085",
    "朝雄制衣厂": "4bcdd211-3b22-41ea-b0eb-8ef679e9b58f",
    "义乌睿得": "7f813331-15d6-40a8-97ac-00589efc8e81",
}

base_url = "https://gw.open.1688.com/openapi/"

import Common.ExcelProcess as excelp

worksheet = excelp.GetPriceGrid()


def CalculateSignature(urlPath, data, shopName):
    # 构造签名因子：urlPath

    # 构造签名因子：拼装参数
    params = list()
    for key in data.keys():
        params.append(key + data[key])
    params.sort()
    sortedParams = params
    assembedParams = str()
    for param in sortedParams:
        assembedParams = assembedParams + param

    # 合并签名因子
    mergedParams = urlPath + assembedParams
    mergedParams = bytes(mergedParams, "utf8")

    # 执行hmac_sha1算法 && 转为16进制
    hex_res1 = hmac.new(AppSecret[shopName], mergedParams, digestmod="sha1").hexdigest()

    # 转为全大写字符
    hex_res1 = hex_res1.upper()

    return hex_res1


def CalPageNum(totalRecord):
    return math.ceil(totalRecord / 20)


def CalDayNum(day):
    day = int(day) + 1


def SavePicByUrl(url):
    io.imsave("./tmp.jpg", io.imread(url))


def GetCost(cargoNumber, skuInfosValue, colNum=0):
    rowIndex = -1
    for t in range(1, worksheet.nrows):
        if str(worksheet.cell(t, colNum).value) != "":
            tmpList = str(worksheet.cell(t, colNum).value).split("\n")
            for each in tmpList:
                if str(cargoNumber).strip() == str(each).strip():
                    rowIndex = t
                    break
            if rowIndex != -1:
                break

    # 货号用int再对比下
    if rowIndex == -1:
        for t in range(1, worksheet.nrows):
            if str(worksheet.cell(t, colNum).value) != "":
                tmpList = str(worksheet.cell(t, colNum).value).split("\n")
                for each in tmpList:
                    if str(cargoNumber) == str(each):
                        rowIndex = t
                        break
                if rowIndex != -1:
                    break

    if rowIndex == -1:
        print(cargoNumber + " 1==========" + worksheet.cell(t, colNum).value)
        return -1
    colIndex = CalPriceLocation(skuInfosValue)
    if colIndex != None:
        _price = worksheet.cell(rowIndex, int(colIndex)).value
    else:
        _price = ""
    if _price == "":
        print(cargoNumber + " 2==========" + worksheet.cell(t, colNum).value)
        _price = -1
    return float(_price)


def PDDid2Commonid(cargoNumber, colNum=0):
    rowIndex = -1
    for t in range(1, worksheet.nrows):
        if str(cargoNumber) == str(worksheet.cell(t, colNum).value):
            rowIndex = t
            break
    if rowIndex == -1:
        print(cargoNumber + " 3==========" + worksheet.cell(t, colNum).value)
        return cargoNumber
    commonId = worksheet.cell(rowIndex, 0).value
    if commonId == "":
        print(cargoNumber + " 4==========" + worksheet.cell(t, colNum).value)
        commonId = cargoNumber
    return commonId


en_code = ["s", "S", "m", "M", "l", "L", "x", "X"]


# 中文混合的尺码转换
def convert_to_numeric_size(size_str):
    """
    字符串数字尺码转纯int 100cm -> 100
    :param size_str:
    :return:
    """
    numeric_size = ""
    for char in size_str:
        if char.isdigit():
            numeric_size += char
        else:
            break

    if numeric_size:
        return int(numeric_size)
    else:
        return None


def convert_to_numeric_size_f(size_str):
    """
    字符串数字尺码转纯int 100cm -> 100
    :param size_str:
    :return:
    """
    numeric_size = ""
    for char in size_str:
        if char.isdigit():
            numeric_size += char
        else:
            break

    if numeric_size:
        return int(numeric_size)
    else:
        return None


def CalPriceLocationback(_size):
    if _size[0] in en_code:
        return CalPriceLocationENCode(_size)
    theta = (CalSize(_size) - 80) / 5
    _col = 5 + theta
    print(_col)

    tt = -1

    for i in range(worksheet.ncols):
        if (
            worksheet.cell(0, i).ctype == 2
            and convert_to_numeric_size(_size) == worksheet.cell(0, i).value
        ):  # 数字码
            print(i)
            tt = i
            break

    return _col


def CalPriceLocation(_size):
    """
    根据价格表标题行获得价格列

    ctype: 0=empty, 1-text, 2-number
    :param _size:
    :return:
    """
    if _size[0] in en_code:
        return CalPriceLocationENCode(_size)

    # 获取第一行的值
    first_row_values = worksheet.row_values(0)

    # 搜索列名并返回其索引
    try:
        col_index = first_row_values.index(convert_to_numeric_size_f(_size))
    except ValueError:
        pass

    return col_index

    # _col = -1
    # for i in range(worksheet.ncols):
    #     if worksheet.cell(0, i).ctype == 2 and \
    #             convert_to_numeric_size(_size) == worksheet.cell(0, i).value:  # 数字码
    #         _col = i
    #         print(i)
    #         break
    #
    # if _col != -1:
    #     return _col

    print("没有该尺码")
    return -1


def CalPriceLocationENCode(_size):
    if _size == "":
        return -1

    if _size[0] == "S" or _size[0] == "s":
        return 24

    if _size[0] == "M" or _size[0] == "m":
        return 25

    if _size[0] == "L" or _size[0] == "l":
        return 26

    if _size[0] == "x" or _size[0] == "X":
        if _size[1] == "L" or _size[1] == "l":
            return 27
        elif _size[1] == "x" or _size[1] == "X":
            if _size[2] == "L" or _size[2] == "l":
                return 28
            elif _size[2] == "x" or _size[2] == "X":
                return 29

    return -1


def CalSize(sizeDescription):
    _size = 0
    for i in range(len(sizeDescription)):
        if sizeDescription[i] >= "0" and sizeDescription[i] <= "9":
            _size = _size * 10 + int(sizeDescription[i])
        else:
            break
    return _size


def CalSizeZE(sizeDescription):
    if sizeDescription[0] in en_code:
        colIndex = CalPriceLocationENCode(sizeDescription)
        if colIndex == 24:
            return "S"
        elif colIndex == 25:
            return "M"
        elif colIndex == 26:
            return "L"
        elif colIndex == 27:
            return "XL"
        elif colIndex == 28:
            return "XXL"
        elif colIndex == 29:
            return "XXL"

    _size = 0
    for i in range(len(sizeDescription)):
        if sizeDescription[i] >= "0" and sizeDescription[i] <= "9":
            _size = _size * 10 + int(sizeDescription[i])
        else:
            break
    return _size


def GetAdressAndShopName(cargoNumber):
    rowIndex = -1
    for t in range(1, worksheet.nrows):
        if cargoNumber == worksheet.cell(t, 0).value:
            rowIndex = t
            break
    if rowIndex == -1:
        return ["", "", ""]
    productName = worksheet.cell(rowIndex, 1).value
    adress = worksheet.cell(rowIndex, 2).value
    shopName = worksheet.cell(rowIndex, 3).value
    return [productName, adress, shopName]


# if __name__ == '__main__':
#     data = {access_token: 'ed0be2fc-75d0-4606-a3cb-bc129e4f312f', 'orderStatus': 'success'}
#     urlPath = 'param2/1/com.alibaba.trade/' + 'alibaba.trade.getSellerOrderList/' + AppKey
#     data = CalculateSignature(urlPath,data)
#     print(data)


def NumFormate4Print(numStr):
    res = ""
    if numStr[0] in en_code:
        for item in numStr:
            if item in en_code:
                res += item
            else:
                break
        fomateSpaceNum = 5 - len(res)
        for k in range(fomateSpaceNum):
            res = " " + res

    else:
        for item in numStr:
            if item >= "0" and item <= "9":
                res += item
            else:
                if res[0] == "9":
                    res += " "
                break
        res += "cm"
    return res


def NumFormate(numStr):
    res = ""
    if numStr[0] in en_code:
        for item in numStr:
            if item in en_code:
                res += item
                break

    else:
        for item in numStr:
            if item >= "0" and item <= "9":
                res += item
            else:
                if res[0] == "9":
                    res += " "
                break
        res += "cm"
    return res


def RequestPic(url):
    flag = True
    while flag:
        try:
            print(url)
            picData = urllib.request.urlopen(url).read()
            flag = False
        except:
            print("# 获取图片异常 重试")
            time.sleep(3)

    return picData
