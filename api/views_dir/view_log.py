from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from api.forms.view_log import SelectForm
from publicFunc.condition_com import conditionCom
import json


@account.is_token(models.UserProfile)
def view_log_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        objs = models.Page.objects.filter(create_datetime__isnull=False)
        for obj in objs:
            print('obj.id---------> ', obj.id)
            data = json.loads(obj.data)
            data['setting'] = [
                {
                    'title':'侧停分享',
                    'disabled': True,
                    'check': True,
                    'tpye':'shareSelect'
                },{
                    'title':'侧停客服',
                    'disabled': 'false',
                    'check': True,
                    'tpye':'customerSelect'
                },{
                    'title':'侧停技术支持',
                    'disabled': True,
                    'check': True,
                    'tpye':'supportSelect'
                },{
                    'title':'制作信息',
                    'disabled': True,
                    'check': True,
                    'tpye':'makeSelect'
                },
            ]
            obj.data = json.dumps(data)
            obj.save()


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









# @account.is_token(models.UserProfile)
def xcx_view_log_oper(request, oper_type):
    user_id = request.GET.get('user_id')
    response = Response.ResponseObj()
    if request.method == 'POST':
        pass

    else:

        # 记录日志
        if oper_type == 'record_log':

            template_id = request.GET.get('template_id')

            source = request.GET.get('source', 1) # 1微信小程序 2百度小程序
            log_data = {
                'user_id':user_id,
                'template_id':template_id,
                'source':source
            }
            if source in [1, '1']:
                applet_objs = models.ClientApplet.objects.filter(template_id=template_id)
                log_data['client_applet_id'] = applet_objs[0].id
            else:
                applet_objs = models.BaiduSmallProgramManagement.objects.filter(template_id=template_id)
                log_data['baidu_client_applet_id'] = applet_objs[0].id

            models.ViewCustomerSmallApplet.objects.create(**log_data) # 记录日志

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)

















