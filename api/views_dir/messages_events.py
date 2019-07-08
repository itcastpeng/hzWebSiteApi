

from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse





def messages_events_oper(request, oper_type, appid):
    response = Response.ResponseObj()

    # 消息与事件接收
    if oper_type == 'callback':
        pass









    return JsonResponse(response.__dict__)












