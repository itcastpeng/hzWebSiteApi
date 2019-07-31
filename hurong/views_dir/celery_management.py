from django.http import HttpResponse
from publicFunc.phone_management_platform import phone_management
from hurong import models
from publicFunc.public import get_traffic_information as get_phone_info, query_device_recharge_information
from publicFunc.public import send_error_msg
from django.db.models import Q
from publicFunc.public import create_xhs_admin_response
import datetime, time, random, requests, json



# 定期删除 设备日志/ 请求日志
def delete_phone_log(request):
    try:
        now_date = datetime.date.today()
        last_there_days = (now_date - datetime.timedelta(days=2))
        models.XiaohongshuPhoneLog.objects.filter(
            create_datetime__lt=last_there_days
        ).delete()
        models.AskLittleRedBook.objects.filter(
            create_datetime__lt=last_there_days
        ).delete()

    except Exception as e:
        content = '{} \n 定期删除 设备日志报错\n错误:{}'.format(datetime.datetime.today(), e)
        send_error_msg(content)
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
        send_error_msg(content)

    return HttpResponse('')


# 查询 流量信息
def get_traffic_information(request):
    try:
        id = request.GET.get('id')
        q = Q()
        if id:
            q.add(Q(id=id), Q.AND)
        q.add(Q(select_datetime__lt=datetime.datetime.today()) | Q(select_datetime__isnull=True), Q.AND)

        objs = models.MobileTrafficInformation.objects.filter(
            q,
            select_number__isnull=False
        )
        for obj in objs:
            ret_json = get_phone_info(obj.select_number)
            if ret_json.get('code') != 0:
                obj.errmsg = ret_json.get('msg')
                obj.save()

            else:
                cardbaldata = ret_json.get('cardbaldata')
                cardimsi = ret_json.get('cardimsi').strip()
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

            obj.select_datetime = datetime.datetime.today()
            obj.save()

    except Exception as e:
        content = '{} \n 查询 流量信息报错\n错误:{}'.format(datetime.datetime.today(), e)
        send_error_msg(content)
    return HttpResponse('')


# 异步传送小红书后台数据
def asynchronous_transfer_data(request):
    """
    transfer_type: 传递类型(1传递到小红书后台 2传递小红书评论成功 3更改笔记阅读量 4删除评论是否成功)
    :param request:
    :return:
    """
    transfer_type = request.POST.get('transfer_type')
    msg = '异步传送小红书后台数据'
    try:
        if transfer_type in [1, '1']:
            msg = '异步传输小红书评论数据'
            url = 'https://a.ppxhs.com/api/v1/sync/sync-comment'
            ret = requests.post(url, data=request.POST)
            obj = models.littleRedBookReviewForm.objects.get(id=request.POST.get('comment_id')) # 修改上传状态
            obj.status = 2
            obj.save()

        elif transfer_type  in [3, '3']:
            msg = '异步传输小红书阅读量'
            url =  'https://a.ppxhs.com/api/v1/sync/sync-read-num'
            ret = requests.post(url, data=request.POST)

        elif transfer_type in [4, '4']:
            msg = '异步传输小红书回复评论是否删除'
            url = 'https://a.ppxhs.com/api/v1/sync-delete-comment'
            ret = requests.post(url, data=request.POST)

        else:
            msg = '异步传输小红书回复评论状态'
            url = 'https://a.ppxhs.com/api/v1/sync/sync-reply-status'
            ret = requests.post(url, data=request.POST)

        response_content = ret.json()

    except Exception as e:
        response_content = e
        content = '{} \n {}报错{}\n错误:{}'.format(
            datetime.datetime.today(),
            msg,
            transfer_type,
            e)
        send_error_msg(content)
    create_xhs_admin_response(request, response_content, 1, url=url, req_type=1) # 创建请求日志 后台请求小红书


    return HttpResponse('')

# 异步上传手机抓取的评论(避免创建的时候 异步上传报错)
def error_asynchronous_transfer_data(request):
    objs = models.littleRedBookReviewForm.objects.filter(status=1)
    for obj in objs:
        try:
            data = {
                'xhs_user_id': obj.xhs_user_id,  # 小红书用户
                'comments_status': obj.comments_status,  # 评论类型
                'article_picture_address': obj.article_picture_address,  # 文章图片地址
                'link': obj.screenshots_address,
                'name': obj.nick_name,
                'content': obj.comments_content,
                'head_portrait': obj.head_portrait,
                'comment_id': obj.id,
            }

            url = 'https://a.ppxhs.com/api/v1/sync/sync-comment'
            ret = requests.post(url, data=data)
            models.AskLittleRedBook.objects.create(  # 创建日志
                request_url=url,
                get_request_parameter='',
                post_request_parameter=data,
                response_data=ret.json(),
                request_type=2,
                status=1,
            )

            obj.status = 2
            obj.save()
        except Exception as e:
            content = '{} \n 异步上传手机抓取的评论报错\n错误:{}'.format(datetime.datetime.today(), e)
            send_error_msg(content)

    return HttpResponse('')



