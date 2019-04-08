# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.db.models import Q

from publicFunc.condition_com import conditionCom
from api.forms.compoment_library import AddForm, UpdateForm, SelectForm
import json


@account.is_token(models.UserProfile)
def compoment_library(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # get_type = forms_obj.cleaned_data['get_type']
            # create_user_id = forms_obj.cleaned_data['create_user_id']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = 'create_datetime'
            field_dict = {
                'compoment_library_class_id': '',
                'name': '__contains',
                'create_datetime': '',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)

            objs = models.CompomentLibrary.objects.select_related('compoment_library_class').filter(is_delete=False).filter(q).order_by(order)
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
                    'name': obj.name,
                    'data': obj.data,
                    'compoment_library_class_id': obj.compoment_library_class_id,
                    'compoment_library_class_name': obj.compoment_library_class.name,
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
                'id': "组件id",
                'name': "组件名称",
                'data': "组件数据",
                'compoment_library_class_id': "组件分类id",
                'compoment_library_class_name': "组件分类名称",
                'create_datetime': '创建时间',
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def compoment_library_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 添加
        if oper_type == "add":
            form_data = {
                'create_user_id': user_id,
                'name': request.POST.get('name'),
                'compoment_library_class_id': request.POST.get('compoment_library_class_id'),
                'data': request.POST.get('data'),
            }
            print('form_data -->', form_data)
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                obj = models.CompomentLibrary.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            objs = models.CompomentLibrary.objects.filter(id=o_id)
            if objs:
                objs.update(is_delete=True)
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
