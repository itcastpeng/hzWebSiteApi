

from publicFunc.baidu_tripartite_platform_oper import tripartite_platform_oper as tripartite_platform, \
    baidu_tripartite_platform_key
from api.forms.baidu_tripartite_platform import AuthorizationForm, UploadAppletCode, SelectForm
from api import models
from publicFunc import Response, account
from django.http import JsonResponse, HttpResponse
from urllib.parse import unquote, quote
from django.shortcuts import redirect
from publicFunc.condition_com import conditionCom
from django.db.models import Q, Count
from publicFunc.role_choice import admin_list
import time, json, datetime, requests
from api.views_dir import message_inform


# 三方平台操作
@account.is_token(models.UserProfile)
def tripartite_platform_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    template_id = request.POST.get('template_id')        # 模板ID



    tripartite_platform_oper = tripartite_platform() # 实例化公共三方

    BaiduTripartitePlatformObjs = models.BaiduTripartitePlatformManagement.objects.filter(id=1)
    BaiduTripartitePlatformObj = BaiduTripartitePlatformObjs[0]

    token = ''
    appid = request.GET.get('appid')
    if not appid:
        appid = request.POST.get('appid')
    if appid:
        token = tripartite_platform_oper.determines_whether_access_token_expired(appid)  # 判断appid是否过期

    if request.method == 'POST':

        # 引导小程序管理员授权
        if oper_type == 'boot_small_program_administrator_authorization':
            redirect_url = 'https://xcx.bjhzkq.com/api/baidu_authorize_callback?user_id={}&template_id={}'.format(
                user_id, template_id
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

        # 未授权的小程序账号上传小程序代码(提交代码包)
        elif oper_type == 'upload_small_program_code':
            response.code = 200
            response.msg = '成功'
            whether_audit = request.POST.get('whether_audit')
            if not whether_audit:
                whether_audit = False

            current_page = request.GET.get('current_page', 1)
            length = request.GET.get('length', 10)
            response = tripartite_platform_oper.get_template_list(current_page, length)
            response_data = response.data.get('list')[0]
            data = {
                'appid': appid,
                'token': token,
                'version': response_data.get('user_version'),
                'template_id': response_data.get('template_id'),
            }
            data['whether_audit'] = whether_audit
            response = tripartite_platform_oper.upload_small_program_code(data)


        # 删除模板
        elif oper_type == 'delete_template':
            o_id = request.POST.get('o_id')
            response = tripartite_platform_oper.delete_template(o_id)

        # 添加草稿至模板
        elif oper_type == 'add_draft_to_template':
            draft_id = request.POST.get('draft_id')
            user_desc = request.POST.get('user_desc')
            response = tripartite_platform_oper.add_draft_to_template(draft_id, user_desc)

        # 为授权的小程序提交审核
        elif oper_type == 'submit_approval_authorized_mini_program':
            response_data = tripartite_platform_oper.gets_list_small_packages(token)
            if not response_data.data[0].get('package_id'):
                response.code = 301
                response.msg = '请重试'
            else:
                data = {
                    'content': request.POST.get('content'),
                    'package_id': response_data.data[0].get('package_id'),
                    'remark': request.POST.get('remark'),
                    'token': token,
                }
                response = tripartite_platform_oper.submit_approval_authorized_mini_program(data)
                baidu_small_program_management_obj = models.BaiduSmallProgramManagement.objects.get(appid=appid)
                msg = "百度小程序: %s 提交审核 " % (baidu_small_program_management_obj.program_name)
                message_inform.save_msg_inform(baidu_small_program_management_obj.user_id, msg, is_send_admin=True)

        # 发布已审核的小程序
        elif oper_type == 'release_approved_applet':
            response_data = tripartite_platform_oper.gets_list_small_packages(token)
            package_id = response_data.data[-1].get('package_id')
            response = tripartite_platform_oper.release_approved_applet(package_id, token)
            if response.code == 200:
                baidu_small_program_management_obj = models.BaiduSmallProgramManagement.objects.get(appid=appid)
                msg = "百度小程序: %s 发布成功 " % (baidu_small_program_management_obj.program_name)
                message_inform.save_msg_inform(baidu_small_program_management_obj.user_id, msg, is_send_admin=True)

        # 小程序版本回滚
        elif oper_type == 'small_program_version_roll_back':
            package_id = request.POST.get('package_id')
            response = tripartite_platform_oper.small_program_version_roll_back(package_id, token)

        # 小程序审核撤回
        elif oper_type == 'small_procedure_review_withdrawal':
            package_id = request.POST.get('package_id')
            response = tripartite_platform_oper.small_procedure_review_withdrawal(package_id, token)

        # web化开关
        elif oper_type == 'web_the_switch':
            # web_status 1:开启 2:关闭
            web_status = request.POST.get('web_status')
            response = tripartite_platform_oper.web_the_switch(web_status)

        # 小程序熊掌ID绑定
        elif oper_type == 'small_procedures_bear_paw_ID_binding':
            response = tripartite_platform_oper.small_procedures_bear_paw_ID_binding()

        # 提交sitemap
        elif oper_type == 'submit_sitemap':
            higher_level = request.POST.get('higher_level')
            url_list = request.POST.get('url_list')
            response = tripartite_platform_oper.submit_sitemap(higher_level, url_list)

    else:

        # 查询所有模板
        if oper_type == 'get_all_templates':
            current_page = request.GET.get('current_page', 1)
            length = request.GET.get('length', 10)
            response = tripartite_platform_oper.get_template_list(current_page, length)

        # 获取模板草稿列表
        elif oper_type == 'gets_the_template_draft_list':
            current_page = request.GET.get('current_page', 1)
            length = request.GET.get('length', 10)
            response = tripartite_platform_oper.gets_the_template_draft_list(current_page, length)

        # 获取小程序包列表
        elif oper_type == 'gets_list_small_packages':
            response = tripartite_platform_oper.gets_list_small_packages(token)
            data_list = []
            for data in response.data:
                if data.get('status') != '开发版本':
                    data_list.append(data)

            response.data = data_list

        # 获取授权小程序包详情
        elif oper_type == 'get_details_authorization_package':
            # package_type 1线上版本 3开发中 4审核中 5审核失败 6审核通过 8回滚中

            package_id = request.GET.get('package_id')
            package_type = request.GET.get('package_type')
            response = tripartite_platform_oper.get_details_authorization_package(package_id, package_type)

        # 获取二维码
        elif oper_type == 'get_qr_code':
            width = request.GET.get('width') #
            package_id = request.GET.get('package_id') #
            if not package_id:
                xiaochengxu_data = tripartite_platform_oper.gets_list_small_packages(token)  # 查询小程序包
                if len(xiaochengxu_data.data) > 0:
                    package_id = xiaochengxu_data.data[0].get('package_id')

            path = tripartite_platform_oper.get_qr_code(package_id, width, token)
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'path': path
            }

        # 判断是否可以审核
        elif oper_type == 'determine_whether_can_be_audited':
            response_data = tripartite_platform_oper.gets_list_small_packages(token)
            flag = False
            msg = '可以审核'
            for data in response_data.data:
                if data.get('status') == '审核中':
                    flag = True
                    msg = '不可提交审核'
                    break
            response.code = 200
            response.msg = msg
            response.data = {
                'flag': flag
            }


    if template_id and appid:
        models.BaiduSmallProgramManagement.objects.filter(appid=appid).update(template_id=template_id)


    return JsonResponse(response.__dict__)


# 后台操作
@account.is_token(models.UserProfile)
def baidu_platform_management_admin(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == 'POST':
        pass

    else:

        # 查询后台所有百度小程序
        if oper_type == 'query_background_baidu_small_procedures':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                }
                q = conditionCom(request, field_dict)
                user_id_id = request.GET.get('user_id_id')
                if user_id_id:
                    q.add(Q(user_id=user_id_id), Q.AND)
                objs = models.BaiduSmallProgramManagement.objects.filter(
                    q,
                    appid__isnull=False
                ).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    ret_data.append({
                        'appid': obj.appid,
                        'program_name':obj.program_name,                                        #小程序名称
                        'app_desc': obj.app_desc,                                               # 小程序的介绍内容
                        'photo_addr': obj.photo_addr,                                           # 小程序图标
                        'user_id': obj.user_id,                                                 # 用户
                        'user_name': obj.user.username,                                         # 用户
                        'template_id': obj.template_id,                                         # 对应模板
                        'template_name': obj.template.name,                                     # 对应模板
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),   # 创建时间
                    })

                user_list = []
                baidu_user_objs = models.BaiduSmallProgramManagement.objects.select_related(
                    'user'
                ).values(
                    'user_id',
                    'user__username'
                ).annotate(
                    Count('id')
                ).filter(
                    appid__isnull=False
                ).exclude(user__role_id__in=admin_list)
                for baidu_user_obj in baidu_user_objs:
                    user_list.append({
                        'user_id': baidu_user_obj.get('user_id'),
                        'username': baidu_user_obj.get('user__username'),
                    })


                response.note = {
                    'appid': 'appid',
                    'program_name': '小程序名称',
                    'app_desc': '小程序的介绍内容',
                    'photo_addr': '小程序图标',
                    'user_id': '用户ID',
                    'user_name':'用户名称',
                    'template_id': '对应模板ID',
                    'template_name': '对应模板名称',
                    'create_datetime': '创建时间',
                }
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'count': count,
                    'ret_data': ret_data,
                    'user_list': user_list
                }
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = '请求异常'
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
    print("get_ticket_ret -->", get_ticket_ret)
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

    elif Event == 'PACKAGE_AUDIT_PASS': # 代码包审核通过
        pass

    elif Event == 'PACKAGE_AUDIT_FAIL': # 代码包审核不通过
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
    tripartite_platform_obj = tripartite_platform()
    authorization_code = request.GET.get('authorization_code')
    expires_in = request.GET.get('expires_in')

    user_id = request.GET.get('user_id')
    template_id = request.GET.get('template_id')
    tripartite_platform_obj.get_get_small_program_authorization_credentials(authorization_code, template_id, user_id)

    print('=================================================授权-------------> ', authorization_code, expires_in)
    if not template_id:
        template_id = 108

    return redirect('https://xcx.bjhzkq.com/thirdTerrace/baiduRoutine?id={}'.format(template_id))









