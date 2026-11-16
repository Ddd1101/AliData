from datetime import timedelta, datetime

import AliData.utils.ali_api as api


class Settings:
    def __init__(
        self,
        shop_names,
        start_time: datetime,
        end_time,
        order_status: list,
        is_print_unit_price=False,
        filter_tags=None,
        limit_delivered_ime=None,
    ):
        if filter_tags is None:
            filter_tags = []
        if limit_delivered_ime is None:
            limit_delivered_ime = []

        self.order_start_time = start_time
        self.shop_names = shop_names
        self.start_time = start_time
        self.end_time = end_time
        self.order_status = order_status
        self.limit_delivered_ime = limit_delivered_ime
        self.filter_tags = filter_tags
        self.is_print_unit_price = is_print_unit_price
        # 拉单按创建时间窗口取近 7 天，兜底“下单早、付款晚”的订单（否则昨天付款但更早创建的订单会缺失）
        self.order_time = start_time - timedelta(days=6)
        self.start_time_str = api.formate_date(self.order_time)
        self.end_time_str = api.formate_date(end_time)
