# developer: 张聪
# email: 18511123018@163.com

from api import models
from publicFunc import Response
from django.http import JsonResponse
import json
from api.forms.login import LoginForm


def login(request):
    response = Response.ResponseObj()
    if request.method == "POST":
        print('request.POST -->', request.POST)
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
