# developer: 张聪
# email: 18511123018@163.com

from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
import json
from publicFunc import base64_encryption
from api.forms.login import LoginForm
from publicFunc.weixin import weixin_xcx_api


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
                    'head_portrait': obj.head_portrait
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
            is_template = False
            if obj.template_set.all(): # 是否存在模板
                is_template = True

            response.code = 200
            response.data = {
                'token': obj.token,
                'id': obj.id,
                'name': base64_encryption.b64decode(obj.name),
                'is_template': is_template,
                'head_portrait': obj.head_portrait
            }
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)


# 微信小程序登录
def xcx_login(request):
    response = Response.ResponseObj()
    if request.method == "POST":
        code = request.POST.get('code')
        print('code -->', code)

        weixin_xcx_api_obj = weixin_xcx_api.WeChatApi()
        data = weixin_xcx_api_obj.get_jscode2session(code)
        print('data -->', data)
        openid = data.get('openid')
        session_key = data.get('session_key')
        client_userprofile_objs = models.ClientUserProfile.objects.filter(openid=openid)
        if client_userprofile_objs:     # 存在更新
            client_userprofile_objs.update(session_key=session_key)
            client_userprofile_obj = client_userprofile_objs[0]
        else:   # 不存在新建
            data['token'] = account.get_token()
            data['user_type'] = 2
            client_userprofile_obj = models.ClientUserProfile.objects.create(**data)
        response.code = 200
        response.data = {
            'token': client_userprofile_obj.token,
            'id': client_userprofile_obj.id
        }
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)

