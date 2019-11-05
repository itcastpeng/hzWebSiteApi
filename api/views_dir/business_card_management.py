from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.business_card_management import AddForm, UpdateForm, SelectForm
import json

# 名片
@account.is_token(models.UserProfile)
def business_card_management(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'name': '__contains',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.BusinessCard.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                ret_data.append({
                    'id': obj.id,
                    'create_user_id': obj.create_user_id,
                    'name': obj.name,                                       # 名称
                    'phone': obj.phone,                                     # 电话
                    'jobs': obj.jobs,                                       # 职位
                    'email': obj.email,                                     # 邮箱
                    'wechat_num': obj.wechat_num,                           # 微信号
                    'address': obj.address,                                 # 地址
                    'heading': obj.heading,                                 # 头像
                    'about_me': obj.about_me,                               # 关于我
                    'enterprise_name': obj.create_user.enterprise_name,                               # 关于我
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            response.note = {
                'id': '名片ID',
                'create_user_id': '创建人ID',
                'name': '名称',
                'phone': '电话',
                'jobs': '职位',
                'email': '邮箱',
                'wechat_num': '微信号',
                'address': '地址',
                'heading': '头像',
                'about_me': '关于我',
                'create_date': '创建时间',
            }

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def business_card_management_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    form_data = {
        'o_id': o_id,
        'create_user_id': user_id,
        'name': request.POST.get('name'),                   # 名称
        'phone': request.POST.get('phone'),                 # 电话
        'jobs': request.POST.get('jobs'),                   # 职位
        'email': request.POST.get('email'),                 # 邮箱
        'wechat_num': request.POST.get('wechat_num'),       # 微信号
        'address': request.POST.get('address'),             # 地址
        'heading': request.POST.get('heading'),             # 头像
        'about_me': request.POST.get('about_me'),           # 关于我
    }
    if request.method == "POST":

        # 添加名片数据
        if oper_type == "add":
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                obj = models.BusinessCard.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改名片数据
        elif oper_type == "update":
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data.get('o_id')
                update_data = {
                    'create_user_id': forms_obj.cleaned_data.get('create_user_id'),
                    'name': forms_obj.cleaned_data.get('name'),
                    'phone': forms_obj.cleaned_data.get('phone'),
                    'jobs': forms_obj.cleaned_data.get('jobs'),
                    'email': forms_obj.cleaned_data.get('email'),
                    'wechat_num': forms_obj.cleaned_data.get('wechat_num'),
                    'address': forms_obj.cleaned_data.get('address'),
                    'heading': forms_obj.cleaned_data.get('heading'),
                    'about_me': forms_obj.cleaned_data.get('about_me'),
                }

                # 更新数据
                models.BusinessCard.objects.filter(id=o_id).update(**update_data)
                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除名片数据
        elif oper_type == "delete":
            objs = models.BusinessCard.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '删除ID不存在'


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
