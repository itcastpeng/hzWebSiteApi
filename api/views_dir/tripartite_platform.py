from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from api.forms.tripartite_platform import AuthorizationForm
from publicFunc.tripartite_platform_oper import tripartite_platform_oper as tripartite_platform, \
    QueryWhetherCallingCredentialExpired as CredentialExpired, GetTripartitePlatformInfo
from publicFunc.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
from urllib.parse import unquote, quote
import time, json, datetime, xml.etree.cElementTree as ET, requests

# 三方平台操作
@account.is_token(models.UserProfile)
def tripartite_platform_oper(request, oper_type):
    """

    :param request:
    :param oper_type:
    :return:
    """
    response = Response.ResponseObj()
    tripartite_platform_objs = tripartite_platform()  # 实例化三方平台
    tripartite_platform_info = GetTripartitePlatformInfo() # 获取三方平台信息

    user_id = request.GET.get('user_id')
    authorization_way = request.GET.get('authorization_way')  # 授权方式 (1扫码, 2链接)
    authorization_type = request.GET.get('authorization_type')  # 授权类型 (1公众号, 2小程序)

    tripartite_appid = tripartite_platform_info.get('tripartite_appid') # 三方APPID
    tripartite_appsecret = tripartite_platform_info.get('tripartite_appsecret') #
    component_access_token = tripartite_platform_info.get('component_access_token') #

    if request.method == "POST":
        appid = request.POST.get('appid')


        # =========================公共=============================================
        # 授权事件接收  （微信后台10分钟一次回调该接口 传递component_verify_ticket）
        if oper_type == 'tongzhi':
            signature = request.GET.get('signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            msg_signature = request.GET.get('msg_signature')
            user_id = request.GET.get('user_id')
            postdata = request.body.decode(encoding='UTF-8')

            xml_tree = ET.fromstring(postdata)
            appid = xml_tree.find('AppId').text
            Encrypt = xml_tree.find('Encrypt').text
            objs = models.TripartitePlatform.objects.filter(
                appid=appid
            )
            if objs:
                objs.update(linshi=postdata)
                wx_obj = WXBizMsgCrypt('sisciiZiJCC6PuGOtFWwmDnIHMsZyX', 'sisciiZiJCC6PuGOtFWwmDnIHMsZyXmDnIHMsZyX123', 'wx1f63785f9acaab9c')
                ret, decryp_xml = wx_obj.DecryptMsg(Encrypt, msg_signature, timestamp, nonce)
                decryp_xml_tree = ET.fromstring(decryp_xml)
                ComponentVerifyTicket = decryp_xml_tree.find("ComponentVerifyTicket").text
                objs.update(
                    component_verify_ticket=ComponentVerifyTicket
                )


            return HttpResponse('success')

        # 授权
        elif oper_type == "authorization":
            form_data = {
                'user_id': user_id,
                'authorization_type': authorization_type,  # 授权类型 (1公众号, 2小程序)
                'authorization_way': authorization_way,  # 授权方式 (1扫码, 2链接)
                'appid': appid,
            }
            forms_obj = AuthorizationForm(form_data)
            if forms_obj.is_valid():
                get_pre_auth_code = tripartite_platform_objs.get_pre_auth_code()  # 获取预授权码
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
                        component_appid=tripartite_appid,  # 三方平台APPID
                        pre_auth_code=get_pre_auth_code,  # 预授权码
                        redirect_uri=redirect_url,  # 回调URL
                        auth_type=authorization_type,  # 授权账户类型
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


        # ============================小程序======================================
        # 上传小程序代码
        elif oper_type == 'upload_applet_code':
            pass

        # 绑定微信用户为小程序体验者
        elif oper_type == '':
            wechatid = request.POST.get('wechatid') # 微信号

        # 解除绑定小程序体验者
        elif oper_type == '':
            pass


    else:
        appid = request.GET.get('appid') # 传递的APPID


        # =============================公共=================================
        # 用户确认 同意授权 回调(用户点击授权 or 扫码授权后 跳转)
        if oper_type == 'authorize_callback':
            """
                auth_code   : GZH/XCX 授权码
                expires_in  : GZH/XCX 授权码过期时间
            """
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

            # 使用授权码 获取调用 GZH/XCX 凭证
            tripartite_platform_objs.exchange_calling_credentials(authorization_type, auth_code)

            # ==== 更改 GZH/XCX 授权码 和 过期时间
            objs.update(
                auth_code=auth_code,
                auth_code_expires_in=int(time.time()) + int(expires_in)
            )
            CredentialExpired(appid, authorization_type)    # 判断调用凭证是否过期 (操作 GZH/XCX 前调用该函数)
            tripartite_platform_objs.get_account_information(authorization_type, appid) # 获取基本信息入库
            objs.update(is_authorization=1) # 授权完成

        # 获取授权方基本信息(手动触发)
        elif oper_type == 'get_authorized_party_info':
            CredentialExpired(appid, authorization_type)
            tripartite_platform_objs.get_account_information(
                authorization_type, appid
            )
            response.code = 200
            response.msg = '获取信息完成'



        # ============================小程序====================================
        # 获取小程序体验二维码
        elif oper_type == 'get_experience_qr_code':
            # 判断调用凭证是否过期
            data = CredentialExpired(appid, authorization_type)
            authorizer_access_token = data.get('authorizer_access_token')
            # tripartite_platform_objs.xcx_get_experience_qr_code(authorizer_access_token)

        # 获取代码模板库中的所有小程序代码模板
        elif oper_type == 'get_code':
            data = CredentialExpired(appid, authorization_type)
            response_data = tripartite_platform_objs.xcx_get_code_template()

            response.code = 301
            if response_data.get('errcode') in [0, '0']:
                template_list = response_data.get('template_list')
                response.code = 200
                response.msg = '查询成功'
                response.data = template_list

            else:
                response.msg = response_data.get('errmsg')

        # 获取小程序体验者列表
        elif oper_type == '':
            pass

        # 查询提交审核的小程序代码
        elif oper_type == '':
            pass

        # 获取草稿箱内的所有临时代码草稿
        elif oper_type == 'get_all_temporary_code_drafts':
            data = CredentialExpired(appid, authorization_type)
            tripartite_platform_objs.get_all_temporary_code_drafts()


        else:
            response.code = 402
            response.msg = "请求异常"


    return JsonResponse(response.__dict__)

