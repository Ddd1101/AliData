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
        # 其他参数设置
        self.settings = Settings(shop_names=shop_names, start_time=self.start_time, end_time=self.end_time,
                                 order_status=order_status, limit_delivered_ime=[], filter_tags=filter_tags)

        self.origin_orders = {}
        for shop_name in shop_names:
            self.origin_orders[shop_name] = []
        print(self.origin_orders)
        self.shuadan_orders = []
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
        # 过滤标签

        amount = {}
        for shop_name in self.settings.shop_names:
            amount[shop_name] = {"sumProductPayment": 0, "refundPayment": 0}
        for shop_name in self.origin_orders:
            print(len(self.origin_orders[shop_name]))
            for order in self.origin_orders[shop_name]:
                amount[shop_name]["sumProductPayment"] += order["baseInfo"]["sumProductPayment"]
                amount[shop_name]["refundPayment"] += order["baseInfo"]["refundPayment"]

            print(amount)

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
                    req_data = {
                        "page": str(pageId + 1),
                        "createStartTime": self.settings.start_time.strip(),
                        "createEndTime": self.settings.end_time.strip(),
                        "orderStatus": order_status,  # 只获取已发出 或者 已签收  todo：或者已完成未到账 或者已完成
                        "needMemoInfo": "true",
                    }
                    res = api.GetTradeData(req_data, shop_name)
                    # print(res)
                    # 2.2.1 遍历订单
                    print(len(res["result"]))
                    for order in res["result"]:
                        # 过滤掉刷单
                        if ("sellerRemarkIcon" in order["baseInfo"]) and (
                                order["baseInfo"]["sellerRemarkIcon"] == global_params.OrderTags.BLUE.value
                                or order["baseInfo"]["sellerRemarkIcon"] == global_params.OrderTags.GREEN.value
                        ):
                            self.shuadan_orders += order
                            continue
                        # todo: 做一个单独的过滤方法 过滤红 或者 黄标签
                        self.origin_orders[shop_name].append(order)

        self.hasGetOrders = True
        print("end get_origin_order_list")

    # 根据发货时间过滤订单
    def filter_order_by_delivered_time(self, order_list):
        pass

    # 根据标签过滤订单
    def filter_order_by_tags(self):
        print("start filter_order_by_tags")
        for tag in self.settings.filter_tags:
            print(tag)

    # 过滤退货产品item
    def filter_refunds_products(self, order_list):
        pass

    def get_refund_producets(self, order_list):
        pass

    def get_beihuo_json(self, order_list):
        pass

    def get_deliver_info(self):
        pass