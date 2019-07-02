from api import models
from publicFunc import Response, account
from django.http import JsonResponse
import requests, datetime, json, time








# 三方平台操作

class tripartite_platform_oper():
    response = Response.ResponseObj()
    def __init__(self, appid, appsecret):
        obj = models.TripartitePlatform.objects.get(id=1)
        self.appsecret = appsecret
        self.appid = appid
        self.component_verify_ticket = obj.component_verify_ticket
        self.token = obj.component_access_token

        if obj.access_token_time - int(time.time()) <= 600: # token还有10分钟过期
            self.get_component_access_token(obj)
            obj = models.TripartitePlatform.objects.get(id=1)
            self.token = obj.component_access_token


    # 获取三方平台 component_access_token
    def get_component_access_token(self, obj):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
        post_data = {
            "component_appid": self.appid,
            "component_appsecret": self.appsecret,
            "component_verify_ticket": self.component_verify_ticket
        }
        ret = requests.post(url, data=post_data)
        """
            {
                "component_access_token":"61W3mEpU66027wgNZ_MhGHNQDHnFATkDa9-2llqrMBjUwxRSNPbVsMmyD-yq8wZETSoE5NQgecigDrSHkPtIYA", 
                "expires_in":7200
            }
        """
        component_access_token = ret.json().get('component_access_token')
        expires_in = int(time.time()) + ret.json().get('expires_in')
        obj.access_token_time = expires_in
        obj.component_access_token = component_access_token
        obj.save()


    # 获取预授权码 pre_auth_code
    def get_pre_auth_code(self):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode'
        params = {
            'component_access_token':self.token
        }
        post_data = {
            "component_appid": self.appid
        }
        ret = requests.post(url, params=params, data=post_data)

        print('get_pre_auth_code--------> ', ret.text)

    # 使用授权码换取公众号或小程序的接口调用凭据和授权信息
    def exchange_calling_credentials(self):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth'
        params = {
            'component_access_token': self.token
        }
        post_data = {
            "component_appid": self.appid,
            "authorization_code": ''  # 授权code
        }



















if __name__ == '__main__':
    objs = tripartite_platform_oper()


