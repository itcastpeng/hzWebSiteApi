from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from api.forms.view_log import SelectForm
from publicFunc.condition_com import conditionCom

@account.is_token(models.UserProfile)
def view_log_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        pass

    else:
        if oper_type == "get_view_data":
            form_objs = SelectForm(request.GET)
            if form_objs.is_valid():
                current_page = form_objs.cleaned_data['current_page']
                length = form_objs.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                    'client_applet_id': '',
                }
                q = conditionCom(request, field_dict)
                objs = models.ViewCustomerSmallApplet.objects.filter(q).order_by(order)
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    ret_data.append({
                        'customer_id': obj.customer_id,
                        'customer_name': obj.customer,
                    })


                response.code = 200
                response.msg = ''

            else:
                response.code = 301
                response.msg = form_objs.errors.as_json()

        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)






