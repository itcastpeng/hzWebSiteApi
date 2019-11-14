from api import models
from publicFunc import Response, account
from django.http import JsonResponse, HttpResponse
from api.forms.tripartite_platform import AuthorizationForm, UploadAppletCode, SelectForm
from publicFunc.tripartite_platform_oper import tripartite_platform_oper as tripartite_platform, \
    QueryWhetherCallingCredentialExpired as CredentialExpired, GetTripartitePlatformInfo, encodingAESKey, \
    encoding_token, encoding_appid
from publicFunc.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
from urllib.parse import unquote, quote
from publicFunc.role_choice import admin_list
from django.shortcuts import redirect
from publicFunc.condition_com import conditionCom
from publicFunc.public import get_qrcode, upload_qiniu
from publicFunc.base64_encryption import b64decode
from django.db.models import Q, Count
from publicFunc.baidu_tripartite_platform_oper import  tripartite_platform_oper as baidu_tripartite_platform_oper
import time, json, datetime, xml.etree.cElementTree as ET, requests

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
            response.code = 301
            if ret_json.get('errcode') in [0, '0']:
                response.code = 200
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
            response.msg = ret_json.get('errmsg')
            response.data = ret_json



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
            if 'app is already released' in errmsg:
                errmsg = '重复发布'

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

            # 获取小程序体验二维码(提交代码包) (体验码)
            elif oper_type == 'get_experience_qr_code':
                user_obj = models.UserProfile.objects.get(id=user_id)
                baidu_appid = request.GET.get('baidu_appid')
                user_desc = request.GET.get('user_desc')
                code = 200
                msg = '查询成功'
                data_dict = {
                    'user_desc': user_desc,
                    'user_id': user_id,
                    'user_token': user_obj.token,
                }
                ret_data = {
                    'xcx_code': '',
                    'gzh_code': '',
                    'baidu_xcx_code': ''
                }
                get_experience_qr_code_template_id = ''
                if appid:
                    xcx_code = ''
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

                        xcx_code = data.get('path')
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
                            xcx_code = data.get('path')

                        else:
                            code = 301
                            msg = '请先绑定模板'
                    ret_data['xcx_code'] = xcx_code
                # 百度小程序
                if baidu_appid:
                    baidu_objs = models.BaiduSmallProgramManagement.objects.filter(appid=baidu_appid)
                    get_experience_qr_code_template_id = baidu_objs[0].template_id
                    baidu_tripartite_platform = baidu_tripartite_platform_oper()
                    response = baidu_tripartite_platform.get_template_list(1, 10)  # 获取模板列表
                    response_data = response.data.get('list')[0]
                    print('response_data--------------------------> ', response_data)
                    data = {
                        'appid': baidu_objs[0].appid,
                        'token': baidu_objs[0].access_token,
                        'version': response_data.get('user_version'),
                        'template_id': response_data.get('template_id'),
                        'id': get_experience_qr_code_template_id,
                        'user_id': user_id,
                        'user_token': user_obj.token,
                    }
                    baidu_tripartite_platform.web_the_switch(baidu_objs[0].access_token, 2) # 关闭web化开关
                    baidu_tripartite_platform.upload_small_program_code(data)
                    time.sleep(3)
                    response_data = baidu_tripartite_platform.gets_list_small_packages(baidu_objs[0].access_token)
                    package_id = response_data.data[0].get('package_id')
                    print('package_idpackage_idpackage_idpackage_idpackage_idpackage_idpackage_id=============== > ', package_id)
                    baidu_xcx_qrcode = baidu_tripartite_platform.get_qr_code(package_id, 200, baidu_objs[0].access_token)
                    ret_data['baidu_xcx_code'] = baidu_xcx_qrcode

                if get_experience_qr_code_template_id:
                    template_obj = models.Template.objects.get(id=get_experience_qr_code_template_id)
                    ret_data['gzh_code'] = template_obj.qrcode

                response.code = code
                response.msg = msg

                response.data = ret_data

            # 获取代码模板库中的所有小程序代码模板
            elif oper_type == 'get_code':
                current_page = int(request.GET.get('current_page', 1))
                length = int(request.GET.get('length', 10))
                start_line = (current_page - 1) * length
                stop_line = start_line + length

                response_data = tripartite_platform_objs.xcx_get_code_template()
                response.code = 301
                if response_data.get('errcode') in [0, '0']:
                    template_list = response_data.get('template_list')
                    template_list = sorted(template_list, key=lambda x: x['create_time'], reverse=True)

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': template_list[start_line: stop_line],
                        'count': len(template_list),
                    }

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
                current_page = int(request.GET.get('current_page', 1))
                length = int(request.GET.get('length', 10))
                start_line = (current_page - 1) * length
                stop_line = start_line + length

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
                data_list = data_list[start_line: stop_line]
                response.code = code
                response.msg = data.get('errmsg')
                response.data = {
                    'ret_data': data_list,
                    'count': len(data_list)
                }

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

            # 获取预览微信/百度小程序二维码
            elif oper_type == 'get_preview_qr_code':
                user_obj = models.UserProfile.objects.get(id=user_id)
                template_id = request.GET.get('template_id')
                whether_regenerate = request.GET.get('whether_regenerate', 0) # 重新生成
                template_obj = models.Template.objects.get(id=template_id)
                path = template_obj.xcx_qrcode
                baidu_xcx_qrcode = template_obj.baidu_xcx_qrcode

                if whether_regenerate or not path: # 重新生成 微信小程序码
                    request_url = 'pages/index/tarBar01?token={}&user_id={}&template_id={}'.format(
                        user_obj.token, user_id, template_id
                    )
                    if not appid:
                        credential_expired_data = CredentialExpired('wx700c48cb72073e61', 2)  # 判断调用凭证是否过期 (操作 GZH/XCX 前调用该函数)
                        authorizer_access_token = credential_expired_data.get('authorizer_access_token')

                    url = 'https://api.weixin.qq.com/cgi-bin/wxaapp/createwxaqrcode?access_token={}'.format(authorizer_access_token)
                    data = {
                        'path': request_url,
                        'width': 430
                    }
                    ret = requests.post(url, data=json.dumps(data))

                    img_path = str(int(time.time())) + '.png'
                    with open(img_path, 'wb') as f:
                        f.write(ret.content)
                    path = upload_qiniu(img_path, 800)

                    template_obj.xcx_qrcode = path
                    template_obj.save()

                if whether_regenerate or not baidu_xcx_qrcode:
                    objs = models.BaiduSmallProgramManagement.objects.filter(appid='14794638')
                    baidu_tripartite_platform = baidu_tripartite_platform_oper()
                    token = baidu_tripartite_platform.determines_whether_access_token_expired('14794638')  # 判断appid是否过期
                    response = baidu_tripartite_platform.get_template_list(1, 10)  # 获取模板列表
                    response_data = response.data.get('list')[0]
                    data = {
                        'appid': objs[0].appid,
                        'token': objs[0].access_token,
                        'version': response_data.get('user_version'),
                        'template_id': response_data.get('template_id'),
                        'id': template_id,
                        'user_id': user_id,
                        'user_token': user_obj.token,
                    }
                    print('data-=-------------------------> ', data)
                    baidu_tripartite_platform.upload_small_program_code(data)
                    time.sleep(3)
                    response_data = baidu_tripartite_platform.gets_list_small_packages(token)
                    package_id = response_data.data[0].get('package_id')
                    print('package_id---------------------> ', package_id)
                    baidu_xcx_qrcode = baidu_tripartite_platform.get_qr_code(package_id, 200, token)
                    template_obj.baidu_xcx_qrcode = baidu_xcx_qrcode
                    template_obj.save()
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'xcx_code': path,
                    'gzh_code': template_obj.qrcode,
                    'baidu_xcx_qrcode': baidu_xcx_qrcode,
                }

            # 临时授权域名
            elif oper_type == 'temporary_authorized_domain_name':
                data = tripartite_platform_objs.authorized_domain_name(authorizer_access_token)

                response.code = 200
                response.msg = '授权成功'
                response.data = data

            # 审核撤回
            elif oper_type == 'audit_to_withdraw':
                response_data = tripartite_platform_objs.audit_to_withdraw(authorizer_access_token)
                response.code = 301
                if response_data.get('errcode') in [0, '0']:
                    response.code = 200
                response.msg = response_data.get('errmsg')

            # 版本回退
            elif oper_type == 'version_back':
                response_data = tripartite_platform_objs.version_back(authorizer_access_token)
                response.code = 301
                if response_data.get('errcode') in [0, '0']:
                    response.code = 200
                response.msg = response_data.get('errmsg')


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


# 微信小程序操作
@account.is_token(models.UserProfile)
def tripartite_platform_admin(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    user_obj = models.UserProfile.objects.get(id=user_id)
    if user_obj.inviter:
        user_id = user_obj.inviter_id

    if request.method == "POST":

        # 保存小程序页面数据
        if oper_type == 'applet_code_version':
            page_data = request.POST.get('page_data')               # 页面数据
            appid = request.POST.get('appid')                       # appid
            navigation_data = request.POST.get('navigation_data')   # 导航数据
            objs = models.ClientApplet.objects.filter(appid=appid)
            if objs:
                obj = objs[0]
                models.AppletCodeVersion.objects.create(
                    applet_id=obj.id,
                    page_data=page_data,
                    navigation_data=navigation_data,
                )
                response.code = 200
                response.msg = '保存成功'

            else:
                response.code = 301
                response.msg = '该小程序不存在'


    else:

        # 查询个人XCX/GZH
        if oper_type == 'select_xcx_gzh_info':
            applet_objs = models.ClientApplet.objects.filter(user_id=user_id)
            offici_objs = models.CustomerOfficialNumber.objects.filter(user_id=user_id)

            applet_flag = False
            offici_flag = False
            result_data = {}
            if applet_objs:
                applet_flag = True
                obj = applet_objs[0]
                result_data['xcx_is_authorization'] = obj.is_authorization
                result_data['xcx_nick_name'] = obj.nick_name
                result_data['xcx_head_img'] = obj.head_img
                result_data['xcx_qrcode_url'] = obj.qrcode_url
                result_data['xcx_appid'] = obj.appid
                result_data['xcx_create_datetime'] = obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S')

            if offici_objs:
                offici_flag = True
                obj = offici_objs[0]
                result_data['gzh_is_authorization']=obj.is_authorization
                result_data['gzh_nick_name']=obj.nick_name
                result_data['gzh_head_img']=obj.head_img
                result_data['gzh_qrcode_url']=obj.qrcode_url
                result_data['gzh_appid']=obj.appid
                result_data['gzh_create_datetime']=obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S')


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

        # 查询个人提交的代码
        elif oper_type == 'query_individual_submitted_code':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                appid = request.GET.get('appid')
                field_dict = {
                    'user_desc': '__contains',
                    'user_version': '__contains',
                }
                q = conditionCom(request, field_dict)
                print('q -->', q)

                objs = models.AppletCodeVersion.objects.filter(
                    q,
                    applet__appid=appid
                ).order_by(order)
                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                # 返回的数据
                ret_data = []

                for obj in objs:
                    #  将查询出来的数据 加入列表
                    ret_data.append({
                        'id': obj.id,
                        'applet_id': obj.applet.id,
                        'applet_name': obj.applet.nick_name,
                        'applet_head_img': obj.applet.head_img,
                        'navigation_data': obj.navigation_data,
                        'page_data': obj.page_data,
                        'user_desc': obj.user_desc,
                        'user_version': obj.user_version,
                        'status_id': obj.status,
                        'status': obj.get_status_display(),
                        'auditid': obj.auditid,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count
                }
                response.note = {
                    'id': '提交的代码ID',
                    'applet_id': '小程序ID',
                    'applet_name': '小程序名称',
                    'applet_head_img': '小程序头像',
                    'navigation_data': '导航数据',
                    'page_data': '页面数据',
                    'user_desc': '备注',
                    'user_version': '版本',
                    'create_datetime': '创建时间',
                }
            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        # 判断 是否有代码在审核状态
        elif oper_type == 'whether_there_code_review_status':
            appid = request.GET.get('appid')
            flag = False
            objs = models.AppletCodeVersion.objects.filter(
                applet__appid=appid,
                status=2
            )
            if objs:
                flag = True

            response.code = 200
            response.msg = '查询成功'
            response.data = flag

        # 查询所有模板
        elif oper_type == 'query_all_templates':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'user_desc': '__contains',
                    'user_version': '__contains'
                }
                q = conditionCom(request, field_dict)
                print('q -->', q)

                if user_obj.inviter and len(user_obj.select_template_list) > 0:
                    q.add(Q(id__in=json.loads(user_obj.select_template_list)), Q.AND)

                objs = models.Template.objects.filter(
                    q,
                    create_user_id=user_id
                ).order_by(order)
                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                # 返回的数据
                ret_data = []
                num = 0
                for obj in objs:

                    is_applet = False
                    if obj.clientapplet_set.all():
                        is_applet = True

                    template_class_id = ''
                    template_class_name = ''
                    if obj.template_class:
                        template_class_id = obj.template_class_id
                        template_class_name = obj.template_class.name

                    #  将查询出来的数据 加入列表
                    ret_data.append({
                        'id': obj.id,
                        'name': obj.name,
                        'logo_img': obj.logo_img,
                        'thumbnail': obj.thumbnail,
                        'share_qr_code': obj.share_qr_code,
                        'template_class_id': template_class_id,
                        'template_class_name': template_class_name,
                        'tab_bar_data': obj.tab_bar_data,
                        'is_applet': is_applet,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })

                    if is_applet:
                        applet_obj = obj.clientapplet_set.all()[0]
                        ret_data[num]['is_authorization'] = applet_obj.is_authorization
                        ret_data[num]['appid'] = applet_obj.appid
                        ret_data[num]['applet_id'] = applet_obj.id
                        ret_data[num]['nick_name'] = applet_obj.nick_name
                        ret_data[num]['qrcode_url'] = applet_obj.qrcode_url
                        ret_data[num]['head_img'] = applet_obj.head_img

                    num += 1

                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count
                }
                response.note = {
                    'id': '提交的代码ID',
                    'is_applet': '是否有小程序',
                    'logo_img': 'logo图片',
                    'thumbnail': '缩略图',
                    'share_qr_code': '微信分享二维码',
                    'template_class_name': '模板分类名称',
                    'template_class_id': '是否模板分类ID',
                    'tab_bar_data': '底部导航数据',
                    'applet_id': '小程序ID',
                    'appid': '小程序APPID',
                    'nick_name': '小程序名字',
                    'head_img': '小程序头像',
                    'qrcode_url': '小程序二维码',
                    'is_authorization': '小程序是否授权',
                    'create_datetime': '创建时间',
                }
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 获取模板二维码
        elif oper_type == 'get_qrcode':
            objs = models.Template.objects.filter(id=o_id)

            data = {'path': ''}
            if objs:
                path = get_qrcode('https://xcx.bjhzkq.com/wx/?id={}'.format(o_id))
                objs.update(qrcode=path)
                code = 200
                msg = '获取成功'
                data['path'] = path

            else:
                code = 301
                msg = '获取失败'

            response.code = code
            response.msg = msg
            response.data = data

        # 查询所有小程序
        elif oper_type == 'query_all_applets':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id':'',
                }
                q = conditionCom(request, field_dict)
                user_id_id = request.GET.get('user_id_id')
                if user_id_id:
                    q.add(Q(user_id=user_id_id), Q.AND)
                objs = models.ClientApplet.objects.filter(
                    q,
                ).order_by(order)
                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:

                    user_id = ''
                    username = ''
                    if obj.user:
                        user_id = obj.user_id
                        username = obj.user.name
                    ret_data.append({
                        'id': obj.id,
                        'appid': obj.appid,
                        'nick_name': obj.nick_name,
                        'head_img': obj.head_img,
                        'user_id': user_id,
                        'username': b64decode(username),
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })

                user_objs = models.ClientApplet.objects.filter(
                    user__isnull=False
                ).select_related('user').values(
                    'user_id',
                    'user__name'
                ).annotate(
                    Count('id')
                ).exclude(
                    user__role_id__in=admin_list
                ).distinct()
                user_count = user_objs.count()
                user_list = []
                for user_obj in user_objs:
                    user_list.append({
                        'id':user_obj.get('user_id'),
                        'name': b64decode(user_obj.get('user__name'))
                    })


                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                    'user_count': user_count,
                    'user_list': user_list,
                }
                response.note = {
                    'id': '提交的代码ID',
                    'create_datetime': '创建时间',
                }
            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)

# 授权事件接收  （微信后台10分钟一次回调该接口 传递component_verify_ticket）
def tongzhi(request):

    user_id = request.GET.get('user_id')
    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    msg_signature = request.GET.get('msg_signature')
    postdata = request.body.decode(encoding='UTF-8')

    xml_tree = ET.fromstring(postdata)
    appid = xml_tree.find('AppId').text
    Encrypt = xml_tree.find('Encrypt').text

    objs = models.TripartitePlatform.objects.filter(
        appid=appid
    )
    wx_obj = WXBizMsgCrypt(encoding_token, encodingAESKey, encoding_appid)
    ret, decryp_xml = wx_obj.DecryptMsg(Encrypt, msg_signature, timestamp, nonce)
    decryp_xml_tree = ET.fromstring(decryp_xml)
    oper_type = decryp_xml_tree.find("InfoType").text
    print('*******************//////////*******************/////////******************')
    if oper_type == 'unauthorized': # 取消授权通知
        # ComponentVerifyTicket = decryp_xml_tree.find("AppId").text
        print('-------------------取消授权通知-', decryp_xml_tree)

    elif oper_type == 'authorized':  # 授权通知
        print('-------------------授权成功通知-', decryp_xml_tree)



    elif oper_type == 'component_verify_ticket': # 获取ticket
        print('=======================================获取ticket')
        ComponentVerifyTicket = decryp_xml_tree.find("ComponentVerifyTicket").text
        objs.update(
            component_verify_ticket=ComponentVerifyTicket
        )


    objs.update(linshi=postdata)

    return HttpResponse('success')

# 用户确认 同意授权 回调(用户点击授权 or 扫码授权后 跳转)
def authorize_callback(request):
    """
                   auth_code   : GZH/XCX 授权码
                   expires_in  : GZH/XCX 授权码过期时间
               """
    auth_code = request.GET.get('auth_code')
    expires_in = request.GET.get('expires_in')

    user_id = request.GET.get('user_id')
    template_id = request.GET.get('template_id')
    authorization_type = request.GET.get('authorization_type')  # 授权类型 (1公众号, 2小程序)

    tripartite_platform_objs = tripartite_platform()  # 实例化三方平台
    # # 使用授权码 获取调用 GZH/XCX 凭证
    id = tripartite_platform_objs.exchange_calling_credentials(authorization_type, auth_code, user_id, template_id) # 创建/更新 授权

    if authorization_type in [1, '1']:
        obj = models.CustomerOfficialNumber.objects.get(id=id)
    else:
        obj = models.ClientApplet.objects.get(id=id)
        # 授权 开发域名
        credential_expired_data = CredentialExpired(obj.appid, authorization_type)  # 判断调用凭证是否过期 (操作 GZH/XCX 前调用该函数)
        authorizer_access_token = credential_expired_data.get('authorizer_access_token')
        data = tripartite_platform_objs.authorized_domain_name(authorizer_access_token)

    # ==== 更改 GZH/XCX 授权码 和 过期时间
    obj.auth_code = auth_code
    obj.auth_code_expires_in=int(time.time()) + int(expires_in)
    obj.is_authorization=1
    obj.save()



    return redirect('https://xcx.bjhzkq.com/thirdTerrace/smallRoutine?id={}'.format(template_id))
    # return HttpResponse('success')



















