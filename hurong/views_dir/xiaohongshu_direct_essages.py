from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from publicFunc.send_email import SendEmail
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.xiaohongshu_direct_essages import SelectForm, AddForm, GetReleaseTaskForm, SaveScreenshotsForm
from django.db.models import Q
import redis
import json
import requests
import datetime
import re
import base64
import time

from publicFunc.redisOper import get_redis_obj
from publicFunc.qiniu.auth import Auth
import os

@account.is_token(models.UserProfile)
def xiaohongshu_direct_essages(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'status': '',
                'select_type': '',
                'keywords': '__contains',
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.XiaohongshuFugai.objects.filter(q).order_by(order)
            print(objs)
            count = objs.count()

            if length != 0:
                if count < 10:
                    current_page = 1
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                #  将查询出来的数据 加入列表
                update_datetime = ""
                if obj.update_datetime:
                    update_datetime = obj.update_datetime.strftime('%Y-%m-%d %H:%M:%S')

                keywords = "({select_type}) {keywords}".format(
                    keywords=obj.keywords,
                    select_type=obj.get_select_type_display()
                )
                ret_data.append({
                    'id': obj.id,
                    'keywords': keywords,
                    'url': obj.url,
                    'rank': obj.rank,
                    'biji_num': obj.biji_num,
                    'status': obj.get_status_display(),
                    'status_id': obj.status,
                    'select_type': obj.get_select_type_display(),
                    'select_type_id': obj.select_type,
                    'create_user__username': obj.create_user.username,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'update_datetime': update_datetime,
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'status_choices': models.XiaohongshuFugai.status_choices,
                'select_type_choices': models.XiaohongshuFugai.select_type_choices,
            }
            response.note = {
                'id': "下拉词id",
                'keywords': "搜索词",
                'url': "匹配url",
                'rank': "排名",
                'biji_num': "笔记数",
                'status': "状态",
                'status_id': "状态id",
                'select_type': "搜索类型",
                'select_type_id': "搜索类型id",
                'create_user__username': "创建人",
                'create_datetime': "创建时间",
                'update_datetime': "更新时间",
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.UserProfile)
def xiaohongshu_direct_essages_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "POST":
        # 保存私信截图
        if oper_type == "save_screenshots":
            print("request.POST ---> ///////////////////", request.POST)

            form_data = {
                'iccid': request.POST.get('iccid'),
                'imsi': request.POST.get('imsi'),
                'img_base64_data': request.POST.get('img_base64_data')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = SaveScreenshotsForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                iccid = forms_obj.cleaned_data.get('iccid')
                imsi = forms_obj.cleaned_data.get('imsi')
                img_base64_data = forms_obj.cleaned_data.get('img_base64_data')
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
                    'key': "xiaohongshu_fabu_" + str(int(time.time() * 1000))
                }

                ret = requests.post(url, data=data, files=files, headers=headers)
                print("ret.text -->", ret.text)

                # obj = models.XiaohongshuBiji.objects.create(
                #     user_id_id=user_id,
                #     content=content,
                #     release_time=release_time
                # )


                response.code = 200
                response.msg = "添加成功"
                response.data = {
                }
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = "请求异常"

    else:
        # 获取发布任务
        if oper_type == "get_release_task":
            form_data = {
                'imsi': request.GET.get('imsi'),
                'iccid': request.GET.get('iccid'),
            }
            forms_obj = GetReleaseTaskForm(form_data)
            if forms_obj.is_valid():
                iccid = forms_obj.cleaned_data['iccid']
                imsi = forms_obj.cleaned_data['imsi']

                objs = models.XiaohongshuBiji.objects.filter(
                    user_id__phone_id__iccid=iccid,
                    user_id__phone_id__imsi=imsi,
                    status=1,
                    release_time__lt=datetime.datetime.now()
                )

                if objs:
                    obj = objs[0]

                    response.code = 200
                    response.data = {
                        "id": obj.id,
                        "content": obj.content
                    }
                else:
                    response.code = 0
                    response.msg = "当前无任务"

            else:
                print("forms_obj.errors -->", forms_obj.errors)
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)