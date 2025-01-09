#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：ShopERP 
@File    ：OrderManager.py
@Author  ：Ddd
@Date    ：2023/9/3 21:51 
'''
from AliData import utils


class ShopData:
    def __init__(self, shopName, appKey, appSecret, accessToken):
        self.shopName = shopName
        self.appKey = appKey
        self.appSecret = appSecret
        self.accessToken = accessToken


class OrderManager:
    def __init__(self, shopData):
        self.shopData = shopData
        self.shuaDanSheet = []

    def IsShuaDan(self, idOfStr):
        print(idOfStr)
        for t in range(1, self.shuaDanSheet.nrows):
            print(self.shuaDanSheet.cell(t, 2).value)
            if idOfStr == self.shuaDanSheet.cell(t, 2).value:
                return True
        return False

    def ProcessByOrderStatus(createStartTime, createEndTime, orderstatus, shopName):
        data = {'createStartTime': createStartTime, 'createEndTime': createEndTime, 'orderStatus': orderstatus,
                'needMemoInfo': 'true'}
        response = TransactionData.GetTradeData(data, shopName)
        # print(response)
        print('# ' + orderstatus + ' : ' + str(response['totalRecord']) + '条记录')
        pageNum = utils.CalPageNum(response['totalRecord'])

        for pageId in range(pageNum):
            data = {'page': str(pageId + 1), 'createStartTime': createStartTime, 'createEndTime': createEndTime,
                    'orderStatus': orderstatus, 'needMemoInfo': 'true'}
            response = TransactionData.GetTradeData(data, shopName)

            orderList = response['result']
            value = list()
            valueShuaDan = list()

            for order in orderList:
                _item = list()
                orderDtae = datetime.strptime(order['baseInfo']['payTime'][0:8], '%Y%m%d').strftime('%Y/%m/%d')

                # 刷单分流记录
                if ('sellerRemarkIcon' in order['baseInfo']) and (
                        order['baseInfo']['sellerRemarkIcon'] == '2' or order['baseInfo']['sellerRemarkIcon'] == '3'):
                    _item.append(orderDate)
                    _item.append(order['baseInfo']['buyerLoginId'])
                    _item.append(order['baseInfo']['idOfStr'])
                    _item.append(order['baseInfo']['sumProductPayment'])
                    _item.append('')
                    if order['baseInfo']['sellerRemarkIcon'] == '2':
                        _item.append('侯国金')
                        _item.append('侯国金')
                    else:
                        _item.append('侯国鑫')
                        _item.append('侯国鑫')
                    valueShuaDan.append(_item)
                else:
                    _item.append(orderDate)
                    _item.append(order['baseInfo']['idOfStr'])
                    _productItems = ''
                    pay = 0
                    cost = 0
                    isCostCount = True
                    productItemNum = len(order['productItems'])
                    for productItem in order['productItems']:
                        productItemNum = productItemNum - 1
                        pay = pay + productItem['itemAmount']

                        # 货号
                        cargoNumber = ''
                        cargoNumberTag = ''
                        if 'cargoNumber' in productItem:
                            cargoNumberTag = 'cargoNumber'
                            cargoNumber = productItem[cargoNumberTag]
                        elif 'productCargoNumber' in productItem:
                            cargoNumberTag = 'productCargoNumber'
                            cargoNumber = productItem[cargoNumberTag]

                        if cargoNumber != '':
                            _productItems = _productItems + cargoNumber + ' ' + utils.NumFormate(
                                productItem['skuInfos'][1][
                                    'value']) + " * " + str(productItem['quantity']) + '件'
                            if utils.GetCost(cargoNumber, productItem['skuInfos'][1]['value']) == -1:
                                cost = -1
                                isCostCount = False
                            if isCostCount:
                                cost += (utils.GetCost(cargoNumber, productItem['skuInfos'][1]['value']) * productItem[
                                    'quantity'])
                        if productItemNum != 0:
                            _productItems = _productItems + '\n'
                    _item.append(_productItems)
                    _item.append(pay)
                    _item.append(order['baseInfo']['shippingFee'])
                    _item.append(cost)
                    _item.append(3)
                    value.append(_item)
            print('# ' + str(len(orderList)) + '条记录')
            if isWriteToExcel:
                # print(value)
                # print('tt')
                excelp.write_excel_xlsx_append(filePath, value, 'Sheet1')
                excelp.write_excel_xlsx_append(filePath, valueShuaDan, 'Sheet2')
            value.clear()

