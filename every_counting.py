from datetime import datetime, date, timedelta

import global_params
from manager.cloth_trade_manager import ClothTradeManager

if __name__ == "__main__":
    todayTmp = datetime.strptime(str(date.today()), "%Y-%m-%d")
    # start_time = todayTmp + timedelta(days=-7)
    # end_time = todayTmp + timedelta(days=-2)
    start_time = datetime(2024, 10, 1)
    end_time = datetime(2024, 11, 1)
    cloth_trade_manager = ClothTradeManager()

    shop_names = ["万盈饰品厂", "联球制衣厂", "朝雄制衣厂"]
    order_status = [global_params.OrderStatus.TRADE_SUCCESS.value, global_params.OrderStatus.WAIT_BUYER_RECEIVE.value]
    filter_tags = [global_params.OrderTags.BLUE.value, global_params.OrderTags.GREEN.value]
    cloth_trade_manager.set_params(shop_names=shop_names, start_time=start_time, end_time=end_time,
                                   order_status=order_status, filter_tags=filter_tags)

    cloth_trade_manager.get_sales_amount()

    ############################################################################

    start_time2 = datetime(2024, 11, 1)
    end_time2 = datetime(2024, 12, 1)
    cloth_trade_manager2 = ClothTradeManager()

    cloth_trade_manager2.set_params(shop_names=shop_names, start_time=start_time2, end_time=end_time2,
                                   order_status=order_status, filter_tags=filter_tags)

    cloth_trade_manager2.get_sales_amount()

    ############################################################################

    start_time3 = datetime(2024, 12, 1)
    end_time3 = datetime(2025, 1, 1)
    cloth_trade_manager3 = ClothTradeManager()

    cloth_trade_manager3.set_params(shop_names=shop_names, start_time=start_time3, end_time=end_time3,
                                    order_status=order_status, filter_tags=filter_tags)

    cloth_trade_manager3.get_sales_amount()
