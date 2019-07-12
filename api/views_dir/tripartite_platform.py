from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from api.forms.tripartite_platform import AuthorizationForm
from publicFunc.tripartite_platform_oper import tripartite_platform_oper as tripartite_platform, \
    QueryWhetherCallingCredentialExpired as CredentialExpired
from publicFunc.crypto_.WXBizMsgCrypt import WXBizMsgCrypt

from urllib.parse import unquote, quote
import time, json, datetime, xml.etree.cElementTree as ET, requests


@account.is_token(models.UserProfile)
def tripartite_platform_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 授权事件接收  （微信后台10分钟一次回调该接口 传递component_verify_ticket）
        if oper_type == 'tongzhi':
            signature = request.GET.get('signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            msg_signature = request.GET.get('msg_signature')
            user_id = request.GET.get('user_id')
            postdata = request.body.decode(encoding='UTF-8')

            xml_tree = ET.fromstring(postdata)
            Encrypt = xml_tree.find('Encrypt').text

            wx_obj = WXBizMsgCrypt('sisciiZiJCC6PuGOtFWwmDnIHMsZyX', 'sisciiZiJCC6PuGOtFWwmDnIHMsZyXmDnIHMsZyX123', 'wx1f63785f9acaab9c')
            ret, decryp_xml = wx_obj.DecryptMsg(Encrypt, msg_signature, timestamp, nonce)

            decryp_xml_tree = ET.fromstring(decryp_xml)
            ComponentVerifyTicket = decryp_xml_tree.find("ComponentVerifyTicket").text
            models.TripartitePlatform.objects.filter(
                appid=xml_tree.find('AppId').text
            ).update(
                component_verify_ticket=ComponentVerifyTicket,
                linshi=decryp_xml
            )


            return HttpResponse('success')


    else:

        # 查询三方平台需要数据===============================================================
        tripartite_objs = models.TripartitePlatform.objects.filter(appid__isnull=False)
        if tripartite_objs:
            tripartite_obj = tripartite_objs[0]
            tripartite_appid = tripartite_obj.appid
            tripartite_appsecret = tripartite_obj.appsecret
            component_access_token = tripartite_obj.component_access_token
            tripartite_platform_objs = tripartite_platform() # 实例化三方平台

            authorization_way = request.GET.get('authorization_way') # 授权方式 (1扫码, 2链接)
            authorization_type = request.GET.get('authorization_type') # 授权类型 (1公众号, 2小程序)
            appid = request.GET.get('appid')


            # 授权
            if oper_type == "authorization":
                form_data = {
                    'user_id': user_id,
                    'authorization_type': authorization_type,# 授权类型 (1公众号, 2小程序)
                    'authorization_way': authorization_way,# 授权方式 (1扫码, 2链接)
                    'appid': appid,
                }
                forms_obj = AuthorizationForm(form_data)
                if forms_obj.is_valid():
                    get_pre_auth_code = tripartite_platform_objs.get_pre_auth_code() # 获取预授权码
                    forms_data = forms_obj.cleaned_data

                    appid = forms_data.get('appid')
                    authorization_way = forms_data.get('authorization_way')
                    authorization_type = forms_data.get('authorization_type')


                    redirect_url = 'https://xcx.bjhzkq.com/api/tripartite_platform/authorize_callback?t=phone&appid={}&authorization_type={}&authorization_way={}'.format(
                        appid,
                        authorization_type,
                        authorization_way
                    )
                    redirect_url = quote(redirect_url)

                    if authorization_way in [2, '2']:  # 链接形式
                        wx_url = """
                            https://mp.weixin.qq.com/safe/bindcomponent?action=bindcomponent&no_scan=1&component_appid={component_appid}&pre_auth_code={pre_auth_code}&redirect_uri={redirect_uri}&auth_type={auth_type}&biz_appid={biz_appid}#wechat_redirect
                        """.format(
                            component_appid=tripartite_appid,       # 三方平台APPID
                            pre_auth_code=get_pre_auth_code,        # 预授权码
                            redirect_uri=redirect_url,              # 回调URL
                            auth_type=authorization_type,           # 授权账户类型
                            biz_appid=appid
                        )


                    else:  # 扫码接入
                        wx_url = """
                            https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid={}&pre_auth_code={}&redirect_uri={}&auth_type={}
                            """.format(
                            appid,
                            get_pre_auth_code,
                            redirect_url,
                            authorization_type
                        )

                    response.code = 200
                    response.msg = '生成授权链接成功'
                    response.data = {
                        'wx_url': wx_url.strip()
                    }

                else:
                    response.code = 301
                    response.msg = json.loads(forms_obj.errors.as_json())

            # 用户确认 同意授权 回调(用户点击授权 or 扫码授权后 跳转)
            elif oper_type == 'authorize_callback':
                auth_code = request.GET.get('auth_code')
                expires_in = request.GET.get('expires_in')

                if authorization_type in [1, '1']:
                    objs = models.CustomerOfficialNumber.objects.filter(
                        appid=appid,
                    )

                else:
                    objs = models.ClientApplet.objects.filter(
                        appid=appid,
                    )
                tripartite_platform_objs.exchange_calling_credentials(authorization_type, auth_code)
                objs.update(
                    auth_code=auth_code,
                    authorizer_access_token_expires_in=int(time.time()) + int(expires_in)
                )
                CredentialExpired(appid, authorization_type)    # 判断调用凭证是否过期
                tripartite_platform_objs.get_account_information(authorization_type, appid)

            # 获取授权方基本信息
            elif oper_type == 'get_authorized_party_info':
                auth_type = authorization_type
                CredentialExpired(appid, auth_type)
                tripartite_platform_obj = tripartite_platform()
                tripartite_platform_obj.get_account_information(auth_type, appid)

            else:
                response.code = 402
                response.msg = "请求异常"

        else:
            response.code = 301
            response.msg = '三方平台获取失败'

    return JsonResponse(response.__dict__)

