

from publicFunc.baidu_tripartite_platform_oper import tripartite_platform_oper as tripartite_platform, \
    QueryWhetherCallingCredentialExpired as CredentialExpired, GetTripartitePlatformInfo, baidu_tripartite_platform_key

from api.forms.baidu_tripartite_platform import AuthorizationForm, UploadAppletCode, SelectForm
from api import models
from publicFunc import Response, account
from django.http import JsonResponse, HttpResponse
from urllib.parse import unquote, quote
import time, json, datetime, requests



# 三方平台操作
@account.is_token(models.UserProfile)
def tripartite_platform_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    # 获取第三方平台access_token
    if oper_type == 'get_access_token':
        BaiduTripartitePlatformObjs = models.BaiduTripartitePlatformManagement.objects.filter(appid__isnull=False)
        ticket = BaiduTripartitePlatformObjs[0].ticket
        url = 'https://openapi.baidu.com/public/2.0/smartapp/auth/tp/token'
        params = {
            'client_id': baidu_tripartite_platform_key,
            'ticket': ticket
        }
        ret = requests.get(url, params=params)
        print('ret.json()--------> ', ret.json())
        ret_data = ret.json()
        access_token = ret_data.get('access_token')     # access_token
        expires_in = ret_data.get('expires_in')         # 有效时长
        scope = ret_data.get('scope')                   # 权限说明

        print(access_token, expires_in, scope)

    return JsonResponse(response.__dict__)



# 百度小程序后台 通知
def baidu_tongzhi(request):
    postdata = json.loads(request.body.decode(encoding='UTF-8'))
    Nonce = postdata.get('Nonce')
    TimeStamp = postdata.get('TimeStamp')
    Encrypt = postdata.get('Encrypt')
    MsgSignature = postdata.get('MsgSignature')

    get_ticket_url = 'http://a.yingxiaobao.org.cn/api/baidu-openssl-decrypt/decrypt'
    get_ticket_data = {
        'encrypted':Encrypt,
        'encodingAesKey':'sisciiZiJCC6PuGOtFWwmDnIHMsZyXmDnIHMsZyX123'
    }
    get_ticket_ret = requests.post(get_ticket_url, data=get_ticket_data)
    get_ticket_ret_json = get_ticket_ret.json()
    data = json.loads(get_ticket_ret_json.get('data'))
    Ticket = data.get('Ticket')
    FromUserName = data.get('FromUserName')
    CreateTime = data.get('CreateTime')
    MsgType = data.get('MsgType')
    Event = data.get('Event')

    objs = models.BaiduTripartitePlatformManagement.objects.filter(appid__isnull=False) # 更新ticket
    objs.update(
        ticket=Ticket,
    )

    return HttpResponse('success')










