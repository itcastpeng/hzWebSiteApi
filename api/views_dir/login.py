# developer: 张聪
# email: 18511123018@163.com

from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc import base64_encryption
from api.forms.login import LoginForm
from publicFunc.tripartite_platform_oper import tripartite_platform_oper as tripartite_platform
import json, requests, datetime


# 账号密码登录
def login(request):
    response = Response.ResponseObj()
    if request.method == "POST":
        # print('request.POST -->', request.POST)
        forms_obj = LoginForm(request.POST)
        if forms_obj.is_valid():

            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            objs = models.UserProfile.objects.filter(**forms_obj.cleaned_data)
            if objs:
                obj = objs[0]
                response.code = 200
                response.data = {
                    'token': obj.token,
                    'id': obj.id,
                    'username': obj.username,
                    'head_portrait': obj.head_portrait,
                }
            else:
                response.code = 402
                response.msg = "账号或密码错误"
        else:
            response.code = 401
            response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)


# 微信扫码登录
def wechat_login(request):
    response = Response.ResponseObj()
    if request.method == "POST":
        login_timestamp = request.POST.get('login_timestamp')
        objs = models.UserProfile.objects.filter(login_timestamp=login_timestamp)
        if objs:
            obj = objs[0]
            inviter = 0
            if obj.inviter:
                inviter = 1
            response.code = 200
            role_obj = models.Role.objects.filter(id=obj.role_id)
            data_list = []
            for i in role_obj[0].permissions.all():
                data_list.append(i.name)

            response.data = {
                'token': obj.token,
                'id': obj.id,
                'role_id': obj.role_id,
                'number_child_users': obj.number_child_users,
                'small_program_number': obj.small_program_number,
                'role_name': obj.role.name,
                'name': base64_encryption.b64decode(obj.name),
                'head_portrait': obj.head_portrait,
                'permissions_list': data_list,
                'inviter': inviter
            }
            obj.last_login_datetime = datetime.datetime.now()
            obj.save()
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)


# 微信小程序登录
def xcx_login(request):
    response = Response.ResponseObj()
    if request.method == "POST":
        js_code = request.POST.get('js_code')
        appid = request.POST.get('appid')
        userInfo = request.POST.get('userInfo') # 客户信息
        print('userInfo, type(userInfo)------> ', userInfo, type(userInfo))
        userInfo = json.loads(userInfo)
        tripartite_platform_objs = tripartite_platform()  # 实例化三方平台
        ret_data = tripartite_platform_objs.get_customer_openid(appid, js_code)  # 获取客户openid
        openid = ret_data.get('openid')
        session_key = ret_data.get('session_key') # 用于加密
        objs = models.Customer.objects.filter(openid=openid)
        nickName = base64_encryption.b64encode(userInfo.get('nickName'))

        if objs:
            objs.update(**{
                'head_portrait': userInfo.get('avatarUrl'),
                'sex': userInfo.get('gender'),
                'country': userInfo.get('country'),
                'province': userInfo.get('province'),
                'city': userInfo.get('city'),
                'name': nickName,
                'session_key': session_key,
            })
            obj = objs[0]

        else:
            token = account.get_token(account.str_encrypt(openid))
            obj = models.Customer.objects.create(**{
                'head_portrait': userInfo.get('avatarUrl'),
                'sex': userInfo.get('gender'),
                'country': userInfo.get('country'),
                'province': userInfo.get('province'),
                'city': userInfo.get('city'),
                'session_key': session_key,
                'name': nickName,
                'openid': openid,
                'token': token,
            })
        response.code = 200
        response.msg = '登录成功'
        response.data = {
            'user_id': obj.id,
            'token': obj.token,
        }


    return JsonResponse(response.__dict__)

# 外部登录
def external_login(request):
    response = Response.ResponseObj()
    external_token = request.GET.get('token')   # 平台token
    source = request.GET.get('source')          # 来自哪个平台
    userId = request.GET.get('userId')          # 来自哪个平台

    login_type = 2

    is_login_flag = True
    if source == 'dingdong': # 叮咚营销宝
        pass

    else:
        is_login_flag = False
        response.code = 402
        response.msg = '请求错误'

    if is_login_flag: # 验证通过
        user_data = {
            'role_id': 7,  # 默认普通用户
            'token': external_token,
            'login_type': login_type,
            'ding_dong_marketing_treasure_user_id': userId,
        }
        objs = models.UserProfile.objects.filter(token=external_token)
        if objs:
            obj = objs[0]

        else:
            get_user_info_url = 'http://a.yingxiaobao.org.cn/api/user/info/{}?token={}&user_id={}'.format(
                userId, external_token, userId
            )
            ret = requests.get(get_user_info_url)
            info_data = ret.json().get('data')
            user_data['username'] = base64_encryption.b64encode(info_data.get('username'))
            user_data['head_portrait'] = info_data.get('head_portrait')
            obj = models.UserProfile.objects.create(**user_data)

        role_obj = models.Role.objects.filter(id=obj.role_id)
        data_list = []
        for i in role_obj[0].permissions.all():
            data_list.append(i.name)

        inviter = 0
        if obj.inviter:
            inviter = 1

        try:
            username = base64_encryption.b64decode(obj.username)
        except Exception:
            username = obj.username

        response.code = 200
        response.msg = '登录成功'
        response.data = {
            'username': username,
            'token': obj.token,
            'id': obj.id,
            'role_id': obj.role_id,
            'role_name': obj.role.name,
            'head_portrait': obj.head_portrait,
            'permissions_list': data_list,
            'inviter': inviter,
        }

    return JsonResponse(response.__dict__)






