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
def user(request):
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
            objs = models.UserProfile.objects.select_related('role_id').exclude(Q(status=3)).filter(q).order_by(order)
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
                    'username': obj.username,
                    'role_name': obj.role_id.name,
                    'role_id': obj.role_id_id,
                    'status': obj.get_status_display(),
                    'status_id': obj.status,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            response.note = {
                'id': "用户id",
                'username': "用户名",
                'status': "用户状态",
                'create_datetime': "创建时间"
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
def user_oper(request, oper_type, o_id):
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
                'role_id': request.POST.get('role_id'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                create_data = {
                    'create_user_id': forms_obj.cleaned_data.get('create_user_id'),
                    'username': forms_obj.cleaned_data.get('username'),
                    'password': forms_obj.cleaned_data.get('password'),
                    'token': forms_obj.cleaned_data.get('token'),
                    'role_id_id': forms_obj.cleaned_data.get('role_id'),
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
            user_profile_objs = models.UserProfile.objects.filter(id=o_id)
            if user_profile_objs:
                if user_profile_objs[0].role_id_id == 1:
                    response.code = 300
                    response.msg = "不能删除管理员角色的用户"
                else:
                    user_profile_objs.update(status=3)
                    response.code = 200
                    response.msg = "删除成功"
            else:
                response.code = 300
                response.msg = "用户id异常"

        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'password': request.POST.get('password'),
                'status': request.POST.get('status'),
                'role_id': request.POST.get('role_id'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data['o_id']
                update_data = {
                    'status': forms_obj.cleaned_data['status'],
                    'role_id_id': forms_obj.cleaned_data['role_id'],
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


# 获取用户信息
def get_userinfo(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        token = request.GET.get('token')
        objs = models.UserProfile.objects.select_related('role_id').filter(token=token)

        if objs:
            obj = objs[0]
            response.code = 200
            response.data = {
                # 'token': obj.token,
                'id': obj.id,
                'username': obj.username,
                'access': json.loads(obj.role_id.access_name),
                'head_portrait': obj.head_portrait
            }
        else:
            response.code = 402
            response.msg = "token异常"
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)
