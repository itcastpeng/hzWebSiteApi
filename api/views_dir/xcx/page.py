from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse


# @account.is_token(models.UserProfile)
def page_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        pass

    else:
        if oper_type == "get_page_data":
            experience = request.GET.get('experience')  # 是否是体验版,该字段有值则为体验版
            page_objs = models.Page.objects.filter(id=o_id)
            if page_objs:
                page_obj = page_objs[0]
                page_data = page_obj.data
                if experience == "true":
                    page_data = page_obj.data_dev
                response.code = 200
                response.data = page_data
            else:
                print('page_objs -->', page_objs)
                response.code = 302
                response.msg = "页面id异常"
        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)
