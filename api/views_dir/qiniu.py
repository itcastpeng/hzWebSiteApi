# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.redisOper import get_redis_obj
from publicFunc.qiniu.auth import Auth
import json
import os


@account.is_token(models.UserProfile)
def get_upload_token(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "GET":

        redis_obj = get_redis_obj()
        upload_token = redis_obj.get('qiniu_upload_token')
        if not upload_token:
            qiniu_data_path = os.path.join(os.getcwd(), "publicFunc", "qiniu", "qiniu_data.json")
            with open(qiniu_data_path, "r", encoding="utf8") as f:
                data = json.loads(f.read())
                access_key = data.get('access_key')
                secret_key = data.get('secret_key')
                obj = Auth(access_key, secret_key)
                ret = obj.upload_token("xcx_wgw_zhangcong")
                print('ret -->', ret)

        response.code = 200
        response.msg = "获取成功"

    return JsonResponse(response.__dict__)

