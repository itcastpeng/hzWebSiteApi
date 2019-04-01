# developer: 张聪
# email: 18511123018@163.com

# 微信小程序api

import os
import json
import requests
from publicFunc.weixin.weixin_api_public import WeixinApiPublic


class WeChatApi(WeixinApiPublic):

    def __init__(self, wechat_data_path=None):
        if wechat_data_path:
            self.wechat_data_path = wechat_data_path
        else:
            self.wechat_data_path = os.path.join(os.getcwd(), "publicFunc", "weixin", "wechat_data.json")

        # print(wechat_data_path)
        with open(self.wechat_data_path, "r", encoding="utf8") as f:
            data = json.loads(f.read())

            self.APPID = data["XCXAPPID"]
            self.APPSECRET = data["XCXAPPSECRET"]

        # self.get_users()

    # 获取用户openid、session_key、unionid
    def get_jscode2session(self, code):
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": self.APPID,
            "secret": self.APPSECRET,
            "js_code": code,
            "grant_type": "authorization_code",
        }
        ret = requests.get(url, params=params)
        return ret.json()

