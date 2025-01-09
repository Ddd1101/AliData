import os

class Utils:
    def __init__(self, path):
        """初始化 Person 对象"""
        self.name = path
    def greet(self):
        """打印问候语"""
        return f"你好，我叫 {self.name}，我 {self.age} 岁。"

    def have_birthday(self):
        """年龄加一"""
        self.age += 1
        print(f"生日快乐！现在你 {self.age} 岁了。")

AppKey = {
    "联球制衣厂": "3527689",
    "朝雄制衣厂": "4834884",
    "朝瑞制衣厂": "4834884",
    "万盈饰品厂": "3527689",
    "义乌睿得": "3527689",
    "义乌茜阳": "4834884",
}
AppSecret = {
    "联球制衣厂": b"Zw5KiCjSnL",
    "朝雄制衣厂": b"JeV4khKJshr",
    "朝瑞制衣厂": b"JeV4khKJshr",
    "万盈饰品厂": b"Zw5KiCjSnL",
    "义乌睿得": b"Zw5KiCjSnL",
    "义乌茜阳": b"JeV4khKJshr",
}
access_token = {
    "联球制衣厂": "999d182a-3576-4aee-97c5-8eeebce5e085",
    "朝雄制衣厂": "ef65f345-7060-4031-98ad-57d7d857f4d9",
    "朝瑞制衣厂": "438de82f-d44f-44f1-b343-4e0721b9e767",
    "万盈饰品厂": "cd62b5c5-00d1-41c9-becf-4f9dfcbf4b75",
    "义乌睿得": "7f813331-15d6-40a8-97ac-00589efc8e81",
    "义乌茜阳": "a8de29c8-ff57-4336-b4e7-e1c3d1c72f34",
}

en_code = ["s", "S", "m", "M", "l", "L", "x", "X"]
base_url = "https://gw.open.1688.com/openapi/"

path = os.path.realpath(os.curdir)

price_path = path + "/price.xlsx"
price_accessor_path = path + "/price_accessor.xlsx"

factory_path = path + "/factory.xlsx"

logging_path = path + "\\Log\\"

request_type = {
    "trade": "param2/1/com.alibaba.trade/",
    "delivery": "param2/1/com.alibaba.logistics/",
}

worksheet = None

## shop type
SHOPTYPE_ALI_CHILD_CLOTH = 1
SHOPTYPE_ALI_ACCESSOR = 2

global_SHOPTYPE = SHOPTYPE_ALI_CHILD_CLOTH
global_OrderNum = 0

from enum import Enum

# 定义一个枚举类型
class OrderStatus(Enum):
    TRADE_SUCCESS = "success"
    WAIT_SELLER_SEND = "waitsellersend"
    WAIT_BUYER_RECEIVE = "waitbuyerreceive"

class ShopType(Enum):
    ALI_CHILD_CLOTH = 1
    ALI_ACCESSOR = 2


