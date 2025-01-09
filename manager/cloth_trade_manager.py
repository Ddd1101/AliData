import utils.ali_api as api
import global_params
from common.settings import Settings
from utils import utils
from datetime import datetime, date, timedelta
from utils.cloth_worksheet import ClothWorksheet


class ClothTradeManager:
    def __init__(self):
        self.shop_names = None
        self.hasGetOrders = None
        self.origin_orders = None
        self.settings = None
        self.start_time = None
        self.end_time = None
        self.need_process_order_count = None
        self.price_worksheet = ClothWorksheet(global_params.price_path, global_params.ShopType.ALI_CHILD_CLOTH)

    def set_params(self, start_time, end_time, shop_names: list, order_status: list, filter_tags: list):
        # 开始时间
        self.start_time = api.formate_date(start_time)
        # 结束时间
        self.end_time = api.formate_date(end_time)

        self.settings = Settings(shop_names=shop_names, start_time=self.start_time, end_time=self.end_time,
                                 order_status=order_status, limit_delivered_ime=[], filter_tags=filter_tags)

        self.origin_orders: list = []
        self.hasGetOrders = False

    def clean_orders(self):
        print("start clean_orders")
        orders_filter_by_tags = self.filter_order_by_tags(self.origin_orders)
        orders_without_refunds = self.filter_refunds_products(orders_filter_by_tags)

    def check_orders(self):
        if not self.hasGetOrders or len(self.origin_orders) <= 0:
            self.get_origin_order_list()

    # 获取销售额
    def get_sales_amount(self):
        self.check_orders()
        # orders_filter_by_tags = self.filter_order_by_tags(self.origin_orders)
        print(self.origin_orders)

    # 获取利润
    def get_profit(self):
        self.check_orders()

    def get_fake_order(self):
        self.check_orders()

    # 收集原始订单
    def get_origin_order_list(self):
        print("start get_origin_order_list")

        # 1. 遍历状态
        for order_status in self.settings.order_status:
            print(order_status)
            req_data = {
                "createStartTime": self.settings.start_time.strip(),
                "createEndTime": self.settings.end_time.strip(),
                "orderStatus": order_status,  # 只获取已发出 或者 已签收  todo：或者已完成未到账 或者已完成
                "needMemoInfo": "true",
            }
            # 2. 遍历店铺
            for shop_name in self.settings.shop_names:
                print("start get_origin_order_list-" + order_status + "-" + shop_name)
                # 2.1 获取总页数
                res = api.GetTradeData(req_data, shop_name)
                page_num = utils.CalPageNum(res["totalRecord"])

                # 2.2 按页获取订单项
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
                        self.origin_orders += res["result"]

        self.hasGetOrders = True
        print("end get_origin_order_list")

    # 根据发货时间过滤订单
    def filter_order_by_delivered_time(self, order_list):
        pass

    # 根据标签过滤订单
    def filter_order_by_tags(self, order_list):
        pass

    # 过滤退货产品item
    def filter_refunds_products(self, order_list):
        pass

    def get_refund_producets(self, order_list):
        pass

    def get_beihuo_json(self, order_list):
        pass

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
