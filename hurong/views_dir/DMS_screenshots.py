from hurong import models
from publicFunc.redisOper import get_redis_obj
from publicFunc.qiniu.auth import Auth
from publicFunc import Response
from django.http import JsonResponse
import json, requests, base64, time, os, random



def DMS_screenshots(request, oper_type):
    response = Response.ResponseObj()
    redis_obj = get_redis_obj()

    # 截图
    if oper_type == "save_screenshots":
        img_base64_data = request.POST.get('img_base64_data')
        img_base64_data = img_base64_data.replace(' ', '+')
        imgdata = base64.b64decode(img_base64_data)
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
        key = "http://qiniu.bjhzkq.com/{key}?imageView2/0/h/400".format(key=ret.json()["key"])
        response.data = {
            'key': key
        }

        num = 0
        while True:
            num += 1
            xhs_screenshots = redis_obj.llen('xhs_screenshots') # 保存截图
            if int(xhs_screenshots) <= 10:  # 只保存十个 追加
                redis_obj.rpush('xhs_screenshots', key)
                break
            else:
                redis_obj.lpop('xhs_screenshots')
            if num >= 10:
                break

    else:

        # 查询截图
        if oper_type == 'get_screenshots':
            ret_data = []
            for i in redis_obj.lrange('xhs_screenshots', 0, 10):
                ret_data.append(i)
            response.code = 200
            response.msg = '查询成功'
            response.data = list(reversed(ret_data))

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)