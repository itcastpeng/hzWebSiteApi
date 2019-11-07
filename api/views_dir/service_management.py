from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.service_management import AddForm, UpdateForm, SelectForm
import json

# 服务
@account.is_token(models.UserProfile)
def service_management(request):
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
            objs = models.ServiceTable.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                try:
                    main_figure = obj.main_figure
                except Exception:
                    main_figure = json.loads(obj.main_figure)

                ret_data.append({
                    'id': obj.id,
                    'create_user_id': obj.create_user_id,
                    'name': obj.name,
                    'abstract': obj.abstract,
                    'main_figure': main_figure,
                    'service_classification': obj.service_classification,
                    'price_type': obj.price_type,
                    'price': obj.price,
                    'promotion_price': obj.promotion_price,
                    'limit_amount': obj.limit_amount,
                    'virtual_order_volume': obj.virtual_order_volume,
                    'service_detail': obj.service_detail,
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
                'id': '服务ID',
                'create_user_id': '创建人ID',
                'name': '服务名称',
                'abstract': '服务简介',
                'main_figure': '主图',
                'service_classification': '服务分类',
                'price_type': '价格类型',
                'price': '价格',
                'promotion_price': '促销价格',
                'limit_amount': '限制总数',
                'virtual_order_volume': '虚拟订单量',
                'create_date': '创建时间',
            }

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def service_management_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    form_data = {
        'o_id': o_id,
        'create_user_id': user_id,
        'name': request.POST.get('name'),                                       # 名称
        'abstract': request.POST.get('abstract'),                               # 摘要
        'main_figure': request.POST.get('main_figure'),                         # 主图
        'service_classification': request.POST.get('service_classification'),   # 服务分类
        'price_type': request.POST.get('price_type', 1),                        # 价格类型
        'price': request.POST.get('price', 0),                                  # 价格
        'promotion_price': request.POST.get('promotion_price', 0),              # 促销价格
        'limit_amount': request.POST.get('limit_amount', 0),                    # 限制总量
        'virtual_order_volume': request.POST.get('virtual_order_volume', 0),    # 虚拟订单量
        'service_detail': request.POST.get('service_detail'),    # 服务详情
    }
    if request.method == "POST":

        # 添加服务数据
        if oper_type == "add":
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                obj = models.ServiceTable.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改服务数据
        elif oper_type == "update":
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data.get('o_id')
                update_data = {
                    'create_user_id': forms_obj.cleaned_data.get('create_user_id'),
                    'name': forms_obj.cleaned_data.get('name'),
                    'abstract': forms_obj.cleaned_data.get('abstract'),
                    'main_figure': forms_obj.cleaned_data.get('main_figure'),
                    'service_classification': forms_obj.cleaned_data.get('service_classification'),
                    'price_type': forms_obj.cleaned_data.get('price_type'),
                    'price': forms_obj.cleaned_data.get('price'),
                    'promotion_price': forms_obj.cleaned_data.get('promotion_price'),
                    'limit_amount': forms_obj.cleaned_data.get('limit_amount'),
                    'virtual_order_volume': forms_obj.cleaned_data.get('virtual_order_volume'),
                    'service_detail': forms_obj.cleaned_data.get('service_detail'),
                }

                # 更新数据
                models.ServiceTable.objects.filter(id=o_id).update(**update_data)
                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除服务数据
        elif oper_type == "delete":
            objs = models.ServiceTable.objects.filter(id=o_id)
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
