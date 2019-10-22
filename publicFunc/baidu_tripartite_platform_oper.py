from api import models
from publicFunc import Response, account
import requests, json, time, os
from publicFunc.qiniu.auth import Auth
from publicFunc.redisOper import get_redis_obj


baidu_tripartite_platform_key = 'PCwOy1gDSz0cAixIMIli4hBIzHaz4Kib' # 第三方平台Key

# 查询 授权的 公众号/小程序 调用凭证是否过期 (操作公众号 调用凭证 过期重新获取)
def QueryWhetherCallingCredentialExpired(appid, auth_type):
    print('appid-----------------------> ', appid)
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

        response['id'] = obj.id
        response['authorizer_access_token'] = authorizer_access_token
    response['flag'] = flag
    return response



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





# 上传七牛云
def upload_qiniu(img_path, img_size):
    redis_obj = get_redis_obj()
    url = 'https://up-z1.qiniup.com/'
    upload_token = redis_obj.get('qiniu_upload_token')
    if not upload_token:
        qiniu_data_path = os.path.join(os.getcwd(), "publicFunc", "qiniu", "qiniu_data.json")
        with open(qiniu_data_path, "r", encoding="utf8") as f:
            data = json.loads(f.read())
            access_key = data.get('access_key')
            secret_key = data.get('secret_key')
            obj = Auth(access_key, secret_key)
            upload_token = obj.upload_token("xcx_wgw_zhangcong")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13'
    }
    with open(img_path, 'rb') as f:
        imgdata = f.read()

    files = {
        'file': imgdata
    }

    data = {
        'token': upload_token,
    }
    ret = requests.post(url, data=data, files=files, headers=headers)
    key = "http://qiniu.bjhzkq.com/{key}?imageView2/0/h/{img_size}".format(
        key=ret.json()["key"],
        img_size=img_size
    )
    if os.path.exists(img_path):
        os.remove(img_path)  # 删除本地图片
    return key





