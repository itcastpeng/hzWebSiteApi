

from publicFunc.baidu_tripartite_platform_oper import tripartite_platform_oper as tripartite_platform, \
    baidu_tripartite_platform_key
from api.forms.baidu_tripartite_platform import AuthorizationForm, UploadAppletCode, SelectForm
from api import models
from publicFunc import Response, account
from django.http import JsonResponse, HttpResponse
import time, json, datetime, requests



# 三方平台操作
@account.is_token(models.UserProfile)
def tripartite_platform_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    tripartite_platform_oper = tripartite_platform() # 实例化公共三方

    # 获取预授权码pre_auth_code
    if oper_type == 'get_access_token':
        print('----------------------------------')
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










