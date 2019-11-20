from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from api.forms.view_log import SelectForm
from publicFunc.condition_com import conditionCom
from django.db.models import Count
from publicFunc.base64_encryption import b64decode
import json

# 后台操作
@account.is_token(models.UserProfile)
def view_log_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        pass


    else:

        # 查询日志
        if oper_type == "get_view_data":
            form_objs = SelectForm(request.GET)
            if form_objs.is_valid():
                current_page = form_objs.cleaned_data['current_page']
                length = form_objs.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                    'client_applet_id': '',
                    'source': '',
                }
                q = conditionCom(request, field_dict)
                objs = models.ViewCustomerSmallApplet.objects.select_related(
                    'customer'
                ).filter(
                    q
                ).values(
                    'customer_id', 'customer__name', 'source', 'customer__phone', 'customer__ip_address'
                ).annotate(Count('id'))

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    customer_id = obj.get('customer_id')
                    source = obj.get('source')
                    objs_detail = models.ViewCustomerSmallApplet.objects.filter(
                        customer_id=customer_id, source=source
                    ).order_by('create_datetime')

                    ret_data.append({
                        'intention_degree': 0,                              # 意向度
                        'access_permissions': '',                           # 访问权限
                        'visitors_id': customer_id,                         # 访客ID
                        'visitors': b64decode(obj.get('customer__name')),   # 访客
                        'terminal': obj.get('customer__ip_address'),        # 终端
                        'mobile_phone': obj.get('customer__phone'),         # 手机
                        'source_id': source,                                # 来源ID
                        'source': objs_detail[0].get_source_display(),      # 来源
                        'first_visit_to': objs_detail[0].create_datetime.strftime('%Y-%m-%d %H:%M:%S'), # 首次访问时间
                        'last_active_time': objs_detail.order_by(
                            '-create_datetime'
                        )[0].create_datetime.strftime('%Y-%m-%d %H:%M:%S'),# 最近活跃时间
                    })


                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'count':'',
                    'ret_data': ret_data
                }
                response.note = {
                    'intention_degree': '意向度',
                    'access_permissions': '访问权限',
                    'visitors_id': '访客ID',
                    'visitors': '访客',
                    'terminal': '终端',
                    'mobile_phone': '手机',
                    'source_id': '来源ID',
                    'source': '来源',
                    'first_visit_to': '首次访问时间',
                    'last_active_time': '最近活跃时间',
                }

            else:
                response.code = 301
                response.msg = form_objs.errors.as_json()


        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)








# 小程序操作
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
            log_type = request.GET.get('log_type', 1)
            source = request.GET.get('source', 1) # 1微信小程序 2百度小程序
            log_data = {
                'customer_id':user_id,
                'template_id':template_id,
                'source':source,
                'log_type': log_type
            }
            if source in [1, '1']:
                applet_objs = models.ClientApplet.objects.filter(template_id=template_id)
                log_data['client_applet_id'] = applet_objs[0].id
            else:
                applet_objs = models.BaiduSmallProgramManagement.objects.filter(template_id=template_id)
                log_data['baidu_client_applet_id'] = applet_objs[0].id

            models.ViewCustomerSmallApplet.objects.create(**log_data) # 记录日志

            response.code = 200
            response.msg = '记录成功'




        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)

















