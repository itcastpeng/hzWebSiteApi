from hurong import models
from publicFunc import Response
from django.http import JsonResponse
from hurong.forms.xiaohongshu_phone_management import get_phone_work_status, get_phone_number, \
    get_xhs_unregistered_information, get_verification_code
from publicFunc.phone_management_platform import phone_management

import os, json, datetime, requests




# 手机 功能 管理
def xiaohongshu_phone_management(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "GET":

        # 获取手机工作状态(是否离线)(离线返回True)
        if oper_type == "get_phone_work_status":

            form_data = {
                'macaddr':request.GET.get('macaddr'),
                'phone_type':request.GET.get('phone_type'),
            }
            flag = True
            form_obj = get_phone_work_status(form_data)
            if form_obj.is_valid():
                macaddr = form_obj.cleaned_data.get('macaddr')
                phone_type = form_obj.cleaned_data.get('phone_type')

                objs = models.XiaohongshuPhone.objects.filter(
                    phone_type=phone_type,
                    macaddr=macaddr
                )
                if objs:
                    obj = objs[0]
                    now = datetime.datetime.today()
                    deletionTime = (now - datetime.timedelta(minutes=5))  # 当前时间减去5分钟
                    phone_log_objs = models.XiaohongshuPhoneLog.objects.filter(
                        parent=obj.id,
                        create_datetime__gte=deletionTime
                    ).order_by('-create_datetime')
                    if phone_log_objs:
                        flag = False

                    response.code = 200
                    response.data = {'flag': flag}
                    response.note = {
                        'flag': '如果为True 则异常'
                    }

                else:
                    response.code = 301
                    response.msg = '该手机不存在'
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 获取未使用的手机号 绑定关系
        elif oper_type == 'get_phone_number':
            form_data = {
                'iccid': request.GET.get('iccid'),
                'imsi': request.GET.get('imsi'),
            }
            form_obj = get_phone_number(form_data)
            if form_obj.is_valid():
                iccid = form_obj.cleaned_data.get('iccid')
                imsi = form_obj.cleaned_data.get('imsi')
                phone_objs = models.XiaohongshuPhone.objects.filter(
                    iccid=iccid,
                    imsi=imsi
                )
                if phone_objs:
                    phone_obj = phone_objs[0]
                    number_objs = models.PhoneNumber.objects.filter(phone=phone_obj)
                    if not number_objs:

                        number_objs = models.PhoneNumber.objects.filter(status=1, phone__isnull=True)
                        if number_objs:
                            number_obj = number_objs[0]
                            number_obj.phone_id = phone_objs[0].id # 将手机号和设备进行关联
                            number_obj.save()
                            phone_num = number_obj.phone_num

                        else:
                            response.code = 301
                            response.msg = '暂无可用手机号'
                            phone_num = ''

                    else:
                        phone_num = number_objs[0].phone_num

                    response.code = 200
                    response.data = {'phone_number': phone_num}

                else:
                    response.code = 301
                    response.msg = '该设备不存在'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 获取验证码
        elif oper_type == 'get_verification_code':
            form_data = {
                'phone_number': request.GET.get('phone_number')
            }
            form_obj = get_verification_code(form_data)
            if form_obj.is_valid():
                phone_number = form_obj.cleaned_data.get('phone_number')
                phone_management_objs = phone_management()
                phone_management_objs.login()
                verification_code = phone_management_objs.query_verification_code(phone_number)
                if verification_code:
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'verification_code': verification_code
                    }
                else:
                    response.code = 301
                    response.msg = '暂无验证码'

            else:
                response.code= 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 获取小红书未注册的账号信息
        elif oper_type == 'get_xhs_unregistered_information':
            form_data = {
                'get_info_number': request.GET.get('get_info_number', 1) # 获取几个信息
            }
            response.code = 301

            form_obj = get_xhs_unregistered_information(form_data)
            if form_obj.is_valid():
                get_info_number = int(form_obj.cleaned_data.get('get_info_number'))

                objs = models.XiaohongshuUserProfileRegister.objects.filter(
                    is_register=False,
                    register_datetime__isnull=True
                ) # is_register 未被注册 register_datetime 注册时间
                count = objs.count()
                if get_info_number > count:
                    msg = '当前未注册小红书账号低于{}条, 剩余{}条'.format(get_info_number, count)

                else:
                    data_list = []
                    for obj in objs[0: get_info_number]:
                        data_list.append({
                            'gender_id': obj.gender,
                            'gender': obj.get_gender_display(),
                            'head_portrait': obj.head_portrait,
                            'birthday': obj.birthday,
                            'name': obj.name,
                        })
                    response.code = 200
                    msg = '查询成功'
                    response.data = {
                        'ret_data': data_list,
                        'count': count
                    }

            else:
                msg = json.loads(form_obj.errors.as_json())

            response.msg = msg

        else:
            response.code = 402
            response.msg = "请求异常"

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
