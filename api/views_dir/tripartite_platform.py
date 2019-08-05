from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from api.forms.tripartite_platform import AuthorizationForm
from publicFunc.tripartite_platform_oper import tripartite_platform_oper as tripartite_platform, \
    QueryWhetherCallingCredentialExpired as CredentialExpired, GetTripartitePlatformInfo, encodingAESKey, \
    encoding_token, encoding_appid
from publicFunc.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
from urllib.parse import unquote, quote
from publicFunc.public import send_error_msg
from django.shortcuts import redirect
import time, json, datetime, xml.etree.cElementTree as ET, requests

# 三方平台操作
@account.is_token(models.UserProfile)
def tripartite_platform_oper(request, oper_type):
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
        credential_expired_data = CredentialExpired(appid, authorization_type)  # 判断调用凭证是否过期 (操作 GZH/XCX 前调用该函数)
        authorizer_access_token = credential_expired_data.get('authorizer_access_token')

        # 授权===========================公共
        if oper_type == "authorization":
            form_data = {
                'user_id': user_id,
                'authorization_type': authorization_type,  # 授权类型 (1公众号, 2小程序)
                'authorization_way': authorization_way,  # 授权方式 (1扫码, 2链接)
                'appid': appid,
            }
            forms_obj = AuthorizationForm(form_data)  # 创建 XCX/GZH appid
            if forms_obj.is_valid():
                get_pre_auth_code = tripartite_platform_objs.get_pre_auth_code()  # 获取预授权码
                forms_data = forms_obj.cleaned_data

                appid = forms_data.get('appid')
                authorization_way = forms_data.get('authorization_way')
                authorization_type = forms_data.get('authorization_type')

                redirect_url = 'https://xcx.bjhzkq.com/api/authorize_callback?appid={}&authorization_type={}&authorization_way={}'.format(
                    appid,
                    authorization_type,
                    authorization_way
                )
                # redirect_url = 'https://xcx.bjhzkq.com/thirdTerrace/thirdTerrace_index'
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
                        tripartite_appid,
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


        # 绑定微信用户为小程序体验者===================小程序
        elif oper_type == 'bind_weChat_user_small_program_experiencer':
            wechatid = request.POST.get('wechatid') # 微信号
            data = tripartite_platform_objs.bind_weChat_user_small_program_experiencer(
                authorizer_access_token, wechatid
            )
            response.code = data.get('errcode')
            response.msg = data.get('errmsg')
            response.data = data.get('userstr')

        # 解除绑定小程序体验者
        elif oper_type == 'the_experiencer_unbound_applet':
            wechatid = request.POST.get('wechatid')  # 微信号
            data = tripartite_platform_objs.the_experiencer_unbound_applet(
                authorizer_access_token, wechatid
            )
            response.code = 200
            response.msg = '解除绑定体验者成功'

        # 设置小程序隐私设置（是否可被搜索） # 1表示不可搜索，0表示可搜索
        elif oper_type == 'set_applet_privacy_Settings':
            status = request.POST.get('status')
            data = tripartite_platform_objs.set_applet_privacy_Settings(
                authorizer_access_token,
                status
            )
            response.data = data.get('members')
            response.code = data.get('errcode')
            response.msg = data.get('errmsg')



    else:
        appid = request.GET.get('appid') # 传递的APPID
        if oper_type != 'authorize_callback':
            credential_expired_data = CredentialExpired(appid, authorization_type)  # 判断调用凭证是否过期 (操作 GZH/XCX 前调用该函数)
            authorizer_access_token = credential_expired_data.get('authorizer_access_token')

            # 获取授权方基本信息(手动触发)
            if oper_type == 'get_authorized_party_info':
                tripartite_platform_objs.get_account_information(
                    authorization_type, appid
                )
                response.code = 200
                response.msg = '获取信息完成'

            # 上传小程序代码===========================小程序
            elif oper_type == 'upload_applet_code':
                template_id = request.GET.get('template_id')  # 代码模板ID
                user_version = request.GET.get('user_version')  # 代码版本号
                user_desc = request.GET.get('user_desc')  # 代码描述
                data = {
                    'appid': appid,
                    'token': authorizer_access_token,
                    'template_id': template_id,
                    'user_version': user_version,
                    'user_desc': user_desc
                }
                tripartite_platform_objs.xcx_update_code(data)
                response.code = 200

            # 获取小程序体验二维码
            elif oper_type == 'get_experience_qr_code':
                path = tripartite_platform_objs.xcx_get_experience_qr_code(authorizer_access_token)
                response.code = 200
                response.data = path

            # 获取代码模板库中的所有小程序代码模板
            elif oper_type == 'get_code':
                response_data = tripartite_platform_objs.xcx_get_code_template()

                response.code = 301
                if response_data.get('errcode') in [0, '0']:
                    template_list = response_data.get('template_list')
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = template_list

                else:
                    response.msg = response_data.get('errmsg')

            # 将草稿箱的草稿选为小程序代码模版
            elif oper_type == 'select_draft_applet_code_template':
                draft_id = request.GET.get('draft_id')  # 草稿ID
                tripartite_platform_objs.xcx_select_draft_applet_code_template(draft_id)
                response.code = 200

            # 获取小程序体验者列表
            elif oper_type == 'Get_list_experiencers':
                data = tripartite_platform_objs.Get_list_experiencers(
                    authorizer_access_token
                )
                response.data = data.get('members')
                response.code = data.get('errcode')
                response.msg = data.get('errmsg')

            # 获取小程序的第三方提交代码的页面配置
            elif oper_type == 'get_code_page_configuration':
                data = tripartite_platform_objs.get_code_page_configuration(
                    authorizer_access_token
                )
                response.code = 200
                response.data = data

            # 查询某个指定版本的审核状态
            elif oper_type == 'query_specified_version_code_audit':
                auditid = request.GET.get('auditid')
                tripartite_platform_objs.query_specified_version_code_audit(
                    authorizer_access_token,
                    auditid
                )
                response.code = 200


            # 查询最新一次提交的审核状态
            elif oper_type == 'check_status_most_recent_submission':
                auditid = request.GET.get('auditid')
                ret_json = tripartite_platform_objs.check_status_most_recent_submission(
                    authorizer_access_token,
                    auditid
                )
                response.code = 200
                response.msg = '查询成功'
                response.data = ret_json

            # 获取草稿箱内的所有临时代码草稿
            elif oper_type == 'get_all_temporary_code_drafts':
                data = tripartite_platform_objs.xcx_get_all_temporary_code_drafts()
                response.code = 200
                response.msg = '查询成功'
                response.data = data

            # 将第三方提交的代码包提交审核
            elif oper_type == 'code_package_submitted_review':
                ret_json = tripartite_platform_objs.code_package_submitted_review(
                    authorizer_access_token
                )
                auditid = ret_json.get('auditid')
                response.code = 200
                response.msg = '提交成功'
                response.data = ret_json

            # 查询小程序当前隐私设置（是否可被搜索）
            elif oper_type == 'query_current_privacy_settings':
                data = tripartite_platform_objs.query_current_privacy_settings(
                    authorizer_access_token
                )
                response.code = 200
                response.msg = '查询成功'
                response.data = data
                response.note = {
                    "status": '1表示不可搜索，0表示可搜索',
                    "errcode": '0',
                    "errmsg": "ok",
                }


        # authorize_callback
        else:
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

            tripartite_platform_objs.get_account_information(authorization_type, appid) # 获取基本信息入库
            objs.update(is_authorization=1) # 授权完成


    return JsonResponse(response.__dict__)


#
@account.is_token(models.UserProfile)
def tripartite_platform_admin(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == "POST":
        if oper_type == '':
            pass

    else:

        # 查询个人XCX/GZH
        if oper_type == 'select_xcx_gzh_info':
            applet_objs = models.ClientApplet.objects.filter(user_id=user_id)
            offici_objs = models.CustomerOfficialNumber.objects.filter(user_id=user_id)

            result_data = {}
            applet_flag = False
            offici_flag = False
            flag = False
            if applet_objs:
                flag = True
                applet_flag = True
                obj = applet_objs[0]

            if offici_objs:
                flag = True
                offici_flag = True
                obj = offici_objs[0]

            if flag:
                result_data['is_authorization']=obj.is_authorization
                result_data['nick_name']=obj.nick_name
                result_data['head_img']=obj.head_img
                result_data['qrcode_url']=obj.qrcode_url
                result_data['appid']=obj.appid
                result_data['create_datetime']=obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S')

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'applet_flag': applet_flag,
                'offici_flag': offici_flag,
                'result_data': result_data,
            }
            response.note = {
                'applet_flag': '是否有小程序',
                'offici_flag': '是否有公众号',
                'result_data': {
                    'is_authorization':'是否完成授权',
                    'nick_name':'名称',
                    'head_img':'头像',
                    'qrcode_url':'二维码',
                    'appid':'appid',
                    'create_datetime':'创建时间',
                },
            }

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)


# 授权事件接收  （微信后台10分钟一次回调该接口 传递component_verify_ticket）
def tongzhi(request):
    try:
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
            wx_obj = WXBizMsgCrypt(encoding_token, encodingAESKey, encoding_appid)
            ret, decryp_xml = wx_obj.DecryptMsg(Encrypt, msg_signature, timestamp, nonce)
            decryp_xml_tree = ET.fromstring(decryp_xml)
            ComponentVerifyTicket = decryp_xml_tree.find("ComponentVerifyTicket").text
            objs.update(
                component_verify_ticket=ComponentVerifyTicket
            )
    except Exception as e:
        content = '{}三方平台后台回调异常:{}'.format(
            datetime.datetime.today(), e
        )
        send_error_msg(content, 5)

    return HttpResponse('success')

# 用户确认 同意授权 回调(用户点击授权 or 扫码授权后 跳转)
def authorize_callback(request):
    """
                   auth_code   : GZH/XCX 授权码
                   expires_in  : GZH/XCX 授权码过期时间
               """
    auth_code = request.GET.get('auth_code')
    expires_in = request.GET.get('expires_in')
    authorization_type = request.GET.get('authorization_type')  # 授权类型 (1公众号, 2小程序)
    appid = request.GET.get('appid')  # 授权类型 (1公众号, 2小程序)
    if authorization_type in [1, '1']:
        objs = models.CustomerOfficialNumber.objects.filter(
            appid=appid,
        )

    else:
        objs = models.ClientApplet.objects.filter(
            appid=appid,
        )

    # 使用授权码 获取调用 GZH/XCX 凭证
    tripartite_platform_objs = tripartite_platform()  # 实例化三方平台
    tripartite_platform_objs.exchange_calling_credentials(authorization_type, auth_code)

    # ==== 更改 GZH/XCX 授权码 和 过期时间
    objs.update(
        auth_code=auth_code,
        auth_code_expires_in=int(time.time()) + int(expires_in)
    )

    tripartite_platform_objs.get_account_information(authorization_type, appid)  # 获取基本信息入库
    objs.update(is_authorization=1)  # 授权完成

    return redirect('https://xcx.bjhzkq.com/thirdTerrace/thirdTerrace_index')
    # return HttpResponse('success')



















