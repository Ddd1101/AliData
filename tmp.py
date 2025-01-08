def GetOrderBill(
        self,
        createStartTime,
        createEndTime,
        order_status: list,
        shop_names: list,
        isPrintOwn,
        mode=0,
        filter=0,
        limitDeliveredTime={},
        isPrintUnitPrice=False,
):
    print("start GetOrderBill", "debug")

    shopNameList = shop_names

    orderListRaw = []

    orderstatusList = order_status

    orderList = []

    for shopName in shopNameList:
        orderListRaw.clear()
        for orderstatus in orderstatusList:
            data = {
                "createStartTime": createStartTime.strip(),
                "createEndTime": createEndTime.strip(),
                "orderStatus": orderstatus.strip(),
                "needMemoInfo": "true",
            }

            response = api.GetTradeData(data, shopName)
            if orderstatus == "waitsellersend":
                orderstatusStr = "待发货"
            if orderstatus == "waitbuyerreceive":
                orderstatusStr = "已发货"

            pageNum = utils.CalPageNum(response["totalRecord"])

            # 规格化数据
            for pageId in range(pageNum):
                data = {
                    "page": str(pageId + 1),
                    "createStartTime": createStartTime,
                    "createEndTime": createEndTime,
                    "orderStatus": orderstatus,
                    "needMemoInfo": "true",
                }
                response = api.GetTradeData(data, shopName)
                if (
                        orderstatus == "waitsellersend"
                        or orderstatus == "waitbuyerreceive"
                ):
                    for order in response["result"]:
                        if ("sellerRemarkIcon" in order["baseInfo"]) and (
                                order["baseInfo"]["sellerRemarkIcon"] == "2"
                                or order["baseInfo"]["sellerRemarkIcon"] == "3"
                        ):
                            continue

                        # 过滤红/黄标签
                        if "sellerRemarkIcon" in order["baseInfo"]:
                            # 过滤红标签
                            if (
                                    filter == 1
                                    and order["baseInfo"]["sellerRemarkIcon"] == "1"
                            ):
                                print("过滤红标签")
                                continue
                            # 过滤黄标签
                            if (
                                    filter == 2
                                    and order["baseInfo"]["sellerRemarkIcon"] == "4"
                            ):
                                print("过滤黄标签")
                                continue

                orderListRaw += response["result"]

            if len(limitDeliveredTime) >= 2:
                for order in orderListRaw:
                    if (
                            "allDeliveredTime" in order["baseInfo"]
                            and len(limitDeliveredTime) > 0
                    ):  # 根据发货时间判断是否要输出
                        allDeliveredTime = int(
                            order["baseInfo"]["allDeliveredTime"][:-8]
                        )
                        if (
                                allDeliveredTime
                                < limitDeliveredTime["deleveredStartTime"]
                                or allDeliveredTime
                                > limitDeliveredTime["deleveredEndTime"]
                        ):
                            continue
                        else:
                            orderList.append(order)
            else:
                for order in orderListRaw:
                    # 过滤黄标签
                    if "sellerRemarkIcon" in order["baseInfo"]:
                        if (
                                filter == 2
                                and order["baseInfo"]["sellerRemarkIcon"] == "4"
                        ):
                            print("过滤黄标签")
                            continue
                        else:
                            orderList.append(order)
                    else:
                        orderList.append(order)

            orderListRaw.clear()

    self.Logout2("# " + orderstatusStr + " : " + str(len(orderList)) + "条记录")
    global global_OrderNum
    global_OrderNum = len(orderList)

    # todo: 童裝/饰品方法不同
    self.GetBeihuoJson(
        orderList, isPrintOwn, mode, limitDeliveredTime, isPrintUnitPrice
    )