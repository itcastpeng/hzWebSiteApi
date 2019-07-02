from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from api.forms.tripartite_platform import AuthorizationForm
import time, json, datetime


@account.is_token(models.UserProfile)
def tripartite_platform_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 授权
        if oper_type == "authorization":
            form_data = {
                'user_id': user_id,
                'appid': request.POST.get('appid'),
            }

            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AuthorizationForm(form_data)
            if forms_obj.is_valid():
                print('--')

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
