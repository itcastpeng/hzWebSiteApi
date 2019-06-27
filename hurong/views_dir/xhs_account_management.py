from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from hurong.forms.xhs_account_management import SelectForm
from publicFunc.condition_com import conditionCom
import json


@csrf_exempt
@account.is_token(models.UserProfile)
def xhs_account_management(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')

        # 查询小红书所有账号
        if oper_type == 'get_xhs_account':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                    'gender': '',
                    'name': '__contains',
                    'uid': '__contains',
                    'is_register': '',
                }
                q = conditionCom(request, field_dict)
                objs = models.XiaohongshuUserProfileRegister.objects.filter(
                    q,

                ).order_by(order)
                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    register_datetime = obj.register_datetime
                    if register_datetime:
                        register_datetime = register_datetime.strftime('%Y-%m-%d %H:%M:%S')

                    ret_data.append({
                        'id':obj.id,
                        'uid':obj.uid,
                        'name':obj.name,
                        'head_portrait':obj.head_portrait,
                        'gender':obj.gender,
                        'birthday':obj.birthday,
                        'is_register':obj.is_register,
                        'register_datetime':register_datetime,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count':count,
                }
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)












