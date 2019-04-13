# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.db.models import Q

from publicFunc.condition_com import conditionCom
from api.forms.photo_library import AddForm, UpdateForm, SelectForm
import json


@account.is_token(models.UserProfile)
def photo_library(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            get_type = forms_obj.cleaned_data['get_type']
            # create_user_id = forms_obj.cleaned_data['create_user_id']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            # order = 'create_datetime'
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'group_id': '',
                'name': '__contains',
                'create_datetime': '',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            if get_type == "system":  # 获取系统分组
                q.add(Q(**{'create_user_id__isnull': True}), Q.AND)
                # objs = models.PhotoLibrary.objects.filter(create_user_id__isnull=True)
            elif get_type == "is_me":
                q.add(Q(**{'create_user_id': user_id}), Q.AND)

            objs = models.PhotoLibrary.objects.select_related('group').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'group_id': obj.group_id,
                    'img_url': obj.img_url,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count
            }
            response.note = {
                'id': "图片id",
                'group_id': "分组id",
                'img_url': '图片地址',
                'create_datetime': '创建时间',
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def photo_library_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 添加页面分组
        if oper_type == "add":
            form_data = {
                'create_user_id': user_id,
                'group_id': request.POST.get('group_id'),
                'img_url': request.POST.get('img_url'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                obj = models.PhotoLibrary.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            objs = models.PhotoLibrary.objects.filter(id=o_id, create_user_id=user_id)
            if objs:
                objs.delete()
                # 待优化，删除的同时删除七牛云资源
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
