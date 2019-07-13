

from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from hurong.forms.public_form import SelectForm
from publicFunc.condition_com import conditionCom
import json, requests, base64, time, os, datetime




@account.is_token(models.UserProfile)
def ask_little_red_book(request):
    response = Response.ResponseObj()
    if request.method == 'POST':
        pass

    else:
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            field_dict = {
                'id': '',
                'comments_status': '',
                'xhs_user_id': '',
            }

            q = conditionCom(request, field_dict)
            order = request.GET.get('order', '-create_datetime')
            objs = models.AskLittleRedBook.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                get_request_parameter = obj.get_request_parameter
                if get_request_parameter:
                    get_request_parameter = eval(get_request_parameter)

                post_request_parameter = obj.post_request_parameter
                if post_request_parameter:
                    post_request_parameter = eval(post_request_parameter)

                response_data = obj.response_data
                if response_data:
                    response_data = eval(response_data)

                ret_data.append({
                    'request_url': obj.request_url,
                    'get_request_parameter': get_request_parameter,
                    'post_request_parameter': post_request_parameter,
                    'response_data': response_data,
                    'request_type_id': obj.request_type,
                    'request_type': obj.get_request_type_display(),
                    'status_id': obj.status,
                    'status': obj.get_status_display(),
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'count': count
            }

        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)











