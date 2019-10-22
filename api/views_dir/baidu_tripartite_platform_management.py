

from publicFunc.baidu_tripartite_platform_oper import tripartite_platform_oper as tripartite_platform, \
    QueryWhetherCallingCredentialExpired as CredentialExpired, GetTripartitePlatformInfo, encodingAESKey

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
    if oper_type == '':
        url = 'https://openapi.baidu.com/public/2.0/smartapp/auth/tp/token?client_id=OdxUiUVpVxH2Ai7G02cIjXGnnnMEUntD&ticket=8e329bc7e5fc432740d2e7e76a39c0e3'


    return JsonResponse(response.__dict__)




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
    print('vget_ticket_ret------> ', get_ticket_ret.json())
    get_ticket_ret_json = get_ticket_ret.json()
    data = get_ticket_ret_json.get('data')
    Ticket = data.get('Ticket')
    FromUserName = data.get('FromUserName')
    CreateTime = data.get('CreateTime')
    MsgType = data.get('MsgType')
    Event = data.get('Event')

    print('Ticket--------> ', Ticket)
    print('FromUserName----------> ', FromUserName)
    print('CreateTime --------> ', CreateTime)
    print('MsgType---------> ', MsgType)
    print('Event------> ', Event)
    # objs = models.BaiduTripartitePlatformManagement.objects.filter(appid__isnull=False)
    # objs.update(
    #
    # )


    return HttpResponse('success')










