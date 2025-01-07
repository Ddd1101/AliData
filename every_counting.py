from datetime import datetime, date, timedelta

from manager.cloth_trade_manager import ClothTradeManager

if __name__ == "__main__":
    todayTmp = datetime.strptime(str(date.today()), "%Y-%m-%d")
    startDateTime = todayTmp + timedelta(days=-1)
    endDateTime = todayTmp + timedelta(days=0)
    cloth_trade_manager = ClothTradeManager()

    shop_names = ["联球制衣厂", "朝雄制衣厂"]
    order_status = []
    filter_tags = []
    mode = []
    cloth_trade_manager.set_params(startDateTime, endDateTime, shop_names, order_status, filter_tags)

    cloth_trade_manager.start()
