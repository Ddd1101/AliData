import sys
import os

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# AliData 所在目录（ShopManager 根目录），供 AliData.* 包导入
parent_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))

# 将上一层目录添加到系统路径
sys.path.append(parent_dir)

from datetime import datetime, date, timedelta
import schedule
import time
import requests
import json
import AliData.global_params as global_params
from AliData.manager.cloth_trade_manager import ClothTradeManager
from AliData.common.order_amount import OrderAmount


# 发送文本消息
def send_text(webhook, content, mentioned_list=None, mentioned_mobile_list=None):
    header = {"Content-Type": "application/json", "Charset": "UTF-8"}
    data = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": mentioned_list,
            "mentioned_mobile_list": mentioned_mobile_list,
        },
    }
    data = json.dumps(data)
    info = requests.post(url=webhook, data=data, headers=header)


# 发送markdown消息
def send_md(webhook, messsage):
    header = {"Content-Type": "application/json", "Charset": "UTF-8"}
    data = {"msgtype": "markdown", "markdown": {"content": messsage}}
    data = json.dumps(data)
    info = requests.post(url=webhook, data=data, headers=header)
    return info


# "# **销售汇算**\n" +
# "#### **请相关同事注意，及时跟进！**\n" +
# "> **--------------------联球制衣厂--------------------**\n"+
# "> **销售额：**<font color=\"info\">%s</font>\n**失败数：**<font color=\"warning\">%s</font>\n" +
# "> **退款额：**<font color=\"info\">%s</font>\n**失败数：**<font color=\"warning\">%s</font>\n" +


def message(message):
    data = {
        "msgtype": "markdown",  # 消息类型，此时固定为markdown
        "markdown": {"content": ("# **销售汇算**\n" + "### 1688平台\n" + message)},
    }
    return data


def formate_single_message(shop_name, amount: OrderAmount):
    res = (
        "> **------%s------**\n"
        + '> **销售额：**<font color="info">%s 元</font>\n'
        + '> **退款数：**<font color="info">%s 元</font>\n'
        + '> **订单数：**<font color="info">%s 单</font>\n'
        + '> **总   计：**<font color="warning">%s 元</font>\n'
    ) % (
        shop_name,
        round(amount.total_amount, 2),
        round(amount.refund, 2),
        amount.order_count,
        round(amount.total_amount - amount.refund, 2),
    )
    return res


def formate_all_message(amount, start_time, end_time):
    header = (
        "# **销售汇算**\n"
        + "#### **1688平台**\n "
        + '**<font color="warning">'
        + start_time.strftime("%Y-%m-%d")
        + " 到 "
        + end_time.strftime("%Y-%m-%d" + "</font>**" + "\n")
    )
    tailer = ""

    total_message = ""
    total_amount = OrderAmount()
    for shop_name in amount:
        total_message += formate_single_message(shop_name, amount[shop_name])
        total_amount.total_amount += amount[shop_name].total_amount
        total_amount.refund += amount[shop_name].refund
        total_amount.order_count += amount[shop_name].order_count

    total_message += formate_single_message("销售额总和", total_amount)

    return header + total_message + tailer


def formate_all_message_for_other(amount, start_time, end_time):
    header = (
        "# **销售汇算**\n"
        + "#### **1688平台**\n "
        + '**<font color="warning">'
        + start_time.strftime("%Y-%m-%d")
        + " 到 "
        + end_time.strftime("%Y-%m-%d" + "</font>**" + "\n")
    )
    tailer = ""

    total_message = ""
    total_amount = 0
    total_refund = 0
    total_order_count = 0
    for shop_name in amount:
        total_message += formate_single_message(shop_name, amount[shop_name])
        total_amount += amount[shop_name].total_amount
        total_refund += amount[shop_name].refund
        total_order_count += amount[shop_name].order_count

    return header + total_message + tailer


# 饰品店成本核算方式与服装不同，暂未接入，成本按 0 计
ACCESSORY_SHOPS = {"万盈饰品厂"}

PROFIT_KEYS = (
    "total_amount",
    "shipping_fee",
    "refund",
    "cost",
    "shipping_cost",
    "commission",
    "profit",
)


# 汇总各店铺利润（按支付时间统计当天数据）
def aggregate_shop_profits(cloth_trade_manager, start_time, end_time):
    # 支付时间窗口（字符串格式零填充，可直接比较）
    pay_start = start_time.strftime("%Y-%m-%d %H:%M:%S")
    pay_end = end_time.strftime("%Y-%m-%d %H:%M:%S")
    shop_profits = {}
    for shop_name, orders in cloth_trade_manager.origin_orders.items():
        with_cost = shop_name not in ACCESSORY_SHOPS
        p = dict.fromkeys(PROFIT_KEYS, 0.0)
        p["order_count"] = 0
        for order in orders:
            info = cloth_trade_manager.get_single_order_profit(
                order, with_cost=with_cost
            )
            if not (pay_start <= info["pay_time"] < pay_end):
                continue
            p["order_count"] += 1
            for k in PROFIT_KEYS:
                p[k] += info[k]
        shop_profits[shop_name] = p
    return shop_profits


# 单店利润汇总 -> markdown
def formate_profit_single_message(shop_name, p):
    income = p["total_amount"] + p["shipping_fee"]
    rate = p["profit"] / income * 100 if income else 0
    res = (
        "> **------%s------**\n"
        + '> **商品总收款：**<font color="info">%.2f 元</font>\n'
        + '> **运　费　　：**<font color="info">%.2f 元</font>\n'
        + '> **总退款　　：**<font color="info">%.2f 元</font>\n'
        + '> **成　本　　：**<font color="info">%.2f 元</font>\n'
        + '> **运费成本　：**<font color="info">%.2f 元</font>\n'
        + '> **平台抽佣　：**<font color="info">%.2f 元</font>\n'
        + '> **利　润　　：**<font color="warning">%.2f 元</font>\n'
        + '> **利 润 率　：**<font color="warning">%.2f%%</font>\n'
        + '> **订 单 数　：**<font color="info">%d 单</font>\n'
    ) % (
        shop_name,
        p["total_amount"],
        p["shipping_fee"],
        p["refund"],
        p["cost"],
        p["shipping_cost"],
        p["commission"],
        p["profit"],
        rate,
        p["order_count"],
    )
    return res


def formate_profit_message(shop_profits, start_time, end_time):
    header = (
        "# **利润汇算**\n"
        + "#### **1688平台**\n "
        + '**<font color="warning">'
        + start_time.strftime("%Y-%m-%d")
        + " 到 "
        + end_time.strftime("%Y-%m-%d")
        + "</font>**\n"
    )
    total_message = ""
    total = None
    for shop_name in shop_profits:
        total_message += formate_profit_single_message(
            shop_name, shop_profits[shop_name]
        )
        if total is None:
            total = dict(shop_profits[shop_name])
        else:
            for k in total:
                total[k] += shop_profits[shop_name][k]
    if total is not None and len(shop_profits) > 1:
        total_message += formate_profit_single_message("合计", total)
    return header + total_message


def start():
    webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c8732431-40a3-4915-b117-76940eacca18"
    # webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=60d040d5-9595-490f-82ec-962b10cdf3e3"
    todayTmp = datetime.strptime(str(date.today()), "%Y-%m-%d")
    start_time = todayTmp + timedelta(days=-1)
    end_time = todayTmp + timedelta(days=0)
    # start_time = datetime(2024, 1, 1)
    # end_time = datetime(2025, 1, 30)
    cloth_trade_manager = ClothTradeManager()

    shop_names = ["万盈饰品厂", "联球制衣厂", "朝雄制衣厂"]
    order_status = {global_params.OrderStatus.ALL.value}
    filter_tags = [
        global_params.OrderTags.BLUE.value,
        global_params.OrderTags.GREEN.value,
    ]
    cloth_trade_manager.set_params(
        shop_names=shop_names,
        start_time=start_time,
        end_time=end_time,
        order_status=order_status,
        filter_tags=filter_tags,
    )
    cloth_trade_manager.get_all_origin_order_list()

    shop_profits = aggregate_shop_profits(cloth_trade_manager, start_time, end_time)
    message = formate_profit_message(shop_profits, start_time, end_time)

    return send_md(webhook, message)


def compare():
    webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=fe36a783-b9a2-4382-9726-6879ec2ae840"
    # webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=60d040d5-9595-490f-82ec-962b10cdf3e3"
    todayTmp = datetime.strptime(str(date.today()), "%Y-%m-%d")
    start_time = todayTmp + timedelta(days=-1)
    end_time = todayTmp + timedelta(days=0)
    # start_time = datetime(2024, 1, 1)
    # end_time = datetime(2025, 1, 30)
    cloth_trade_manager = ClothTradeManager()

    shop_names = ["万盈饰品厂", "联球饰品厂", "义乌睿得", "义乌茜阳"]
    order_status = {global_params.OrderStatus.ALL.value}
    filter_tags = [
        global_params.OrderTags.BLUE.value,
        global_params.OrderTags.GREEN.value,
    ]
    cloth_trade_manager.set_params(
        shop_names=shop_names,
        start_time=start_time,
        end_time=end_time,
        order_status=order_status,
        filter_tags=filter_tags,
    )

    amount_res = cloth_trade_manager.get_sales_amount()
    message = formate_all_message_for_other(amount_res, start_time, end_time)

    send_md(webhook, message)


# compare()
#
# start()

if __name__ == "__main__":
    # 设置每日零点执行任务
    schedule.every().day.at("00:00").do(start)

    schedule.every().day.at("00:00").do(compare)

    print("定时任务已设置")

    while True:
        # 检查并执行任务
        schedule.run_pending()
        time.sleep(1)
