import sys
import os

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上一层目录
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

# 将上一层目录添加到系统路径
sys.path.append(parent_dir)

from datetime import datetime, date, timedelta
import schedule
import time
import requests
import json
import global_params
from manager.cloth_trade_manager import ClothTradeManager

webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c8732431-40a3-4915-b117-76940eacca18"


# 发送文本消息
def send_text(webhook, content, mentioned_list=None, mentioned_mobile_list=None):
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    data = {

        "msgtype": "text",
        "text": {
            "content": content
            , "mentioned_list": mentioned_list
            , "mentioned_mobile_list": mentioned_mobile_list
        }
    }
    data = json.dumps(data)
    info = requests.post(url=webhook, data=data, headers=header)


# 发送markdown消息
def send_md(webhook, messsage):
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    data = {

        "msgtype": "markdown",
        "markdown": {
            "content": messsage
        }
    }
    data = json.dumps(data)
    info = requests.post(url=webhook, data=data, headers=header)


# "# **销售汇算**\n" +
# "#### **请相关同事注意，及时跟进！**\n" +
# "> **--------------------联球制衣厂--------------------**\n"+
# "> **销售额：**<font color=\"info\">%s</font>\n**失败数：**<font color=\"warning\">%s</font>\n" +
# "> **退款额：**<font color=\"info\">%s</font>\n**失败数：**<font color=\"warning\">%s</font>\n" +

def message(message):
    data = {
        "msgtype": "markdown",  # 消息类型，此时固定为markdown
        "markdown": {
            "content": ("# **销售汇算**\n" +
                        "### 1688平台\n" +
                        message)
        }
    }
    return data


def formate_single_message(shop_name, sale_amount, refund_amount):
    res = ("> **--------------------%s--------------------**\n" +
           "> **销售额：**<font color=\"info\">%s 元</font>\n" +
           "> **退款数：**<font color=\"info\">%s 元</font>\n" +
           "> **总   计：**<font color=\"info\">%s 元</font>\n") % (
              shop_name, round(sale_amount, 2), round(refund_amount, 2), round(sale_amount - refund_amount, 2))
    return res


def formate_all_message(amount):
    today = datetime.strptime(str(date.today()), "%Y-%m-%d")
    time = today + timedelta(days=-1)
    header = "# **销售汇算**\n" + "#### **1688平台**\n " + time.strftime("%Y-%m-%d" + "\n")
    tailer = ""

    total_message = ""
    total_amount = 0
    total_refund = 0
    for shop_name in amount:
        total_message += formate_single_message(shop_name, amount[shop_name].total_amount,
                                                amount[shop_name].refund)
        total_amount += amount[shop_name].total_amount
        total_refund += amount[shop_name].refund

    total_message += formate_single_message("销售额总和", total_amount, total_refund)

    return header + total_message + tailer


def start():
    todayTmp = datetime.strptime(str(date.today()), "%Y-%m-%d")
    start_time = todayTmp + timedelta(days=-1)
    end_time = todayTmp + timedelta(days=0)
    # start_time = datetime(2024, 12, 1)
    # end_time = datetime(2025, 1, 13)
    cloth_trade_manager = ClothTradeManager()

    shop_names = ["万盈饰品厂", "联球制衣厂", "朝雄制衣厂", "朝瑞制衣厂"]
    order_status = [global_params.OrderStatus.TRADE_SUCCESS.value, global_params.OrderStatus.TRADE_CANCEL.value,
                    global_params.OrderStatus.SEND_GOODS_BUT_NOT_FUND.value,
                    global_params.OrderStatus.WAIT_BUYER_RECEIVE.value,
                    global_params.OrderStatus.CONFIRM_GOODS_BUT_NOT_FUND.value,
                    global_params.OrderStatus.SEND_GOODS_BUT_NOT_FUND.value]
    # order_status = [global_params.OrderStatus.WAIT_SELLER_SEND.value]
    filter_tags = [global_params.OrderTags.BLUE.value, global_params.OrderTags.GREEN.value]
    cloth_trade_manager.set_params(shop_names=shop_names, start_time=start_time, end_time=end_time,
                                   order_status=order_status, filter_tags=filter_tags)

    amount_res = cloth_trade_manager.get_sales_amount()
    message = formate_all_message(amount_res)

    send_md(webhook, message)


if __name__ == "__main__":
    # 设置每日零点执行任务
    schedule.every().day.at("00:00").do(start)

    print("定时任务已设置")

    while True:
        # 检查并执行任务
        schedule.run_pending()
        time.sleep(1)
