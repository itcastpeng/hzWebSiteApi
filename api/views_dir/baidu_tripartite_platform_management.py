

from publicFunc.baidu_tripartite_platform_oper import tripartite_platform_oper as tripartite_platform, \
    baidu_tripartite_platform_key
from api.forms.baidu_tripartite_platform import AuthorizationForm, UploadAppletCode, SelectForm
from api import models
from publicFunc import Response, account
from django.http import JsonResponse, HttpResponse
from urllib.parse import unquote, quote
from django.shortcuts import redirect
import time, json, datetime, requests

# 三方平台操作
@account.is_token(models.UserProfile)
def tripartite_platform_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    tripartite_platform_oper = tripartite_platform() # 实例化公共三方

    BaiduTripartitePlatformObjs = models.BaiduTripartitePlatformManagement.objects.filter(id=1)
    BaiduTripartitePlatformObj = BaiduTripartitePlatformObjs[0]

    # 引导小程序管理员授权
    if oper_type == 'boot_small_program_administrator_authorization':
        redirect_url = 'https://xcx.bjhzkq.com/api/baidu_authorize_callback?user_id={}'.format(
            user_id
        )
        redirect_url = quote(redirect_url)

        url = 'https://smartprogram.baidu.com/mappconsole/tp/authorization?client_id={}&redirect_uri={}&pre_auth_code={}'.format(
            baidu_tripartite_platform_key,
            redirect_url,
            BaiduTripartitePlatformObj.pre_auth_code
        )
        response.code = 200
        response.msg = '生成链接成功'
        response.data = {
            'url': url.strip()
        }

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

    if Event == 'UNAUTHORIZED': # 取消授权通知
        pass

    elif Event == 'AUTHORIZED': # 授权成功通知
        pass

    elif Event == 'UPDATE_AUTHORIZED': # 授权更新通知
        pass
    else:
        objs = models.BaiduTripartitePlatformManagement.objects.filter(id=1) # 更新ticket
        objs.update(
            ticket=Ticket,
        )

    return HttpResponse('success')




# 用户确认 同意授权 回调(用户点击授权 or 扫码授权后 跳转)
def authorize_callback(request):
    """
                   authorization_code   : GZH/XCX 授权码
                   expires_in  : GZH/XCX 授权码过期时间
               """
    authorization_code = request.GET.get('authorization_code')
    expires_in = request.GET.get('expires_in')

    user_id = request.GET.get('user_id')
    template_id = request.GET.get('template_id')

    print('=================================================授权-------------> ', authorization_code, expires_in)



    return redirect('https://xcx.bjhzkq.com')
    # return redirect('https://xcx.bjhzkq.com/thirdTerrace/smallRoutine?id={}'.format(template_id))









