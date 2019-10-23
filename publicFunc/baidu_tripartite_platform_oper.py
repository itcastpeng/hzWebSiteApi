from api import models
from publicFunc import Response, account
import requests, json, time, os
from publicFunc.qiniu.auth import Auth
from publicFunc.redisOper import get_redis_obj


baidu_tripartite_platform_key = 'PCwOy1gDSz0cAixIMIli4hBIzHaz4Kib' # 第三方平台Key




# 三方平台操作
class tripartite_platform_oper():
    response = Response.ResponseObj()

    # ========================================公共函数==========================================

    def __init__(self):
        BaiduTripartitePlatformObjs = models.BaiduTripartitePlatformManagement.objects.filter(id=1)
        BaiduTripartitePlatformObj = BaiduTripartitePlatformObjs[0]
        ticket = BaiduTripartitePlatformObj.ticket
        access_token_time = BaiduTripartitePlatformObj.access_token_time
        pre_auth_code_time = BaiduTripartitePlatformObj.pre_auth_code_time
        self.access_token = BaiduTripartitePlatformObj.access_token

        if int(access_token_time) - int(time.time()) <= 600: # token还有10分钟过期

            url = 'https://openapi.baidu.com/public/2.0/smartapp/auth/tp/token'
            params = {
                'client_id': baidu_tripartite_platform_key,
                'ticket': ticket
            }
            ret = requests.get(url, params=params)
            ret_data = ret.json().get('data')
            self.access_token = ret_data.get('access_token')  # access_token
            access_token_time = int(time.time()) + int(ret_data.get('expires_in'))  # 有效时长
            scope = ret_data.get('scope')  # 权限说明

            BaiduTripartitePlatformObjs.update(
                access_token=self.access_token,
                access_token_time=access_token_time
            )

        if int(pre_auth_code_time) - int(time.time()) <= 60: # 预授权码还有1分钟到期
            url = 'https://openapi.baidu.com/rest/2.0/smartapp/tp/createpreauthcode'
            params = {
                'access_token': self.access_token
            }
            ret = requests.get(url, params=params)
            ret_data = ret.json().get('data')
            self.pre_auth_code = ret_data.get('pre_auth_code')  # access_token
            pre_auth_code_time = int(time.time()) + int(ret_data.get('expires_in'))  # 有效时长

            BaiduTripartitePlatformObjs.update(
                pre_auth_code=self.pre_auth_code,
                pre_auth_code_time=pre_auth_code_time
            )

    # 使用 授权码 调用 小程序凭证
    def get_get_small_program_authorization_credentials(self, auth_code):
        url = 'https://openapi.baidu.com/rest/2.0/oauth/token'
        params = {
            'access_token': self.access_token,
            'code': auth_code,
            'grant_type': 'app_to_tp_authorization_code',
        }
        ret = requests.get(url, params=params)
        ret_json = ret.json().get('data')
        access_token = ret_json.get('access_token')

        url = 'https://openapi.baidu.com/rest/2.0/smartapp/app/info?access_token={}'.format(access_token)
        ret = requests.get(url)
        ret_json = ret.json().get('data')

        app_id = ret_json.get('app_id')
        small_data = {
            'appid':app_id,
            'access_token':access_token,
            'refresh_token': ret_json.get('refresh_token'),
            'access_token_time': ret_json.get('expires_in'),
            'app_name': ret_json.get('app_name')  ,     # 小程序的名称
            'app_key': ret_json.get('app_key')  ,       # 小程序的key
            'app_desc': ret_json.get('app_desc')  ,     # 小程序的介绍内容
            'photo_addr': ret_json.get('photo_addr')  , # 小程序图标
        }

        # qualification = ret_json.get('qualification')   # 小程序账号对应的主体信息
        # qualification_name = qualification.name     # 主体名称

        objs = models.BaiduSmallProgramManagement.objects.filter(
            appid=app_id
        )
        if objs:
            objs.update(**small_data)
        else:
            models.BaiduSmallProgramManagement.objects.create(**small_data)




















