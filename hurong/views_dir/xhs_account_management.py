from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from hurong.forms.public_form import SelectForm
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
                    'phone_id': '__contains',
                    'name': '__contains',
                    'xiaohongshu_id': '__contains',
                    'home_url': '__contains',
                    'xhs_version': '__contains',
                    'phone_id__name': '__contains',
                }
                q = conditionCom(request, field_dict)
                objs = models.XiaohongshuUserProfile.objects.select_related(
                    'phone_id'
                ).filter(
                    q,
                ).order_by(order)
                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    phone_id = ''
                    if obj.phone_id:
                        phone_id = obj.phone_id_id

                    phone_name = ''
                    if obj.phone_id.name:
                        phone_name = obj.phone_id.name
                    ret_data.append({
                        'id':obj.id,
                        'name':obj.name,
                        'phone_id':phone_id,
                        'phone_number':obj.phone_id.phone_num,
                        'xiaohongshu_id':obj.xiaohongshu_id,
                        'xhs_version':obj.xhs_version,
                        'package_version':obj.package_version,
                        'home_url':obj.home_url,
                        'phone_name':phone_name,
                        'phone_type':obj.phone_id.get_phone_type_display(),
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












