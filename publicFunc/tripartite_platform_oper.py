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
        self.tripartite_platform_appid = obj.appid
        self.tripartite_platform_appsecret = obj.appsecret
        if int(obj.access_token_time) - int(time.time()) <= 600: # token还有10分钟过期
            self.get_component_access_token(obj)
            obj = models.TripartitePlatform.objects.get(id=1)
            self.token = obj.component_access_token

        self.params = {
            'component_access_token': self.token
        }

    # 获取第三方平台component_access_token
    def get_component_access_token(self, obj):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
        print('self.component_verify_ticket----> ', self.component_verify_ticket)
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "component_appsecret": self.tripartite_platform_appsecret,
            "component_verify_ticket": self.component_verify_ticket
        }
        ret = requests.post(url, data=json.dumps(post_data))
        """
            {
                "component_access_token":"61W3mEpU66027wgNZ_MhGHNQDHnFATkDa9-2llqrMBjUwxRSNPbVsMmyD-yq8wZETSoE5NQgecigDrSHkPtIYA", 
                "expires_in":7200
            }
        """
        print('ret.获取第三方平台component_access_token()---------> ', ret.json())
        component_access_token = ret.json().get('component_access_token')
        expires_in = int(time.time()) + ret.json().get('expires_in')
        obj.access_token_time = expires_in
        obj.component_access_token = component_access_token
        obj.save()


    # 获取预授权码 pre_auth_code
    def get_pre_auth_code(self):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode'

        post_data = {
            "component_appid": self.tripartite_platform_appid
        }
        ret = requests.post(url, params=self.params, data=json.dumps(post_data))

        print('获取预授权码 pre_auth_code--------> ', ret.json())
        pre_auth_code = ret.json().get('pre_auth_code')
        return pre_auth_code

    # 使用授权码换取公众号或小程序的接口调用凭据和授权信息
    def exchange_calling_credentials(self):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth'
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "authorization_code": ''  # 授权code
        }
        ret = requests.post(url, params=self.params, data=post_data)
        print('ret.text===exchange_calling_credentials=======> ', ret.text)


    # 获取（刷新）授权公众号或小程序的接口调用凭据（令牌）
    def refresh_exchange_calling_credentials(self):
        url = 'https:// api.weixin.qq.com /cgi-bin/component/api_authorizer_token'
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "authorizer_appid":self.appid,
            "authorizer_refresh_token":self.token,
        }

        ret = requests.post(url, params=self.params, data=post_data)
        print('refresh_exchange_calling_credentials----> ', ret.text)

    # 公众号/小程序 获取授权方的帐号基本信息
    def get_account_information(self, authorized_party_type):
        if authorized_party_type == 1: # 公众号
            pass
        else: # 小程序
            pass

        url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
        post_data = {
            "component_appid": self.tripartite_platform_appid,    # 第三方APPID
            "authorizer_appid": self.appid       # 授权方APPID
        }
        ret = requests.post(url, params=self.params, data=post_data)
        print('get_account_information=----> ', ret.text)

    # 获取授权方的选项设置信息
    def option_setting_information(self, option_name):
        url = 'https://api.weixin.qq.com/cgi-bin/component/ api_get_authorizer_option'
        post_data = {
            "component_appid":self.tripartite_platform_appid,
            "authorizer_appid": self.appid,
            "option_name": option_name, # 选项名称
        }

        ret = requests.post(url, params=self.params, data=post_data)
        print('-option_setting_information-----------> ', ret.text)

    # 设置授权方的选项信息
    def set_authorizer_information(self, option_name, option_value):
        url = 'https://api.weixin.qq.com/cgi-bin/component/ api_set_authorizer_option'
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "authorizer_appid": self.appid,
            "option_name": option_name, # 选项名称
            "option_value": option_value, # 选项值
        }
        ret = requests.post(url, params=self.params, data=post_data)

        print('set_authorizer_information------> ', ret.text)

    # 推送授权相关通知
    # def push_authorization_notification(self):









