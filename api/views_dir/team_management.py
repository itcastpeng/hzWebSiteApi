from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
import json




@csrf_exempt
@account.is_token(models.UserProfile)
def team_management_oper(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "POST":
        user_id = request.GET.get('user_id')



    else:
        # 获取角色对应的权限
        if oper_type == "get_team_data":

            objs = models.Role.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                rules_list = [i['name'] for i in obj.permissions.values('name')]
                print('dataList -->', rules_list)
                response.data = {
                    'rules_list': rules_list
                }

                response.code = 200
                response.msg = "查询成功"

        else:
            response.code = 402
            response.msg = "请求异常"


    return JsonResponse(response.__dict__)
