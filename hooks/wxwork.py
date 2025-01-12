import requests
import json

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
def send_md(webhook, content):
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    data = {

        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    data = json.dumps(data)
    info = requests.post(url=webhook, data=data, headers=header)


content = "# 实时新增用户反馈<font color=\"warning\">132例</font>，请相关同事注意。\n >类型:<font color=\"comment\">用户反馈</font>\n > 普通用户反馈:<font color=\"comment\">117例</font>\n## VIP用户反馈:<font color=\"comment\">15例</font>"

send_md(webhook, content)
