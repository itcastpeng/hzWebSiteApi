from hurong import models
from publicFunc.redisOper import get_redis_obj
from publicFunc.qiniu.auth import Auth
from publicFunc import Response
from django.http import JsonResponse
from hurong.forms.DMS_screenshots import Screenshots
from publicFunc.public import create_xhs_admin_response
import json, requests, base64, time, os, random, hashlib





def get_qiniu_token():
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
    return upload_token

def DMS_screenshots(request, oper_type):
    response = Response.ResponseObj()
    redis_obj = get_redis_obj()

    # 截图
    if oper_type == "save_screenshots":
        start_time = time.time()
        form_data = {
            'img_base64_data': request.POST.get('img_base64_data'),
            'iccid': request.POST.get('iccid'),
            'imsi': request.POST.get('imsi')
        }

        form_obj = Screenshots(form_data)
        if form_obj.is_valid():
            forms_data = form_obj.cleaned_data
            imgdata = forms_data.get('img_base64_data')
            img_base64_data = request.POST.get('img_base64_data')
            md5_obj = hashlib.md5()
            md5_obj.update(img_base64_data.encode('utf8'))
            img_base64_data = md5_obj.hexdigest()

            judge_key = "dms_screenshots_" + forms_data.get('iccid') + forms_data.get('imsi')
            judge_key_objs = redis_obj.get(judge_key)
            img_flag = False
            key = ''
            if judge_key_objs:
                for i in json.loads(judge_key_objs):
                    if img_base64_data == i['img_base64_data']:
                        img_flag = True
                        key = i['key']
                        break
            # print("1111 -->", time.time() - start_time)
            # print("key -->", key)
            if not img_flag:
                print("没有保存过，提交七牛云获取url")
                upload_token = get_qiniu_token()
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
                print("七牛云返回数据 -->", ret.json())
                print("222 -->", time.time() - start_time)
                key = "http://qiniu.bjhzkq.com/{key}?imageView2/0/h/400".format(key=ret.json()["key"])


                if judge_key_objs:
                    data_list = json.loads(judge_key_objs)
                    data_list.append({'key': key, 'img_base64_data': img_base64_data})
                    redis_obj.delete(judge_key)
                    redis_obj.set(judge_key, json.dumps(data_list))
                else:
                    redis_obj.set(judge_key, json.dumps([{'img_base64_data': img_base64_data, 'key': key}]))

            # ===================保存最后 十张截图=====================
            num = 0
            while True:
                num += 1
                xhs_screenshots = redis_obj.llen('xhs_screenshots') # 保存截图
                if int(xhs_screenshots) < 10:  # 只保存十个 追加
                    redis_obj.rpush('xhs_screenshots', key)
                    break
                else:
                    redis_obj.lpop('xhs_screenshots')
                if num >= 10:
                    break
            print("333 -->", time.time() - start_time)
            response.code = 200
            response.msg = "提交成功"
            response.data = {
                'key': key
            }

        else:
            response.code = 301
            response.msg = json.loads(form_obj.errors.as_json())

        # print("444 -->", time.time() - start_time)
        # create_xhs_admin_response(request, response, 3)  # 创建请求日志(手机端)
        # print("555 -->", time.time() - start_time)
        # print("response.data -->", response.data, response.code, response.code)

    # 上传截图
    elif oper_type == 'upload_img':
        img_base64_data = request.POST.get('img_base64_data')
        imgdata = base64.b64decode(img_base64_data)
        upload_token = get_qiniu_token()
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
        key = "http://qiniu.bjhzkq.com/{key}?imageView2/0/h/400".format(key=ret.json()["key"])

        response.code = 200
        response.msg = '上传成功'
        response.data = {
            'key': key
        }

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
