# from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.task_info import SelectForm
import json
from django.db.models import Q
# import re
# import datetime
# from publicFunc import base64_encryption


@account.is_token(models.UserProfile)
def task_info(request):
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
                'task_list_id': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            # q.add(Q(**{k + '__contains': value}), Q.AND)
            objs = models.TaskInfo.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'to_email': obj.to_email,
                    'send_num': obj.send_num,
                    'status': obj.get_status_display()
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            response.note = {
                'id': "任务id",
                'to_email': "接收邮件的邮箱",
                'send_num': "发送次数",
                'status': "状态"
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)
