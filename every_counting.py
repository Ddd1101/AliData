from datetime import datetime, date, timedelta

import global_params
from manager.cloth_trade_manager import ClothTradeManager

if __name__ == "__main__":
    todayTmp = datetime.strptime(str(date.today()), "%Y-%m-%d")
    start_time = todayTmp + timedelta(days=-1)
    end_time = todayTmp + timedelta(days=0)
    cloth_trade_manager = ClothTradeManager()

    shop_names = ["朝雄制衣厂"]
    order_status = [global_params.OrderStatus.WAIT_BUYER_RECEIVE.value]
    filter_tags = []
    cloth_trade_manager.set_params(shop_names=shop_names, start_time=start_time, end_time=end_time,
                                   order_status=order_status, filter_tags=filter_tags)

    cloth_trade_manager.get_sales_amount()
