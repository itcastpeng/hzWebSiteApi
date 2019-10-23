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
        BaiduTripartitePlatformObjs = models.BaiduTripartitePlatformManagement.objects.filter(appid__isnull=False)
        BaiduTripartitePlatformObj = BaiduTripartitePlatformObjs[0]
        ticket = BaiduTripartitePlatformObj.ticket
        access_token_time = BaiduTripartitePlatformObj.access_token_time
        access_token = BaiduTripartitePlatformObj.access_token
        pre_auth_code_time = BaiduTripartitePlatformObj.pre_auth_code_time
        pre_auth_code = BaiduTripartitePlatformObj.pre_auth_code

        if int(access_token_time) - int(time.time()) <= 600: # token还有10分钟过期

            url = 'https://openapi.baidu.com/public/2.0/smartapp/auth/tp/token'
            params = {
                'client_id': baidu_tripartite_platform_key,
                'ticket': ticket
            }
            ret = requests.get(url, params=params)
            ret_data = ret.json().get('data')
            access_token = ret_data.get('access_token')  # access_token
            access_token_time = int(time.time()) + int(ret_data.get('expires_in'))  # 有效时长
            scope = ret_data.get('scope')  # 权限说明

            BaiduTripartitePlatformObjs.update(
                access_token=access_token,
                access_token_time=access_token_time
            )

        if int(pre_auth_code_time) - int(time.time()) <= 60: # 预授权码还有1分钟到期
            url = 'https://openapi.baidu.com/rest/2.0/smartapp/tp/createpreauthcode'
            params = {
                'access_token': access_token
            }
            ret = requests.get(url, params=params)
            ret_data = ret.json().get('data')
            pre_auth_code = ret_data.get('pre_auth_code')  # access_token
            pre_auth_code_time = int(time.time()) + int(ret_data.get('expires_in'))  # 有效时长

            BaiduTripartitePlatformObjs.update(
                pre_auth_code=pre_auth_code,
                pre_auth_code_time=pre_auth_code_time
            )









