from hurong import models
from publicFunc import Response
from django.http import JsonResponse
from hurong.forms.xiaohongshu_phone_management import get_phone_work_status
import os, json, datetime





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
                    deletionTime = (now - datetime.timedelta(minutes=5))  # 当前时间减去两小时
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

        else:
            response.code = 402
            response.msg = "请求异常"

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
