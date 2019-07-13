from django.http import HttpResponse
from publicFunc.phone_management_platform import phone_management
from hurong import models
from publicFunc.public import get_traffic_information as get_phone_info, query_device_recharge_information
from publicFunc.public import send_error_msg
import datetime, time, random, requests, json



# 定期删除 设备日志
def delete_phone_log(request):
    try:
        now_date = datetime.date.today()
        last_there_days = (now_date - datetime.timedelta(days=2))
        objs = models.XiaohongshuPhoneLog.objects.filter(
            create_datetime__lt=last_there_days
        )
        objs.delete()
    except Exception as e:
        content = '{} \n 定期删除 设备日志报错\n错误:{}'.format(datetime.datetime.today(), e)
        send_error_msg(content, 1)
    return HttpResponse('')


# 获取 手机号短信
def celery_get_phone_content(request):
    try:
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
    except Exception as e:
        content = '{} \n 获取 手机号短信报错\n错误:{}'.format(datetime.datetime.today(), e)
        send_error_msg(content, 1)

    return HttpResponse('')


# 查询 流量信息
def get_traffic_information(request):
    try:
        objs = models.MobileTrafficInformation.objects.filter(
            select_number__isnull=False
        )
        for obj in objs:
            ret_json = get_phone_info(obj.select_number)
            if ret_json.get('code') != 0:
                obj.errmsg = ret_json.get('msg')
                obj.save()

            else:
                cardbaldata = ret_json.get('cardbaldata')
                cardimsi = ret_json.get('cardimsi')
                cardstatus = ret_json.get('cardstatus')

                phone_objs = models.XiaohongshuPhone.objects.filter(imsi=cardimsi)
                if phone_objs:
                    phone_obj = phone_objs[0]
                    obj.phone_id = phone_obj.id  # 外键到手机

                obj.cardbaldata = cardbaldata                   # 剩余流量
                obj.cardenddate = ret_json.get('cardenddate')   # 卡到期时间
                obj.cardimsi = cardimsi                         # ismi号
                obj.cardno = ret_json.get('cardno')             # 卡编号
                obj.cardnumber = ret_json.get('cardnumber')     # 卡号
                obj.cardstatus = cardstatus                     # 用户状态
                obj.cardstartdate = ret_json.get('cardstartdate')  # 卡开户时间
                obj.cardtype = ret_json.get('cardtype')         # 套餐类型
                obj.cardusedata = ret_json.get('cardusedata')   # 已用流量
                obj.errmsg = ''
                obj.save()

                flag = False
                if cardstatus != '已停用':
                    flag = True

                if flag and cardbaldata and float(cardbaldata) <= 500:
                    content = '{} \n 流量低于五百兆提醒, 查询号码:{}, 剩余流量:{}, ISMI号:{}'.format(datetime.datetime.today(), obj.select_number, cardbaldata, cardimsi)
                    send_error_msg(content)

                if flag:  # 查询 充值情况
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
        content = '{} \n 查询 流量信息报错\n错误:{}'.format(datetime.datetime.today(), e)
        send_error_msg(content, 1)
    return HttpResponse('')


# 异步传送小红书后台数据
def asynchronous_transfer_data(request):
    """
    transfer_type: 传递类型(1传递到小红书后台 2传递小红书评论成功 3更改笔记阅读量)
    :param request:
    :return:
    """
    transfer_type = request.POST.get('transfer_type')
    try:
        if transfer_type in [1, '1']:
            url = 'https://www.ppxhs.com/api/v1/sync/sync-comment'
            ret = requests.post(url, data=dict(request.POST))

        elif transfer_type  in [3, '3']:
            url =  'https://www.ppxhs.com/api/v1/sync/sync-read-num'
            ret = requests.post(url, data=dict(request.POST))

        else:
            url = 'https://www.ppxhs.com/api/v1/sync/sync-reply-status'
            ret = requests.post(url, data=dict(request.POST))

        models.AskLittleRedBook.objects.create( # 创建日志
            request_url=url,
            get_request_parameter='',
            post_request_parameter=request.POST,
            response_data=ret.json(),
            request_type=2,
            status=1,
        )

    except Exception as e:
        content = '{} \n 异步传输小红书评论数据报错{}\n错误:{}'.format(datetime.datetime.today(), transfer_type, e)
        send_error_msg(content, 1)

    return HttpResponse('')



