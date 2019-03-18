from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.renewal import AddForm, UpdateForm, DeleteForm, SelectForm
from publicFunc.base64_encryption import b64decode
import json


# cerf  token验证 用户展示模块
@account.is_token(models.Userprofile)
def renewal(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'price': '__contains',
                'the_length': '',
                'renewal_number_days': '',
                'create_date': '',
                'create_user_id': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.renewal_management.objects.filter(q).order_by(order)
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
                    'price': obj.price,
                    'original_price': obj.original_price,
                    'the_length_id': obj.the_length,
                    'the_length': obj.get_the_length_display(),
                    'create_user_id': obj.create_user_id,
                    'create_user__name': b64decode(obj.create_user.name),
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
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
                'price': '钱数',
                'the_length_id': '时长ID(一个月， 一年....)',
                'the_length': '时长',
                'create_user_id': '创建人ID',
                'create_user__name': '创建人名字',
                'original_price': '原价',
                'create_date': '创建时间',
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.Userprofile)
def renewal_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    form_data = {
        'o_id': o_id,
        'user_id': request.GET.get('user_id'),
        'price': request.POST.get('price'),
        'original_price': request.POST.get('original_price'),  # 原价
        'the_length': request.POST.get('the_length')
    }
    print('form_data------> ', form_data)
    if request.method == "POST":

        # 添加续费
        if oper_type == "add":
            form_obj = AddForm(form_data)
            if form_obj.is_valid():
                the_length, renewal_number_days = form_obj.cleaned_data.get('the_length')

                models.renewal_management.objects.create(**{
                    'price': form_obj.cleaned_data.get('price'),
                    'original_price': form_obj.cleaned_data.get('original_price'),
                    'the_length': the_length,
                    'renewal_number_days': renewal_number_days,
                    'create_user_id': form_obj.cleaned_data.get('user_id')
                })
                response.code = 200
                response.msg = '添加成功'
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 修改续费
        elif oper_type == "update":
            form_obj = UpdateForm(form_data)
            if form_obj.is_valid():
                o_id, objs = form_obj.cleaned_data.get('o_id')
                the_length, renewal_number_days = form_obj.cleaned_data.get('the_length')
                objs.update(**{
                    'price': form_obj.cleaned_data.get('price'),
                    'original_price': form_obj.cleaned_data.get('original_price'),
                    'the_length': the_length,
                    'renewal_number_days': renewal_number_days,
                })
                response.code = 200
                response.msg = '修改成功'
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 删除续费
        elif oper_type == "delete":
            form_obj = DeleteForm(form_data)
            if form_obj.is_valid():
                o_id, objs = form_obj.cleaned_data.get('o_id')
                objs.delete()
                response.code = 200
                response.msg = '删除成功'
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)
