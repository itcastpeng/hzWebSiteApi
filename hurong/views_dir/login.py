# developer: 张聪
# email: 18511123018@163.com

from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
import json
from hurong.forms.login import LoginForm


def login(request):
    response = Response.ResponseObj()
    if request.method == "POST":
        print('request.POST -->', request.POST)
        forms_obj = LoginForm(request.POST)
        if forms_obj.is_valid():

            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            objs = models.UserProfile.objects.select_related('role_id').filter(**forms_obj.cleaned_data)
            if objs:
                obj = objs[0]
                if obj.status != 1:
                    response.code = 300
                    response.msg = "账号异常，请联系管理员处理"
                else:
                    if not obj.token:
                        obj.token = account.get_token(obj.password)
                        obj.save()
                    response.code = 200
                    print(obj.role_id.id)
                    response.data = {
                        'token': obj.token,
                        'id': obj.id,
                        'username': obj.username,
                        # 'access': json.loads(obj.role_id.access_name),
                        'head_portrait': obj.head_portrait,
                        'is_update_pwd': obj.is_update_pwd,
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
