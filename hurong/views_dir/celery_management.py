from django.http import HttpResponse
from publicFunc.phone_management_platform import phone_management

from hurong import models
import datetime

# 定期删除 设备日志
def delete_phone_log(request):
    now_date = datetime.date.today()
    last_there_days = (now_date - datetime.timedelta(days=2))
    objs = models.XiaohongshuPhoneLog.objects.filter(
        create_datetime__lt=last_there_days
    )
    objs.delete()

    return HttpResponse('')


# 获取 手机号短信
def celery_get_phone_content(request):
    phone_management_objs = phone_management()
    data_list = phone_management_objs.get_all_information_day()

    for data in data_list:
        serial_number = data.get('serial_number') # 流水号
        content = data.get('content')             # 信息
        date_time = data.get('date_time')         # 接收信息时间
        phone_number = data.get('phone_number')   # 接收信息手机号

        objs = models.text_messages_received_cell_phone_number.objects.filter(
            serial_number=serial_number,
        )
        if not objs:
            phone_objs = models.PhoneNumber.objects.filter(phone_num=phone_number)
            if phone_objs:
                phone_obj = phone_objs[0]
                models.text_messages_received_cell_phone_number.objects.create(
                    serial_number=serial_number,
                    phone_id=phone_obj.id,
                    message_content=content,
                    receiving_time=date_time,
                )


    return HttpResponse('')



















