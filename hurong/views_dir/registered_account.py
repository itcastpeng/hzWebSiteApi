from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from hurong.forms.public_form import SelectForm
from publicFunc.condition_com import conditionCom
import json


@csrf_exempt
@account.is_token(models.UserProfile)
def registered_account(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')

        # 查询小红书所有账号
        if oper_type == 'get_xhs_unregistered_account':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                    'uid': '__contains',
                    'name': '__contains',
                    'gender': '',
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
                    if obj.register_datetime:
                        register_datetime =obj.register_datetime.strftime('%Y-%m-%d %H:%M:%S')

                    ret_data.append({
                        'id':obj.id,
                        'name':obj.name,
                        'uid':obj.uid,
                        'gender_id':obj.gender,
                        'remark':obj.remark,
                        'gender':obj.get_gender_display(),
                        'birthday':obj.birthday,
                        'is_register':obj.is_register,
                        'register_datetime':register_datetime,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'gender_choices': [{'id': i[0], 'name': i[1]} for i in models.XiaohongshuUserProfileRegister.gender_choices],
                    'count':count,
                }
                response.note = {
                    'name': '账号昵称',
                    'uid': '小红书后台博主ID',
                    'gender_id': '性别ID',
                    'gender': '性别名称',
                    'birthday': '生日',
                    'is_register': '是否已经被注册',
                    'register_datetime': '注册时间',
                    'create_datetime': '创建时间',
                }
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)












