from django.http import HttpResponse
from api import models
from publicFunc.public import send_error_msg
from django.db.models import Q
import datetime, time, random, requests, json



# 定时刷新转接 时间是否过期
def time_refresh_whether_connect_time_expired(request):
    objs = models.Transfer.objects.filter(whether_transfer_successful__in=[1, 2])
    for obj in objs:
        if int(obj.timestamp) + 600 < int(time.time()):
            obj.whether_transfer_successful = 3
            obj.save()

    return HttpResponse('1')




