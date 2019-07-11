from api import models
from publicFunc import Response, account
from django.http import JsonResponse
import requests, datetime, json, time







# 三方平台操作
class tripartite_platform_oper():
    response = Response.ResponseObj()
    def __init__(self):
        obj = models.TripartitePlatform.objects.get(id=1)
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
        print('获取第三方平台component_access_token---------> ', ret.json())
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

    # 使用授权码换取公众号或小程序的接口调用凭据和授权信息exchange_calling_credentials
    def exchange_calling_credentials(self, auth_type, auth_code):
        """

        :param auth_type: 类型 1公众号 2小程序
        :param auth_code: 授权码
        :return:
        """
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth'
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "authorization_code": auth_code,            # 授权code
        }
        ret = requests.post(url, params=self.params, data=json.dumps(post_data))
        print('使用授权码换取公众号或小程序的接口调用凭据和授权信息exchange_calling_credentials=======> ', ret.text)
        authorization_info = ret.json().get('authorization_info')
        if authorization_info:
            authorizer_appid = authorization_info.get('authorizer_appid')
            authorizer_access_token = authorization_info.get('authorizer_access_token')
            expires_in = authorization_info.get('expires_in')
            authorizer_refresh_token = authorization_info.get('authorizer_refresh_token')
            # 更新令牌
            if auth_type in [1, '1']: # 公众号
                models.CustomerOfficialNumber.objects.filter(appid=authorizer_appid).update(
                    authorizer_access_token=authorizer_access_token,
                    authorizer_access_token_expires_in=expires_in,
                    authorizer_refresh_token=authorizer_refresh_token
                )
            else: # 小程序
                models.ClientApplet.objects.filter(appid=authorizer_appid).update(

                )

    # 获取（刷新）授权公众号或小程序的接口调用凭据（令牌）
    def refresh_exchange_calling_credentials(self, appid, token, auth_type):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token'
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "authorizer_appid":appid,
            "authorizer_refresh_token":token,
        }

        ret = requests.post(url, params=self.params, data=json.dumps(post_data))
        ret_json = ret.json()
        print('获取（刷新）授权公众号或小程序的接口调用凭据（令牌）refresh_exchange_calling_credentials----> ', ret_json)
        authorizer_access_token = ret_json.get('authorizer_access_token')
        expires_in = int(time.time()) + int(ret_json.get('expires_in'))
        authorizer_refresh_token = ret_json.get('authorizer_refresh_token')
        # 更新令牌
        if auth_type in [1, '1']:  # 公众号
            models.CustomerOfficialNumber.objects.filter(appid=appid).update(
                authorizer_access_token=authorizer_access_token,
                authorizer_access_token_expires_in=expires_in,
                authorizer_refresh_token=authorizer_refresh_token
            )
        else:  # 小程序
            models.ClientApplet.objects.filter(appid=appid).update(

            )

        return authorizer_access_token

    # 公众号/小程序 获取授权方的帐号基本信息
    def get_account_information(self, auth_type, appid):
        """
        :param auth_type: 授权方类型 1公众号 2小程序
        :param appid:    # 授权方APPID
        :return:
        """
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
        post_data = {
            "component_appid": self.tripartite_platform_appid,    # 第三方APPID
            "authorizer_appid": appid       # 授权方APPID
        }
        ret = requests.post(url, params=self.params, data=json.dumps(post_data))
        ret_json = ret.json()
        print('公众号/小程序 获取授权方的帐号基本信息get_account_information----> ', json.dumps(ret_json))



    # 获取授权方的选项设置信息
    def option_setting_information(self, option_name, appid):
        url = 'https://api.weixin.qq.com/cgi-bin/component/ api_get_authorizer_option'
        post_data = {
            "component_appid":self.tripartite_platform_appid,
            "authorizer_appid": appid,
            "option_name": option_name, # 选项名称
        }

        ret = requests.post(url, params=self.params, data=post_data)
        print('-option_setting_information-----------> ', ret.text)

    # 设置授权方的选项信息
    def set_authorizer_information(self, option_name, option_value, appid):
        url = 'https://api.weixin.qq.com/cgi-bin/component/ api_set_authorizer_option'
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "authorizer_appid": appid,
            "option_name": option_name, # 选项名称
            "option_value": option_value, # 选项值
        }
        ret = requests.post(url, params=self.params, data=post_data)

        print('set_authorizer_information------> ', ret.text)

    # 推送授权相关通知
    # def push_authorization_notification(self):



# 查询 授权的 公众号/小程序 调用凭证是否过期 (操作公众号 调用凭证 过期重新获取)
def QueryWhetherCallingCredentialExpired(appid, auth_type):
    """

    :param appid:  公众号/小程序 appid
    :param auth_type: 类型 (1公众号 2小程序) 区分查询数据库
    :return:
        authorizer_access_token : 调用 凭证
        flag： appid 是否存在
    """
    flag = False  # appid  是否存在
    response = {}
    if auth_type in [1, '1']:
        objs = models.CustomerOfficialNumber.objects.filter(appid=appid)
    else:
        objs = models.ClientApplet.objects.filter(appid=appid)
    if objs:
        flag = True
        obj = objs[0]
        authorizer_access_token_expires_in = obj.authorizer_access_token_expires_in
        authorizer_access_token = obj.authorizer_access_token
        authorizer_refresh_token = obj.authorizer_refresh_token
        time_stamp = authorizer_access_token_expires_in - int(time.time())
        if time_stamp <= 100: # 已经过期
            tripartite_platform_oper_obj = tripartite_platform_oper()
            authorizer_access_token = tripartite_platform_oper_obj.refresh_exchange_calling_credentials(
                appid,
                authorizer_refresh_token,
                auth_type
            )

        response['authorizer_access_token'] = authorizer_access_token
    response['flag'] = flag
    return response


