from hurong import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.equipment_management import AddForm, SelectForm, UpdateForm
from publicFunc.public import get_traffic_information
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
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'status': '',
                'select_type': '',
                'keywords': '__contains',
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.XiaohongshuFugai.objects.filter(q).order_by(order)
            print(objs)
            count = objs.count()

            if length != 0:
                if count < 10:
                    current_page = 1
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                #  将查询出来的数据 加入列表
                update_datetime = ""
                if obj.update_datetime:
                    update_datetime = obj.update_datetime.strftime('%Y-%m-%d %H:%M:%S')

                keywords = "({select_type}) {keywords}".format(
                    keywords=obj.keywords,
                    select_type=obj.get_select_type_display()
                )
                ret_data.append({
                    'id': obj.id,
                    'keywords': keywords,
                    'url': obj.url,
                    'rank': obj.rank,
                    'biji_num': obj.biji_num,
                    'status': obj.get_status_display(),
                    'status_id': obj.status,
                    'select_type': obj.get_select_type_display(),
                    'select_type_id': obj.select_type,
                    'create_user__username': obj.create_user.username,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'update_datetime': update_datetime,
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'status_choices': models.XiaohongshuFugai.status_choices,
                'select_type_choices': models.XiaohongshuFugai.select_type_choices,
            }
            response.note = {
                'id': "下拉词id",
                'keywords': "搜索词",
                'url': "匹配url",
                'rank': "排名",
                'biji_num': "笔记数",
                'status': "状态",
                'status_id': "状态id",
                'select_type': "搜索类型",
                'select_type_id': "搜索类型id",
                'create_user__username': "创建人",
                'create_datetime': "创建时间",
                'update_datetime': "更新时间",
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
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
                ret_json = get_traffic_information(select_number)
                if ret_json.get('code') != 0:
                    models.MobileTrafficInformation.objects.create(
                        select_number=select_number,
                        errmsg=ret_json.get('msg')
                    )
                else:
                    models.MobileTrafficInformation.objects.create(**{
                        'select_number': select_number,
                        'cardbaldata': ret_json.get('cardbaldata'),  # 剩余流量
                        'cardenddate': ret_json.get('cardenddate'),  # 卡到期时间
                        'cardimsi': ret_json.get('cardimsi'),  # ismi号
                        'cardno': ret_json.get('cardno'),  # 卡编号
                        'cardnumber': ret_json.get('cardnumber'),  # 卡号
                        'cardstatus': ret_json.get('cardstatus'),  # 用户状态
                        'cardstartdate': ret_json.get('cardstartdate'),  # 卡开户时间
                        'cardtype': ret_json.get('cardtype'),  # 套餐类型
                        'cardusedata': ret_json.get('cardusedata'),  # 已用流量
                    })

                response.code = 200
                response.msg = '创建成功'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == 'update':
            form_obj = UpdateForm(form_data)
            if form_obj.is_valid():
                select_number = form_obj.cleaned_data.get('select_number')
                objs = models.MobileTrafficInformation.objects.filter(id=o_id)
                objs.update(select_number=select_number)
                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 删除
        elif oper_type == 'delete':
            models.MobilePhoneRechargeInformation.objects.filter(equipment_package_id=o_id).delete()
            models.MobileTrafficInformation.objects.filter(id=o_id).delete()
            response.code = 200
            response.msg = '删除成功'

        else:

            response.code = 402
            response.msg = "请求异常"

    else:

        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
