from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.public import verify_phone_number
import json



# @account.is_token(models.UserProfile)
def xcx_customer_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        if oper_type == "add":
            phone = request.POST.get('phone')
            if verify_phone_number(phone):
                objs = models.Customer.objects.filter(id=user_id).update(phone=phone)

                if objs:
                    response.code = 200
                    response.msg = "更新成功"

                else:
                    response.code = 301
                    response.msg = '请先登录'

            else:
                response.code = 301
                response.msg = '手机号错误'

    else:
        if oper_type == 'x':
            pass

        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)
