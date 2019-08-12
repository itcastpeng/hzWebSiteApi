# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.db.models import Q
from publicFunc.condition_com import conditionCom
from api.forms.template import AddForm, UpdateForm, SelectForm, GetTabBarDataForm, UpdateClassForm, UserAddTemplateForm
from api.views_dir.page import page_base_data
from publicFunc.role_choice import admin_list
import json


@account.is_token(models.UserProfile)
def template(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            is_all = request.GET.get('is_all') #
            user_id = request.GET.get('user_id')
            obj = models.UserProfile.objects.get(id=user_id)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'name': '__contains',
                'template_class_id': '',
                'create_datetime': '',
            }
            q = conditionCom(request, field_dict)
            if obj.role_id in [7, '7'] and not is_all:
                q.add(Q(create_user_id=user_id), Q.AND)
            else:
                q.add(Q(create_user__role_id__in=admin_list), Q.AND)
            objs = models.Template.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                template_class_id = ''
                template_class_name = ''
                if obj.template_class:
                    template_class_id = obj.template_class_id
                    template_class_name = obj.template_class.name

                # 将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'share_qr_code': obj.share_qr_code,
                    'logo_img': obj.logo_img,
                    'thumbnail': obj.thumbnail,
                    'template_class_name': template_class_name,
                    'template_class_id': template_class_id,
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
                'share_qr_code': '分享二维码',
                'logo_img': 'logo图片',
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def template_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'create_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'thumbnail': request.POST.get('thumbnail'), # 缩略图
                'template_class_id': request.POST.get('template_class_id'), # 缩略图
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                template_obj = models.Template.objects.create(
                    create_user_id=forms_obj.cleaned_data.get('create_user_id'),
                    name=forms_obj.cleaned_data.get('name'),
                    thumbnail=forms_obj.cleaned_data.get('thumbnail'),
                    template_class_id=forms_obj.cleaned_data.get('template_class_id'),
                )
                page_group_obj = models.PageGroup.objects.create(
                    name="默认组",
                    template=template_obj
                )

                print('page_base_data -->', page_base_data)
                models.Page.objects.create(
                    name="首页",
                    page_group=page_group_obj,
                    data=json.dumps(page_base_data)
                )
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': template_obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
        elif oper_type == "delete":
            # 删除 ID
            objs = models.Template.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
                'logo_img': request.POST.get('logo_img'),
                'tab_bar_data': request.POST.get('tab_bar_data'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                # print("验证通过")
                # print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']
                logo_img = forms_obj.cleaned_data['logo_img']
                tab_bar_data = forms_obj.cleaned_data['tab_bar_data']
                update_data = {}
                if logo_img:
                    update_data['logo_img'] = logo_img
                if name:
                    update_data['name'] = name
                if tab_bar_data:
                    update_data['tab_bar_data'] = tab_bar_data

                # 更新数据
                models.Template.objects.filter(id=o_id).update(**update_data)

                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改模板分类id
        elif oper_type == "update_class":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'class_id': request.POST.get('class_id'),
            }

            forms_obj = UpdateClassForm(form_data)
            if forms_obj.is_valid():
                # print("验证通过")
                # print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                class_id = forms_obj.cleaned_data['class_id']

                # 更新数据
                models.Template.objects.filter(id=o_id).update(template_class_id=class_id)

                response.code = 200
                response.msg = "修改成功"

        # 客户创建模板
        elif oper_type == 'user_add_template':
            form_data = {
                'template_id':o_id
            }
            form_obj = UserAddTemplateForm(form_data)
            if form_obj.is_valid():
                template_id, data = form_obj.cleaned_data.get('template_id')
                data['create_user_id'] = user_id
                obj = models.Template.objects.create(**data)

                page_group_obj = models.PageGroup.objects.get(template_id=template_id)
                page_obj = models.Page.objects.get(page_group__template_id=template_id)
                page_group_obj = models.PageGroup.objects.create(
                    name=page_group_obj.name,
                    template_id=obj.id,
                    create_user_id=user_id,
                )

                models.Page.objects.create(
                    name=page_obj.name,
                    page_group=page_group_obj,
                    data=page_obj.data
                )

                response.code = 200
                response.msg = '创建成功'
                response.data = {
                    'id': obj.id
                }
            else:
                response.code = 301
                response.msg = json.load(form_obj.errors.as_json())

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
