from hurong import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.equipment_management import AddForm, SelectForm, UpdateForm
from hz_website_api_celery.tasks import get_traffic_information
import requests, datetime, json


# 设备管理 (手机 流量 操作 查询充值话费)


@account.is_token(models.UserProfile)
def equipment_management(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'cardbaldata': '__contains',
                'select_number': '__contains',
                'cardnumber': '__contains',
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.MobileTrafficInformation.objects.filter(q).order_by(order)
            print(objs)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                cardstartdate = obj.cardstartdate
                if obj.cardstartdate:
                    cardstartdate = obj.cardstartdate.strftime('%Y-%m-%d %H:%M:%S')

                cardenddate = obj.cardenddate
                if obj.cardenddate:
                    cardenddate = obj.cardenddate.strftime('%Y-%m-%d %H:%M:%S')

                ret_data.append({
                    'id': obj.id,
                    'cardimsi': obj.cardimsi,
                    'cardstatus': obj.cardstatus,
                    'cardtype': obj.cardtype,
                    'cardusedata': obj.cardusedata,
                    'cardno': obj.cardno,
                    'cardbaldata': obj.cardbaldata,
                    'select_number': obj.select_number,
                    'cardnumber': obj.cardnumber,
                    'cardstartdate': cardstartdate,
                    'cardenddate': cardenddate,
                    'errmsg': obj.errmsg,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            response.note = {
                'id': 'ID',
                'cardimsi': 'ISMI号',
                'cardstatus': '用户状态',
                'cardtype': '套餐类型',
                'cardusedata': '已用流量',
                'cardno': '卡编号',
                'cardbaldata': '剩余流量',
                'select_number': '查询号码',
                'cardnumber': '卡号',
                'cardstartdate': '卡开户时间',
                'cardenddate': '卡到期时间',
                'errmsg': '错误日志',
                'create_datetime': '创建时间',
            }
        else:
            response.code = 301
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def equipment_management_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "POST":

        form_data = {
            'o_id': o_id,
            'select_number': request.POST.get('select_number'),
        }

        # 添加
        if oper_type == "add":
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                select_number = forms_obj.cleaned_data.get('select_number')
                for i in select_number:
                    models.MobileTrafficInformation.objects.create(
                        select_number=i
                    )
                get_traffic_information.delay()
                response.code = 200
                response.msg = '创建成功'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'update':
            form_obj = UpdateForm(form_data)
            if form_obj.is_valid():
                select_number = form_obj.cleaned_data.get('select_number')
                models.MobilePhoneRechargeInformation.objects.filter(equipment_id=o_id).delete()
                objs = models.MobileTrafficInformation.objects.filter(id=o_id)
                objs.update(**{
                    'select_number':select_number,
                    'cardbaldata': '',
                    'cardenddate': None,
                    'cardimsi': '',
                    'cardno':'',
                    'cardnumber':'',
                    'cardstatus':'',
                    'cardstartdate':None,
                    'cardtype':'',
                    'cardusedata':'',
                })

                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 删除
        elif oper_type == 'delete':
            models.MobilePhoneRechargeInformation.objects.filter(equipment_id=o_id).delete()
            models.MobileTrafficInformation.objects.filter(id=o_id).delete()
            response.code = 200
            response.msg = '删除成功'

        else:

            response.code = 402
            response.msg = "请求异常"

    else:

        # 查询设备充值信息
        if oper_type == 'get_recharge_information':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                    'equipment_id': '',
                    'equipment_package': '',
                    'create_datetime': '__contains',
                }

                q = conditionCom(request, field_dict)

                objs = models.MobilePhoneRechargeInformation.objects.filter(q).order_by(order)
                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:

                    ret_data.append({
                        'equipment_id': obj.equipment_id,
                        'prepaid_phone_time': obj.equipment_package,
                        'equipment_package': obj.prepaid_phone_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count
                }
                response.note = {
                    'equipment_id': '设备ID',
                    'prepaid_phone_time': '充值时间',
                    'equipment_package': '设备套餐',
                    'create_datetime': '创建时间',
                }

            else:
                response.code = 301
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())
        else:

            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
