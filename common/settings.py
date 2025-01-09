class Settings:
    def __init__(self,
                 shop_names,
                 start_time,
                 end_time,
                 order_status: list,
                 is_print_unit_price=False,
                 filter_tags=None,
                 limit_delivered_ime=None):
        if filter_tags is None:
            filter_tags = []
        if limit_delivered_ime is None:
            limit_delivered_ime = []

        self.shop_names = shop_names
        self.start_time = start_time
        self.end_time = end_time
        self.order_status = order_status
        self.limit_delivered_ime = limit_delivered_ime
        self.filter_tags = filter_tags
        self.is_print_unit_price = is_print_unit_price
