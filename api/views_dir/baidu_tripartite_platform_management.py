

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
    template_id = request.POST.get('template_id')        # 模板ID

    tripartite_platform_oper = tripartite_platform() # 实例化公共三方

    BaiduTripartitePlatformObjs = models.BaiduTripartitePlatformManagement.objects.filter(id=1)
    BaiduTripartitePlatformObj = BaiduTripartitePlatformObjs[0]

    if request.method == 'POST':
        appid = request.POST.get('appid')
        token = tripartite_platform_oper.determines_whether_access_token_expired(appid)  # 判断appid是否过期

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
            xiaochengxu_data = tripartite_platform_oper.gets_list_small_packages(token) # 查询小程序包
            response.code = 200
            response.msg = '成功'
            flag = False
            if len(xiaochengxu_data.data) > 0:
                status = xiaochengxu_data.data[0].get('status')
                if status != '开发版本':
                    flag = True
            else:
                flag = True

            if flag:
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
                response = tripartite_platform_oper.upload_small_program_code(data)
                time.sleep(3)

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

        # 发布已审核的小程序
        elif oper_type == 'release_approved_applet':
            response_data = tripartite_platform_oper.gets_list_small_packages(token)
            package_id = response_data.data[0].get('package_id')
            response = tripartite_platform_oper.release_approved_applet(package_id, token)

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

        appid = request.GET.get('appid')
        token = tripartite_platform_oper.determines_whether_access_token_expired(appid) # 判断appid是否过期

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
            path = tripartite_platform_oper.get_qr_code(package_id, width)
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
                if data.get('status') in [4, '4', 8, '8']:
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


    return redirect('https://xcx.bjhzkq.com/thirdTerrace/baiduRoutine?id={}'.format(template_id))









