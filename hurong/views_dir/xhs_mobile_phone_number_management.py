
from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from hurong.forms.xhs_mobile_phone_number_management import SelectForm, AddForm, UpdateForm
from publicFunc.condition_com import conditionCom
import json


# 手机号管理
def xhs_mobile_phone_number_management(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')

        # 查询手机短信
        if oper_type == 'get_phone_content':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']

                phone_number = request.GET.get('phone_number')

                field_dict = {
                    'id': '',
                    'gender': '',
                    'name': '__contains',
                    'uid': '__contains',
                    'is_register': '',
                }
                q = conditionCom(request, field_dict)

                objs = models.text_messages_received_cell_phone_number.objects.select_related(
                    'phone'
                ).filter(
                    q,
                    phone__phone_num=phone_number
                ).order_by('-receiving_time')
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    ret_data.append({
                        'id': obj.id,
                        'message_content': obj.message_content,
                        'receiving_time': obj.receiving_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'phone_id': obj.phone_id,
                        'serial_number': obj.serial_number,
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count
                }

        # 查询手机号
        elif oper_type == 'get_phone_number':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                field_dict = {
                    'id': '',
                    'phone_num': '__contains',
                }
                q = conditionCom(request, field_dict)
                order = request.GET.get('order')

                objs = models.PhoneNumber.objects.filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    ret_data.append({
                        'id': obj.id,
                        'phone_id': obj.phone_id,
                        'phone_name': obj.phone.name,
                        'phone_num': obj.phone_num,
                        'status_id': obj.status,
                        'status': obj,
                        'remark': obj.remark,
                        'expire_date': obj.expire_date,
                        'create_datetime': obj.create_datetime,
                    })

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:

        form_data = {
            'phone_number': request.POST.get('phone_number'),
        }

        # 添加手机号
        if oper_type == 'add':
            form_obj = AddForm(form_data)
            if form_obj.is_valid():
                pass

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        elif oper_type == 'update':
            form_obj = UpdateForm(form_data)
            if form_obj.is_valid():
                pass

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)