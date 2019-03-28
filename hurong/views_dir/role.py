# from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.user import SelectForm, AddForm, UpdateForm
import json
from django.db.models import Q
# import re
# import datetime
# from publicFunc import base64_encryption


@account.is_token(models.UserProfile)
def role(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            # q.add(Q(**{k + '__contains': value}), Q.AND)
            objs = models.Role.objects.filter(q).order_by(order)
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
                    'name': obj.name
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            response.note = {
                'id': "角色id",
                'name': "角色名"
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
def role_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "POST":
        # 添加用户
        if oper_type == "add":
            form_data = {
                'create_user_id': request.GET.get('user_id'),
                'username': request.POST.get('username'),
                'password': request.POST.get('password'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                create_data = {
                    'create_user_id': forms_obj.cleaned_data.get('create_user_id'),
                    'username': forms_obj.cleaned_data.get('username'),
                    'password': forms_obj.cleaned_data.get('password'),
                }
                print('create_data -->', create_data)
                obj = models.UserProfile.objects.create(**create_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {
                    'testCase': obj.id,
                    'id': obj.id,
                }
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            models.UserProfile.objects.exclude(id=1).filter(id=o_id).update(status=3)
            response.code = 200
            response.msg = "删除成功"

        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'password': request.POST.get('password'),
                'status': request.POST.get('status'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data['o_id']
                update_data = {
                    'status': forms_obj.cleaned_data['status'],
                }
                password = forms_obj.cleaned_data['password']
                if password:
                    update_data['password'] = password

                # 更新数据
                models.UserProfile.objects.filter(id=o_id).update(**update_data)

                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)

