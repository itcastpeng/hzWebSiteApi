from django.http import HttpResponse
from publicFunc.phone_management_platform import phone_management
from hurong import models
from publicFunc.public import get_traffic_information as get_phone_info, query_device_recharge_information
from publicFunc.weixin.workWeixin.workWeixinApi import WorkWeixinApi
import datetime, time, random, requests, json



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


# 查询 流量信息
def get_traffic_information(request):
    print('-=-------------------------------------')
    objs = models.MobileTrafficInformation.objects.filter(
        # select_number__isnull=False
        id__gte=66
    )
    for obj in objs:
        print('obj.id------------------> ', obj.id)
        ret_json = get_phone_info(obj.select_number)
        if ret_json.get('code') != 0:
            obj.errmsg = ret_json.get('msg')
            obj.save()

        else:
            cardbaldata = ret_json.get('cardbaldata')
            cardimsi = ret_json.get('cardimsi')
            obj.cardbaldata = cardbaldata                   # 剩余流量
            obj.cardenddate = ret_json.get('cardenddate')   # 卡到期时间
            obj.cardimsi = cardimsi                         # ismi号
            obj.cardno = ret_json.get('cardno')             # 卡编号
            obj.cardnumber = ret_json.get('cardnumber')     # 卡号
            obj.cardstatus = ret_json.get('cardstatus')     # 用户状态
            obj.cardstartdate = ret_json.get('cardstartdate')  # 卡开户时间
            obj.cardtype = ret_json.get('cardtype')         # 套餐类型
            obj.cardusedata = ret_json.get('cardusedata')   # 已用流量
            obj.errmsg = ''
            obj.save()

            work_obj = WorkWeixinApi()
            try:
                if cardbaldata and float(cardbaldata) <= 500:
                    content = '流量低于五百兆提醒, 查询号码:{}, 剩余流量:{}, ISMI号:{}'.format(obj.select_number, cardbaldata, cardimsi)
                    # work_obj.message_send('HeZhongGaoJingJianCe', content)  # 张聪

                info_json = query_device_recharge_information(obj.select_number)
                if info_json.get('data_list'):
                    for i in info_json.get('data_list'):
                        info_objs = models.MobilePhoneRechargeInformation.objects.filter(
                            equipment_package=i.get('pkName'),
                            prepaid_phone_time=i.get('payTime'),
                            equipment_id=obj.id,
                        )
                        if not info_objs:
                            models.MobilePhoneRechargeInformation.objects.create(
                                equipment_package=i.get('pkName'),
                                prepaid_phone_time=i.get('payTime'),
                                equipment_id=obj.id,
                            )
            except Exception as e:
                content = '鹏---获取流量 报错---> {}'.format(e)
                work_obj.message_send('HeZhongGaoJingJianCe', content)

    return HttpResponse('')






