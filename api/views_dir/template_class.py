# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse

from publicFunc.condition_com import conditionCom
from api.forms.template_class import AddForm, UpdateForm, SelectForm, GetTabBarDataForm
import json
from api.views_dir.page import page_base_data


@account.is_token(models.UserProfile)
def template_class(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
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
            # print('q -->', q)
            objs = models.TemplateClass.objects.filter(q).order_by(order)
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
                'id': "模板id",
                'name': '模板名称',
                'create_datetime': '创建时间',
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def template_class_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'create_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                obj = models.TemplateClass.objects.create(
                    create_user_id=forms_obj.cleaned_data.get('create_user_id'),
                    name=forms_obj.cleaned_data.get('name')
                )

                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
        elif oper_type == "delete":
            # 删除 ID
            objs = models.Template.objects.filter(template_class_id=o_id)
            if objs:
                response.code = 0
                response.msg = "当前模板分类下还存在模板，请移除后在进行删除操作"
            else:
                models.TemplateClass.objects.filter(id=o_id).delete()
                response.code = 200
                response.msg = "删除成功"
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                # print("验证通过")
                # print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']

                # 更新数据
                models.Template.objects.filter(id=o_id).update(name=name)

                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        # 获取底部导航数据
        if oper_type == "get_tab_bar_data":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id
            }

            forms_obj = GetTabBarDataForm(form_data)
            if forms_obj.is_valid():
                # print("验证通过")
                # print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']

                template_objs = models.Template.objects.filter(id=o_id)
                if template_objs:
                    response.code = 200
                    response.data = {
                        'data': template_objs[0].tab_bar_data
                    }
                else:
                    response.code = 301
                    response.msg = "模板id异常"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
