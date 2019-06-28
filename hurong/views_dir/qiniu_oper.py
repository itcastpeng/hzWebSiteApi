
from hurong import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.qiniu_oper import get_qiniu_token


@account.is_token(models.UserProfile)
def qiniu_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == "POST":
        pass

    else:

        # 获取七牛云token
        if oper_type == "get_token":
            data = get_qiniu_token()
            response.code = 200
            response.msg = '获取token成功'
            response.data = data


        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
