# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.page import AddForm, UpdateForm, CopyForm
import json

page_base_data = {
    'topData': {
        'type': 'pageTop',
        'title': '顶部标题名称',
        'style': {
            'backgroundColor': '#ffffff',
            'color': '#000000'
        }
    },
    'itemData': []
}
#
# @account.is_token(models.UserProfile)
# def page(request):
#     response = Response.ResponseObj()
#     if request.method == "GET":
#         forms_obj = SelectForm(request.GET)
#         if forms_obj.is_valid():
#             current_page = forms_obj.cleaned_data['current_page']
#             length = forms_obj.cleaned_data['length']
#             print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
#             order = request.GET.get('order', '-create_datetime')
#             field_dict = {
#                 'id': '',
#                 'template_id': '',
#                 'name': '__contains',
#                 'create_datetime': '',
#             }
#             q = conditionCom(request, field_dict)
#             print('q -->', q)
#             objs = models.Page.objects.filter(q).order_by(order)
#             count = objs.count()
#
#             if length != 0:
#                 start_line = (current_page - 1) * length
#                 stop_line = start_line + length
#                 objs = objs[start_line: stop_line]
#
#             # 返回的数据
#             ret_data = []
#
#             for obj in objs:
#
#                 #  将查询出来的数据 加入列表
#                 ret_data.append({
#                     'id': obj.id,
#                     'name': obj.name,
#                     'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
#                 })
#             #  查询成功 返回200 状态码
#             response.code = 200
#             response.msg = '查询成功'
#             response.data = {
#                 'ret_data': ret_data,
#                 'data_count': count,
#             }
#             response.note = {
#                 'id': "页面分组id",
#                 'name': '页面分组名称',
#                 'create_datetime': '创建时间',
#             }
#         else:
#             response.code = 402
#             response.msg = "请求异常"
#             response.data = json.loads(forms_obj.errors.as_json())
#     return JsonResponse(response.__dict__)
#


@account.is_token(models.UserProfile)
def page_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'create_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'page_group_id': request.POST.get('page_group_id'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                create_data = {
                    'create_user_id': forms_obj.cleaned_data.get('create_user_id'),
                    'name': forms_obj.cleaned_data.get('name'),
                    'page_group_id': forms_obj.cleaned_data.get('page_group_id'),
                    'data': json.dumps(page_base_data)
                }
                print('create_data -->', create_data)
                obj = models.Page.objects.create(**create_data)
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

        # 复制页面
        elif oper_type == "copy":
            form_data = {
                'page_id': o_id,
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = CopyForm(form_data)
            if forms_obj.is_valid():
                page_id = forms_obj.cleaned_data.get('page_id')
                objs = models.Page.objects.filter(id=page_id)
                if objs:
                    old_obj = objs[0]
                    page_name = old_obj.name + ' - 复制'
                    obj = models.Page.objects.create(
                        name=page_name,
                        page_group=old_obj.page_group,
                        data=old_obj.data,
                        create_user_id=user_id
                    )
                    response.code = 200
                    response.msg = "复制成功"
                    response.data = {
                        'testCase': obj.id,
                        'id': obj.id,
                    }
                else:
                    response.code = 301
                    response.msg = "id异常"
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            objs = models.Page.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'

        elif oper_type == "update":
            # 获取需要修改的信息
            print('request.POST -->', request.POST)
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
                'data': request.POST.get('data'),
                'page_group_id': request.POST.get('page_group_id'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                update_data = {}
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']
                data = forms_obj.cleaned_data['data']
                page_group_id = forms_obj.cleaned_data['page_group_id']
                print('data -->', data)
                if name:
                    update_data['name'] = name
                if data:
                    update_data['data'] = data

                if page_group_id:
                    update_data['page_group_id'] = page_group_id

                # 更新数据
                models.Page.objects.filter(id=o_id).update(**update_data)

                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        if oper_type == "get_page_data":
            page_objs = models.Page.objects.filter(id=o_id)
            if page_objs:
                page_obj = page_objs[0]
                response.code = 200
                response.data = page_obj.data
            else:
                print('page_objs -->', page_objs)
                response.code = 302
                response.msg = "页面id异常"
        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)
