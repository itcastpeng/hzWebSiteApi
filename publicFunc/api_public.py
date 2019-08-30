from api import models
from publicFunc.Response import ResponseObj
from django.http import JsonResponse




response = ResponseObj()




# 创建日志
def create_error_log(data):
    models.ErrorLog.objects.create(**data)
    response.code = 200
    response.msg = '创建日志完成'

    return JsonResponse(response.__dict__)



























