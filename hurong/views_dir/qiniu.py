# from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.redisOper import get_redis_obj
from publicFunc.qiniu.auth import Auth
import json, os


@account.is_token(models.UserProfile)
def get_upload_token(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "GET":

        redis_obj = get_redis_obj()
        upload_token = redis_obj.get('xhs_qiniu_upload_token')
        if not upload_token:
            qiniu_data_path = os.path.join(os.getcwd(), "publicFunc", "qiniu", "qiniu_data.json")
            with open(qiniu_data_path, "r", encoding="utf8") as f:
                data = json.loads(f.read())
                access_key = data.get('access_key')
                secret_key = data.get('secret_key')
                obj = Auth(access_key, secret_key)
                upload_token = obj.upload_token("xcx_wgw_zhangcong")
                redis_obj.set("xhs_qiniu_upload_token", upload_token, ex=60 * 50)  # 使用redis缓存50分钟

        response.code = 200
        response.msg = "获取成功"
        response.data = {
            'upload_token': upload_token
        }

    return JsonResponse(response.__dict__)

