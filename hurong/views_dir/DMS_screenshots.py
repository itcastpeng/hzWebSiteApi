from hurong import models
from publicFunc.redisOper import get_redis_obj
from publicFunc.qiniu.auth import Auth
from publicFunc import Response
from django.http import JsonResponse
import json, requests, base64, time, os



def DMS_screenshots(request, oper_type):
    response = Response.ResponseObj()

    # 截图
    if oper_type == "save_screenshots":
        img_base64_data = request.POST.get('img_base64_data')
        imgdata = base64.b64decode(img_base64_data)

        redis_obj = get_redis_obj()
        upload_token = redis_obj.get('qiniu_upload_token')
        if not upload_token:
            qiniu_data_path = os.path.join(os.getcwd(), "publicFunc", "qiniu", "qiniu_data.json")
            with open(qiniu_data_path, "r", encoding="utf8") as f:
                data = json.loads(f.read())
                access_key = data.get('access_key')
                secret_key = data.get('secret_key')
                obj = Auth(access_key, secret_key)
                upload_token = obj.upload_token("xcx_wgw_zhangcong")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13'
        }

        url = 'https://up-z1.qiniup.com/'

        files = {
            'file': imgdata
        }

        data = {
            'token': upload_token,
        }
        ret = requests.post(url, data=data, files=files, headers=headers)

        response.code = 200
        response.msg = "提交成功"
        response.data = {
            'key': ret.json()["key"]
        }

    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)