from datetime import datetime, date, timedelta

import global_params
from manager.cloth_trade_manager import ClothTradeManager

if __name__ == "__main__":
    todayTmp = datetime.strptime(str(date.today()), "%Y-%m-%d")
    start_time = todayTmp + timedelta(days=-1)
    end_time = todayTmp + timedelta(days=0)
    cloth_trade_manager = ClothTradeManager()

    shop_names = ["联球制衣厂", "朝雄制衣厂"]
    order_status = []
    filter_tags = [global_params.OrderStatus.TRADE_SUCCESS]
    cloth_trade_manager.set_params(shop_names=shop_names, create_start_time=start_time,
                                   create_end_time=end_time, order_status=order_status, filter_tags=filter_tags)
