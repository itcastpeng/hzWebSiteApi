

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
    template_id = request.POST.get('template_id')  # 模板ID

    tripartite_platform_objs = tripartite_platform()  # 实例化三方平台
    tripartite_platform_info = GetTripartitePlatformInfo() # 获取三方平台信息

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

                # redirect_url = 'https://xcx.bjhzkq.com/api/authorize_callback?appid={}&authorization_type={}&authorization_way={}&template_id={}'.format(
                redirect_url = 'https://xcx.bjhzkq.com/api/authorize_callback?user_id={}&authorization_type={}&authorization_way={}&template_id={}'.format(
                    user_id,
                    authorization_type,
                    authorization_way,
                    template_id
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
                if authorization_type in [1, '1']:
                    models.ClientApplet.objects.filter(appid=appid).delete()
                else:
                    models.CustomerOfficialNumber.objects.filter(appid=appid).delete()
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 上传小程序代码===========================小程序
        # elif oper_type == 'upload_applet_code':
        #     if credential_expired_data.get('flag'):
        #         form_data = {
        #             'user_version': request.POST.get('user_version', '1.0.1'),  # 代码版本号
        #             'user_desc': request.POST.get('user_desc'),  # 代码描述
        #         }
        #
        #         form_obj = UploadAppletCode(form_data)
        #         if form_obj.is_valid():
        #             user_version = form_obj.cleaned_data.get('user_version')
        #             user_desc = form_obj.cleaned_data.get('user_desc')
        #
        #             obj = models.ClientApplet.objects.get(id=credential_expired_data.get('id'))
        #             if obj.template:
        #                 user_obj = models.UserProfile.objects.get(id=user_id)
        #                 data = {
        #                     'appid': appid,
        #                     'token': authorizer_access_token,
        #                     'user_version': user_version,
        #                     'user_desc': user_desc,
        #                     'user_id': user_id,
        #                     'user_token': user_obj.token,
        #                     'id': obj.template_id,
        #                 }
        #                 tripartite_platform_objs.xcx_update_code(data)
        #
        #                 code = 200
        #                 msg = '上传代码成功'
        #
        #             else:
        #                 code = 301
        #                 msg = '请先绑定模板'
        #         else:
        #             code = 301
        #             msg = json.loads(form_obj.errors.as_json())
        #
        #     else:
        #         code = 301
        #         msg = '小程序异常'
        #         if authorization_type in [1, '1']:
        #             msg = '公众号异常'
        #
        #     response.code = code
        #     response.msg = msg

        # 绑定微信用户为小程序体验者===================小程序
        elif oper_type == 'bind_weChat_user_small_program_experiencer':
            wechatid = request.POST.get('wechatid') # 微信号
            data = tripartite_platform_objs.bind_weChat_user_small_program_experiencer(
                authorizer_access_token, wechatid
            )
            code = 301
            userstr = data.get('userstr')
            if data.get('errcode') in [0, '0']:
                code = 200
                objs = models.AppletExperiencerList.objects.filter(
                    applet__appid=appid,
                    userstr=userstr
                )
                if not objs:
                    models.AppletExperiencerList.objects.create(
                        applet_id=credential_expired_data.get('id'),
                        userstr=userstr,
                        wechat_id=wechatid
                    )
                else:
                    objs.update(is_delete=1)

            response.code = code
            response.msg = data.get('errmsg')
            response.data = userstr

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
            code = 301
            if data.get('errcode') in [0, '0']:
                code = 200
            response.code = code
            response.data = data.get('members')
            response.msg = data.get('errmsg')

        # 将第三方提交的代码包提交审核
        elif oper_type == 'code_package_submitted_review':
            ret_json = tripartite_platform_objs.code_package_submitted_review(
                authorizer_access_token
            )
            response.code = 200
            response.msg = '提交成功'
            response.data = ret_json

            obj = models.ClientApplet.objects.get(id=credential_expired_data.get('id'))

            # 记录上传的版本 模板
            page_data = ''
            page_objs = models.Page.objects.filter(page_group__template_id=obj.template_id)
            if page_objs:
                page_data = page_objs[0].data
            models.AppletCodeVersion.objects.create(
                applet_id=obj.id,
                page_data=page_data,
                navigation_data=obj.template.tab_bar_data,
                user_version='1.10',
                user_desc='',
                auditid=ret_json.get('auditid')
            )

        # 将草稿箱的草稿选为小程序代码模版
        elif oper_type == 'select_draft_applet_code_template':
            draft_id = request.POST.get('draft_id')  # 草稿ID
            data = tripartite_platform_objs.xcx_select_draft_applet_code_template(draft_id)
            code = 301
            if data.get('errcode') in [0, '0']:
                code = 200
            response.code = code
            response.msg = data.get('errmsg')

        # 删除指定小程序代码模版
        elif oper_type == 'deletes_specified_applet_code_template':
            applet_template_id = request.POST.get('applet_template_id')
            data = tripartite_platform_objs.deletes_specified_applet_code_template(applet_template_id)
            errmsg = data.get('errmsg')
            code = 301
            if data.get('errcode') in [0, '0']:
                code = 200
                errmsg = '删除成功'

            response.code = code
            response.msg = errmsg

        # 发布小程序
        elif oper_type == 'publish_approved_applets':
            data = tripartite_platform_objs.publish_approved_applets(authorizer_access_token)
            code = 301
            errmsg = data.get('errmsg')
            if data.get('errcode') in [0, '0']:
                code = 200
                errmsg = '发布完成'

            response.code = code
            response.msg = errmsg

        # 删除小程序
        elif oper_type == 'delete_applet':
            data = tripartite_platform_objs.delete_applet(appid, authorizer_access_token)
            errcode = data.get('errcode')
            errmsg = data.get('errmsg')
            code = 301
            msg = '解绑失败: {}'.format(errmsg)
            if errcode in [0, '0']:
                code = 200
                msg = '解绑成功'
            response.code = code
            response.msg = msg

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

            # 获取小程序体验二维码
            elif oper_type == 'get_experience_qr_code':
                user_obj = models.UserProfile.objects.get(id=user_id)
                user_desc = request.POST.get('user_desc')
                response_data = ''
                data_dict = {
                    'user_desc': user_desc,
                    'user_id': user_id,
                    'user_token': user_obj.token,
                }
                get_experience_qr_code_template_id = ''
                if not credential_expired_data.get('flag'): #
                    appid = 'wx700c48cb72073e61'
                    get_experience_qr_code_template_id = request.GET.get('template_id')
                    credential_expired_data = CredentialExpired(appid, 2)  # 判断调用凭证是否过期 (操作 GZH/XCX 前调用该函数)
                    authorizer_access_token = credential_expired_data.get('authorizer_access_token')
                    data_dict['id'] = get_experience_qr_code_template_id
                    data_dict['appid'] = appid
                    data_dict['token'] = authorizer_access_token
                    tripartite_platform_objs.xcx_update_code(data_dict)
                    data = tripartite_platform_objs.xcx_get_experience_qr_code(authorizer_access_token)

                    code = 200
                    msg = '查询成功'
                    response_data = data.get('path')


                else:
                    obj = models.ClientApplet.objects.get(id=credential_expired_data.get('id'))
                    if obj.template:
                        get_experience_qr_code_template_id = obj.template_id
                        data_dict = {
                            'appid': appid,
                            'token': authorizer_access_token,
                            'user_desc': user_desc,
                            'user_id': user_id,
                            'user_token': user_obj.token,
                            'id': get_experience_qr_code_template_id,
                        }
                        tripartite_platform_objs.xcx_update_code(data_dict)
                        data = tripartite_platform_objs.xcx_get_experience_qr_code(authorizer_access_token)

                        code = 200
                        msg = '查询成功'
                        response_data = data.get('path')

                    else:
                        code = 301
                        msg = '请先绑定模板'

                template_obj = models.Template.objects.get(id=get_experience_qr_code_template_id)
                data = {
                    'xcx_code': response_data,
                    'gzh_code': template_obj.qrcode
                }
                response.code = code
                response.msg = msg
                response.data = data


            # 获取代码模板库中的所有小程序代码模板
            elif oper_type == 'get_code':
                response_data = tripartite_platform_objs.xcx_get_code_template()

                response.code = 301
                if response_data.get('errcode') in [0, '0']:
                    template_list = response_data.get('template_list')
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = sorted(template_list, key=lambda x: x['create_time'], reverse=True)
                else:
                    response.msg = response_data.get('errmsg')

            # 获取小程序体验者列表
            elif oper_type == 'Get_list_experiencers':
                data = tripartite_platform_objs.Get_list_experiencers(
                    authorizer_access_token
                )
                code = 301
                members = []
                if data.get('errcode') in [0, '0']:
                    code = 200
                    for member_obj in data.get('members'):
                        userstr = member_obj.get('userstr')
                        objs = models.AppletExperiencerList.objects.filter(
                            userstr=userstr,
                            applet__appid=appid
                        )
                        if objs:
                            obj = objs[0]
                            wechat_id = obj.wechat_id
                        else:
                            wechat_id = userstr
                        members.append(wechat_id)

                response.code = code

                response.data = members
                response.msg = data.get('errmsg')

            # 获取小程序的第三方提交代码的页面配置
            elif oper_type == 'get_code_page_configuration':
                data = tripartite_platform_objs.get_code_page_configuration(
                    authorizer_access_token
                )
                code = 301
                if data.get('errcode') in [0, '0']:
                    code = 200
                response.code = code
                response.data = data.get('members')
                response.msg = data.get('errmsg')


            # 查询某个指定版本的审核状态
            elif oper_type == 'query_specified_version_code_audit':
                auditid = request.GET.get('auditid')
                if auditid:
                    data = tripartite_platform_objs.query_specified_version_code_audit(
                        authorizer_access_token,
                        auditid
                    )
                    status = data.get('status')

                    models.AppletCodeVersion.objects.filter(auditid=auditid).update(
                        status=status,
                        user_desc=data.get('reason')
                    ) # 更新审核状态
                    code = 301
                    if data.get('errcode') in [0, '0']:
                        code = 200
                    response.code = code
                    response.data = data.get('reason')
                    response.msg = data.get('errmsg')
                else:
                    response.code = 301
                    response.msg = '参数缺失'

            # 查询最新一次提交的审核状态
            elif oper_type == 'check_status_most_recent_submission':
                auditid = request.GET.get('auditid')
                data = tripartite_platform_objs.check_status_most_recent_submission(
                    authorizer_access_token,
                    auditid
                )
                code = 301
                if data.get('errcode') in [0, '0']:
                    code = 200
                response.code = code
                response.data = data.get('members')
                response.msg = data.get('errmsg')

            # 获取草稿箱内的所有临时代码草稿
            elif oper_type == 'get_all_temporary_code_drafts':
                data = tripartite_platform_objs.xcx_get_all_temporary_code_drafts()
                code = 301
                if data.get('errcode') in [0, '0']:
                    code = 200

                data_list = []
                for data in data.get('draft_list'):
                    create_time = time.localtime(int(data.get('create_time')))
                    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", create_time)
                    data_list.append({
                        'create_time' : otherStyleTime,
                        'developer' : data.get('developer'),
                        'draft_id' : data.get('draft_id'),
                        'source_miniprogram' : data.get('source_miniprogram'),
                        'source_miniprogram_appid' : data.get('source_miniprogram_appid'),
                        'user_desc' : data.get('user_desc'),
                        'user_version' : data.get('user_version'),
                    })

                response.code = code
                response.msg = data.get('errmsg')
                response.data = data_list

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


            # 临时授权域名
            elif oper_type == 'temporary_authorized_domain_name':
                data = tripartite_platform_objs.authorized_domain_name(authorizer_access_token)

                response.code = 200
                response.msg = '授权成功'
                response.data = data


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

    if template_id and oper_type not in ['get_preview_qr_code']:
        models.ClientApplet.objects.filter(
            appid=appid
        ).update(
            template_id=template_id
        )

    return JsonResponse(response.__dict__)




def baidu_tongzhi(request):
    print('----------> ', request.GET)
    print('----------> ', request.POST)
    postdata = request.body.decode(encoding='UTF-8')
    print('postdata---------> ', postdata)

    return HttpResponse('success')










