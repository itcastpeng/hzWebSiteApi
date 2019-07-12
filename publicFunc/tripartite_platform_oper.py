from api import models
from publicFunc import Response, account
from django.http import JsonResponse
import requests, datetime, json, time



# 查询 授权的 公众号/小程序 调用凭证是否过期 (操作公众号 调用凭证 过期重新获取)
def QueryWhetherCallingCredentialExpired(appid, auth_type):
    """

    :param appid:  公众号/小程序 appid
    :param auth_type: 类型 (1公众号 2小程序) 区分查询数据库
    :return:
        authorizer_access_token : 调用 凭证
        flag： appid 是否存在
    """
    flag = False
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


# 获取开放平台信息
def GetTripartitePlatformInfo():
    tripartite_objs = models.TripartitePlatform.objects.filter(appid__isnull=False)
    flag = False
    response = {}
    if tripartite_objs:
        tripartite_obj = tripartite_objs[0]
        response['tripartite_appid'] = tripartite_obj.appid
        response['tripartite_appsecret'] = tripartite_obj.appsecret
        response['component_access_token'] = tripartite_obj.component_access_token
    else:
        flag = True
    response['flag'] = flag

    return response



# 三方平台操作
class tripartite_platform_oper():
    response = Response.ResponseObj()

    # ========================================公共函数==========================================

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
            expires_in = int(time.time()) + int(authorization_info.get('expires_in'))
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
                    authorizer_access_token=authorizer_access_token,
                    authorizer_access_token_expires_in=expires_in,
                    authorizer_refresh_token=authorizer_refresh_token
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
                authorizer_access_token=authorizer_access_token,
                authorizer_access_token_expires_in=expires_in,
                authorizer_refresh_token=authorizer_refresh_token
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
        ret_json = ret_json.get('authorizer_info')
        alias = ret_json.get('alias')                       # 授权方公众号所设置的微信号(公众号)
        miniprograminfo = ret_json.get('miniprograminfo')   # 可根据这个字段判断是否为小程序类型授权(小程序)
        network = ret_json.get('network')                   # 小程序已设置的各个服务器域名(小程序)

        func_info = ret_json.get('func_info')               # 公众号授权给开发者的权限集列表
        business_info = ret_json.get('business_info')       # 用以了解以下功能的开通状况（0代表未开通，1代表已开通)
        open_store = ret_json.get('open_store')             # 是否开通微信门店功能 open_scan:是否开通微信扫商品功能
        open_pay = ret_json.get('open_pay')                 # 是否开通微信支付功能 open_card:是否开通微信卡券功能
        open_shake = ret_json.get('open_shake')             # 是否开通微信摇一摇功能
        service_type_info = ret_json.get('service_type_info')# 小程序默认为0 公众号 0代表订阅号，1代表由历史老帐号升级后的订阅号，2代表服务号
        verify_type_info = ret_json.get('verify_type_info') # 授权方认证类型
        authorization_info = ret_json.get('authorization_info')     # 授权信息
        authorization_appid = ret_json.get('authorization_appid')   # 授权方appid
        """
                    verify_type_info
                    -1代表未认证，0代表微信认证  # 公共
                    公众号：
                        1代表新浪微博认证，2代表腾讯微博认证，
                        3代表已资质认证通过但还未通过名称认证，
                        4代表已资质认证通过、还未通过名称认证，但通过了新浪微博认证，
                        5代表已资质认证通过、还未通过名称认证，但通过了腾讯微博认证
                """

        nick_name = ret_json.get('nick_name')               # 授权方昵称
        head_img = ret_json.get('head_img')                 # 授权方头像
        user_name = ret_json.get('user_name')               # 授权方原始ID
        qrcode_url = ret_json.get('qrcode_url')             # 二维码图片的URL

        data = {
            'nick_name': nick_name,
            'head_img': head_img,
            'original_id': user_name,
            'qrcode_url': qrcode_url
        }

        if auth_type in [1, '1']:
            models.CustomerOfficialNumber.objects.filter(appid=appid).update(**data)

        else:
            models.ClientApplet.objects.filter(appid=appid).update(**data)

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

    #===================================================小程序函数============================

    # 上传小程序代码
    def xcx_update_code(self, appid, token):
        # ext_json 格式

        """
            {
                extAppid:"",   授权方APPID
                ext:{           # 自定义字段 可在小程序调用
                    "attr1":"value1",
                    "attr2":"value2",
                },
                extPages:{      # 页面配置
                    "index":{
                    },
                    "search/index":{
                    },
                },
                pages:["index","search/index"],
                "window":{
                },
                "networkTimeout":{
                },
                "tabBar":{
                },
            }

        """

        ext_json = {
                'extAppid':appid,   #授权方APPID
                'ext':{           # 自定义字段 可在小程序调用

                },
                'extPages':{      # 页面配置
                    "index":{
                    },
                    "search/index":{
                    },
                },
                'pages':["index","search/index"],
                "window":{
                },
                "networkTimeout":{
                },
                "tabBar":{
                },
            }

        url = 'https://api.weixin.qq.com/wxa/commit?access_token={}'.format(token)

        data = {
            # 代码库中的代码模板ID
            "template_id": '',
            "ext_json": ext_json,
            # 代码版本号(自定义)
            "user_version": '',
            # 代码描述(自定义)
            "user_desc": '',
        }
        ret = requests.post(url, data=data)
        print('ret.text------> ', ret.text)


    # 获取体验小程序二维码
    def xcx_get_experience_qr_code(self, token, path=None):
        url = 'https://api.weixin.qq.com/wxa/get_qrcode?access_token={}'.format(token)
        ret = requests.get(url)

        with open('1.png', 'wb') as f:
            f.write(ret.content)

    # 获取代码模板库中的所有小程序代码模板
    def xcx_get_code_template(self):
        url = 'https://api.weixin.qq.com/wxa/gettemplatelist?access_token={}'.format(self.token)
        ret = requests.post(url)
        print('获取代码模板库中的所有小程序代码模板=========--------> ', ret.text)
        errcode = ret.json().get('errcode')
        errmsg = ret.json().get('errmsg')
        template_list = ret.json().get('template_list')
        data = {
            'errcode':errcode,
            'template_list':template_list,
            'errmsg':errmsg,
        }
        return data
