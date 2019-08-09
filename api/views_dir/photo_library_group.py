# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.db.models import Q
from publicFunc.role_choice import admin_list
from publicFunc.condition_com import conditionCom
from api.forms.photo_library_group import AddForm, UpdateForm, SelectForm
import json


@account.is_token(models.UserProfile)
def photo_library_group(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            get_type = forms_obj.cleaned_data['get_type']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = 'create_datetime'
            # field_dict = {
            #     'create_user_id': '',
            #     'name': '__contains',
            #     'create_datetime': '',
            # }
            # q = conditionCom(request, field_dict)
            # print('q -->', q)
            q = Q()

            if get_type == "system":  # 获取系统分组
                q.add(Q(create_user__role_id__in=admin_list), Q.AND)
            elif get_type == "is_me":
                q.add(Q(**{'create_user_id': user_id}), Q.AND)

            objs = models.PhotoLibraryGroup.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                # 获取分组下面的页面数据
                page_group_objs = obj.photolibrarygroup_set.all().order_by(order)
                children_data = []
                for page_group_obj in page_group_objs:
                    children_data.append({
                        'id': page_group_obj.id,
                        'name': page_group_obj.name
                    })

                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'children_data': children_data,
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
                'id': "分组id",
                'name': '分组名称',
                'children_data': '子分组数据',
                'create_datetime': '创建时间',
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def photo_library_group_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 添加页面分组
        if oper_type == "add":
            form_data = {
                'create_user_id': user_id,
                'parent_id': request.POST.get('parent_id'),
                'name': request.POST.get('name'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                obj = models.PhotoLibraryGroup.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            objs = models.PhotoLibraryGroup.objects.filter(id=o_id, create_user_id=user_id)
            if objs:
                obj = objs[0]
                # 如果当前分组下没有图片或者当前分组下不存在子分组
                if obj.photolibrary_set.all().count() == 0 and obj.photolibrarygroup_set.all().count() == 0:
                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 302
                    response.msg = "删除失败，该分组下存在图片或分组"

            else:
                response.code = 302
                response.msg = '删除ID不存在'

        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data['o_id']
                update_data = {
                    'name': forms_obj.cleaned_data['name'],
                }

                # 更新数据
                models.PhotoLibraryGroup.objects.filter(
                    id=o_id,
                    create_user_id=user_id
                ).update(**update_data)

                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
