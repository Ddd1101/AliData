import utils.ali_api as api
import global_params
from common.settings import Settings
from utils import utils
from datetime import datetime, date, timedelta
from utils.cloth_worksheet import ClothWorksheet


class ClothTradeManager:
    def __init__(self):
        self.price_worksheet = ClothWorksheet(global_params.price_path, global_params.ShopType.ALI_CHILD_CLOTH)

    def start(self, create_start_time, create_end_time, shop_names: list, order_status: list, filter_tags: list):
        # 开始时间
        self.create_start_time = api.formate_date(create_start_time)
        # 结束时间
        self.create_end_time = api.formate_date(create_end_time)
        # 订单类型
        self.order_status = order_status
        # 过滤色标
        self.filter_tags = filter_tags
        # 店铺名字
        self.shop_names = shop_names

        self.mode = ""

        self.settings = Settings(shopNames=self.shop_names, mode=self.mode, fileter=filter_tags,
                                 createStartTime=create_start_time,
                                 createEndTime=create_end_time, orderStatus=self.order_status, isPrintOwn=True,
                                 limitDeliveredTime=[], isPrintUnitPrice="")

        self.get_order_list()

    def get_order_list(self):
        print(
            "start OrderList shopname" + self.settings.shopName + " mode:" + str(self.settings.mode), "debug"
        )

        order_list_origin = []
        order_for_process = []

        # 1. 遍历状态
        for order_status in self.settings.orderStatus:
            req_data = {
                "createStartTime": self.settings.createStartTime.strip(),
                "createEndTime": self.settings.createEndTime.strip(),
                "orderStatus": order_status.strip(),  # 只获取已发出 或者 已签收  todo：或者已完成未到账 或者已完成
                "needMemoInfo": "true",
            }
            # 2. 遍历店铺
            for shop_name in self.shop_names:
                # 2.1 获取总页数
                res = api.GetTradeData(req_data, shop_name)
                page_num = utils.CalPageNum(res["totalRecord"])

                # 
                for pageId in range(page_num):
                    # 2.2.1 遍历订单
                    for order in res["result"]:
                        # 过滤掉刷单
                        if ("sellerRemarkIcon" in order["baseInfo"]) and (
                                order["baseInfo"]["sellerRemarkIcon"] == "2"
                                or order["baseInfo"]["sellerRemarkIcon"] == "3"
                        ):
                            continue
                        # todo: 做一个单独的过滤方法 过滤红 或者 黄标签
                        order_list_origin += res["result"]



                # 收集原始订单结束
    # 根据标签过滤订单
    def filter_list_by_tags(self):
        pass

    # 根据发货时间过滤订单
    def filter_list_by_deliver_time(self):
        pass
    def OrderList(
            self,
            shopName,
            mode,
            filter,
            createStartTime,
            createEndTime,
            orderStatus,
            isPrintOwn,
            limitDeliveredTime,
            isPrintUnitPrice,
    ):
        print(
            "start OrderList shopname" + shopName + " mode:" + str(mode), "debug"
        )
        if orderStatus == 0:
            self.GetOrderBill(
                createStartTime,
                createEndTime,
                "waitbuyerreceive",
                shopName,
                isPrintOwn,
                mode,
                filter,
                limitDeliveredTime,
                isPrintUnitPrice
            )
        elif orderStatus == 1:
            self.GetOrderBill(
                createStartTime,
                createEndTime,
                "waitsellersend,waitbuyerreceive",
                shopName,
                isPrintOwn,
                mode,
                filter,
                limitDeliveredTime,
                isPrintUnitPrice,
            )
        elif orderStatus == 2:
            self.GetOrderBill(
                createStartTime,
                createEndTime,
                "waitsellersend",
                shopName,
                isPrintOwn,
                mode,
                filter,
                limitDeliveredTime,
                isPrintUnitPrice
            )
        elif orderStatus == 3:
            self.GetOrderBill(
                createStartTime,
                createEndTime,
                "waitbuyerpay",
                shopName,
                isPrintOwn,
                mode,
                filter,
                limitDeliveredTime,
                isPrintUnitPrice
            )
        elif orderStatus == 4:
            self.GetOrderHistory(
                createStartTime,
                createEndTime,
                "waitbuyerreceive,success",
                shopName,
                isPrintOwn,
                mode,
                filter,
                limitDeliveredTime,
                isPrintUnitPrice
            )

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

    # 获取订单号列表
    # 筛除刷单
    def GetOrderBill2(
            createStartTime,
            createEndTime,
            orderstatusStr,
            shopName,
            mode=0,
            limitDeliveredTime={},
    ):
        orderList = []

        orderstatusList = orderstatusStr.split(",")

        for orderstatus in orderstatusList:
            data = {
                "createStartTime": createStartTime,
                "createEndTime": createEndTime,
                "orderStatus": orderstatus,
                "needMemoInfo": "true",
            }
            response = api.GetTradeData(data, shopName)
            if orderstatus == "waitsellersend":
                orderstatusStr = "待发货"
            if orderstatus == "waitbuyerreceive":
                orderstatusStr = "已发货"
            # self.Logout('# ' + orderstatusStr + ' : ' + str(response['totalRecord']) + '条记录')
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

                if orderstatus == "waitsellersend" or orderstatus == "waitbuyerreceive":
                    for order in response["result"]:
                        if ("sellerRemarkIcon" in ["baseInfo"]) and (
                                order["baseInfo"]["sellerRemarkIcon"] == "2"
                                or order["baseInfo"]["sellerRemarkIcon"] == "3"
                        ):
                            continue
                        elif mode != 0 and "sellerRemarkIcon" not in order["baseInfo"]:
                            if mode == 1:
                                order["baseInfo"]["sellerRemarkIcon"] = "1"
                            elif mode == 4:
                                order["baseInfo"]["sellerRemarkIcon"] = "4"

                orderList += response["result"]

        return orderList
