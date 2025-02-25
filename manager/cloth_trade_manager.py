import json
from pprint import pprint

import utils.ali_api as api
import global_params
from common.order_amount import OrderAmount
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
        self.price_worksheet = ClothWorksheet(
            global_params.price_path, global_params.ShopType.ALI_CHILD_CLOTH
        )

    def set_params(
        self,
        start_time,
        end_time,
        shop_names: list,
        order_status: list,
        filter_tags: list,
        pay_start_time=None,
        pay_end_time=None,
    ):
        # 其他参数设置
        self.settings = Settings(
            shop_names=shop_names,
            start_time=start_time,
            end_time=end_time,
            order_status=order_status,
            limit_delivered_ime=[],
            filter_tags=filter_tags,
        )

        self.origin_orders = {}
        for shop_name in shop_names:
            self.origin_orders[shop_name] = []
        # print(self.origin_orders)
        self.shuadan_orders = []
        self.hasGetOrders = False

    def clean_orders(self):
        print("start clean_orders")
        orders_filter_by_tags = self.filter_order_by_tags(self.origin_orders)
        orders_without_refunds = self.filter_refunds_products(orders_filter_by_tags)

    def check_orders(self):
        pass

    # 获取销售额
    def get_sales_amount(self):
        self.get_all_origin_order_list()
        # 过滤标签
        amount = {}
        order_count = 0
        for shop_name in self.settings.shop_names:
            amount[shop_name] = OrderAmount()
        for shop_name in self.origin_orders:
            print("订单数： " + str(len(self.origin_orders[shop_name])))
            flag = False
            for order in self.origin_orders[shop_name]:
                single_order_amount = self.get_single_order_amount(order)
                if single_order_amount != None:
                    amount[
                        shop_name
                    ].sum_product_payment += single_order_amount.sum_product_payment
                    amount[shop_name].shipping_fee += single_order_amount.shipping_fee
                    amount[shop_name].total_amount += single_order_amount.total_amount
                    amount[shop_name].refund += single_order_amount.refund
                    amount[
                        shop_name
                    ].refund_shipping_fee += single_order_amount.refund_shipping_fee
                    amount[shop_name].order_count += 1

                    # if single_order_amount.total_amount > 500:
                    #     print(single_order_amount.total_amount)
                    #     print(order)

            print(
                amount[shop_name].total_amount,
                amount[shop_name].refund,
                amount[shop_name].total_amount - amount[shop_name].refund,
                amount[shop_name].order_count,
            )

        return amount

    #
    def get_single_order_amount(self, order):
        order_status = order["baseInfo"]["status"]

        is_available_order = False

        # 判断付款时间
        if "payTime" in order["baseInfo"]:
            pay_time = api.de_formate_time(order["baseInfo"]["payTime"])
            if not (
                self.settings.order_start_time <= pay_time < self.settings.end_time
            ):
                return None

        if global_params.OrderStatus.ALL.value in self.settings.order_status:
            is_available_order = True

        if order_status in self.settings.order_status:
            is_available_order = True

        # 订单不统计直接返回空值
        if not is_available_order:
            return None

        if order_status == global_params.OrderStatus.TRADE_SUCCESS.value:
            return self.get_single_order_amount_success(order)
        elif order_status == global_params.OrderStatus.TRADE_CANCEL.value:
            return self.get_single_order_amount_cancel(order)
        elif order_status == global_params.OrderStatus.WAIT_SELLER_SEND.value:
            return self.get_single_order_amount_waitsellersend(order)
        elif order_status == global_params.OrderStatus.WAIT_BUYER_RECEIVE.value:
            return self.get_single_order_amount_waitbuyerreceive(order)
        elif order_status == global_params.OrderStatus.CONFIRM_GOODS_BUT_NOT_FUND.value:
            return self.get_single_order_amount_confirm_goods_but_not_fund(order)
        elif order_status == global_params.OrderStatus.SEND_GOODS_BUT_NOT_FUND.value:
            return self.get_single_order_amount_send_goods_but_not_fund(order)

        return None

    # 单笔交易成功
    def get_single_order_amount_success(self, order):
        amount = OrderAmount()
        amount.id = order["baseInfo"]["id"]
        amount.sum_product_payment = round(order["baseInfo"]["sumProductPayment"], 2)
        amount.shipping_fee = round(order["baseInfo"]["shippingFee"], 2)
        amount.total_amount = round(order["baseInfo"]["totalAmount"], 2)
        amount.refund = round(order["baseInfo"]["refund"], 2)

        return amount

    def get_single_order_amount_cancel(self, order):
        amount = OrderAmount()
        # 买家没付钱主动取消
        if order["baseInfo"]["alipayTradeId"] == "UNCREATED":
            return None
        # 买家没付钱被动取消
        if "closeReason" in order["baseInfo"]:
            return None

        # 订单退款/取消
        amount.id = order["baseInfo"]["id"]
        amount.sum_product_payment = round(order["baseInfo"]["sumProductPayment"], 2)
        amount.shipping_fee = round(order["baseInfo"]["shippingFee"], 2)
        amount.total_amount = round(order["baseInfo"]["totalAmount"], 2)
        amount.refund = round(order["baseInfo"]["refund"], 2)
        amount.refund_shipping_fee = round(
            amount.refund - amount.total_amount + amount.shipping_fee, 2
        )

        return amount

    def get_single_order_amount_waitsellersend(self, order):
        amount = OrderAmount()
        has_refund = False
        refund_amount = None
        # 待收货 -> 有退款
        if "refundStatus" in order["baseInfo"]:
            if order["baseInfo"]["refundStatus"] == "waitselleragree":
                has_refund = True
                product_items = order["productItems"]
                refund_amount = self.get_refund_amount_info_by_product_items(
                    product_items
                )
                # pprint(refund_amount)

        # 首先获取订单参数
        amount.id = order["baseInfo"]["id"]
        amount.sum_product_payment = round(order["baseInfo"]["sumProductPayment"], 2)
        amount.shipping_fee = round(order["baseInfo"]["shippingFee"], 2)
        amount.total_amount = round(order["baseInfo"]["totalAmount"], 2)
        amount.refund = round(order["baseInfo"]["refund"], 2)

        # 再减去退款
        if has_refund:
            amount.refund += refund_amount["refund_amount"]

        return amount

    def get_single_order_amount_waitbuyerreceive(self, order):
        amount = OrderAmount()
        has_refund = False
        refund_amount = None
        # 待收货 -> 有退款
        if "refundStatus" in order["baseInfo"]:
            if order["baseInfo"]["refundStatus"] == "waitselleragree":
                has_refund = True
                product_items = order["productItems"]
                refund_amount = self.get_refund_amount_info_by_product_items(
                    product_items
                )
                # pprint(refund_amount)

        # 首先获取订单参数
        amount.id = order["baseInfo"]["id"]
        amount.sum_product_payment = round(order["baseInfo"]["sumProductPayment"], 2)
        amount.shipping_fee = round(order["baseInfo"]["shippingFee"], 2)
        amount.total_amount = round(order["baseInfo"]["totalAmount"], 2)
        amount.refund = round(order["baseInfo"]["refund"], 2)

        # 再减去退款
        if has_refund:
            amount.refund += refund_amount["refund_amount"]

        return amount

    def get_refund_amount_info_by_product_items(self, product_items):
        all_amount = {"normal_amount": 0, "refund_amount": 0}
        for product_item in product_items:
            if (
                "refundStatus" in product_item
                and product_item["refundStatus"] == "WAIT_SELLER_AGREE"
            ):
                all_amount["refund_amount"] += product_item["itemAmount"]
            else:
                all_amount["normal_amount"] += product_item["itemAmount"]

        return all_amount

    def get_single_order_amount_confirm_goods_but_not_fund(self, order):
        # 丢件
        amount = OrderAmount()
        amount.id = order["baseInfo"]["id"]
        amount.sum_product_payment = round(order["baseInfo"]["sumProductPayment"], 2)
        amount.shipping_fee = round(order["baseInfo"]["shippingFee"], 2)
        amount.total_amount = round(order["baseInfo"]["totalAmount"], 2)
        amount.refund = round(order["baseInfo"]["refund"], 2)

        return amount

    def get_single_order_amount_send_goods_but_not_fund(self, order):
        # 丢件
        amount = OrderAmount()
        amount.id = order["baseInfo"]["id"]
        amount.sum_product_payment = round(order["baseInfo"]["sumProductPayment"], 2)
        amount.shipping_fee = round(order["baseInfo"]["shippingFee"], 2)
        amount.total_amount = round(order["baseInfo"]["totalAmount"], 2)
        amount.refund = round(order["baseInfo"]["refund"], 2)

        return amount

    # 获取利润
    def get_profit(self):
        self.check_orders()

    def get_fake_order(self):
        self.check_orders()

    # 收集原始订单 (暂时没用，订单重复)
    def get_origin_order_list(self):
        print("start get_origin_order_list")
        # 1. 遍历状态
        for order_status in self.settings.order_status:
            print(order_status)
            req_data = {
                "createStartTime": self.settings.start_time.strip(),
                "createEndTime": self.settings.end_time.strip(),
                "orderStatus": order_status,  # 只获取已发出 或者 已签收  todo：或者已完成未到账 或者已完成
                # "refundStatus": "refundsuccess",
                "buyerMemberId": "memberId",
                "buyerLoginId": "LoginId",
                "needMemoInfo": "true",
                "pageSize": 20,
            }
            # 2. 遍历店铺
            for shop_name in self.settings.shop_names:
                if "_aop_signature" in req_data:
                    req_data.pop("_aop_signature")
                print("start get_origin_order_list-" + order_status + "-" + shop_name)
                # 2.1 获取总页数
                res = api.GetTradeData(req_data, shop_name)
                page_num = utils.CalPageNum(res["totalRecord"])

                print("订单页数：" + str(page_num))

                # 2.2 按页获取订单项
                for pageId in range(page_num):
                    req_data = {
                        "page": str(pageId + 1),
                        "createStartTime": self.settings.start_time.strip(),
                        "createEndTime": self.settings.end_time.strip(),
                        "orderStatus": order_status,  # 只获取已发出 或者 已签收  todo：或者已完成未到账 或者已完成
                        # "refundStatus":"refundsuccess",
                        "buyerMemberId": "memberId",
                        "buyerLoginId": "LoginId",
                        "needMemoInfo": "true",
                        "pageSize": 20,
                    }
                    # print(req_data)
                    res = api.GetTradeData(req_data, shop_name)
                    # 2.2.1 遍历订单
                    for order in res["result"]:
                        # print(order)
                        # 过滤掉刷单
                        if ("sellerRemarkIcon" in order["baseInfo"]) and (
                            order["baseInfo"]["sellerRemarkIcon"]
                            == global_params.OrderTags.BLUE.value
                            or order["baseInfo"]["sellerRemarkIcon"]
                            == global_params.OrderTags.GREEN.value
                        ):
                            self.shuadan_orders += order
                            continue
                        # todo: 做一个单独的过滤方法 过滤红 或者 黄标签
                        self.origin_orders[shop_name].append(order)

        self.hasGetOrders = True
        print("end get_origin_order_list")

    # 无视订单状态收集所有原始订单
    def get_all_origin_order_list(self):
        print("start get_all_origin_order_list")
        req_data = {
            "createStartTime": self.settings.start_time_str.strip(),
            "createEndTime": self.settings.end_time_str.strip(),
            "needMemoInfo": "true",
            "needBuyerAddressAndPhone": "true",
            # "isHis":"true",
            "pageSize": 20,
        }
        # 2. 遍历店铺
        for shop_name in self.settings.shop_names:
            if "_aop_signature" in req_data:
                req_data.pop("_aop_signature")
            print("start get_all_origin_order_list-" + shop_name)
            # 获取总页数
            res = api.GetTradeData(req_data, shop_name)
            page_num = utils.CalPageNum(res["totalRecord"])

            print("订单页数：" + str(page_num))

            # 2.2 按页获取订单项
            for pageId in range(page_num):
                req_data = {
                    "page": str(pageId + 1),
                    "createStartTime": self.settings.start_time_str.strip(),
                    "createEndTime": self.settings.end_time_str.strip(),
                    "needMemoInfo": "true",
                    "needBuyerAddressAndPhone": "true",
                    # "isHis": "true",
                    "pageSize": 20,
                }
                # print(req_data)
                res = api.GetTradeData(req_data, shop_name)
                # 2.2.1 遍历订单
                for order in res["result"]:
                    # print(order)
                    # 过滤掉刷单
                    if ("sellerRemarkIcon" in order["baseInfo"]) and (
                        order["baseInfo"]["sellerRemarkIcon"]
                        == global_params.OrderTags.BLUE.value
                        or order["baseInfo"]["sellerRemarkIcon"]
                        == global_params.OrderTags.GREEN.value
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

    def get_history_orders(self):
        pass
