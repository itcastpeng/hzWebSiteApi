from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.xhs_phone_log import CheckForbiddenTextForm, SelectForm, AddForm, IsSelectedRankForm, DeleteForm
from publicFunc.public import send_error_msg
from publicFunc.redisOper import get_redis_obj
from publicFunc.public import create_xhs_admin_response
import json, datetime
import time

@account.is_token(models.UserProfile)
def xhs_phone_log(request):
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
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            # print('q -->', q)
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


# 增删改
# token验证
@account.is_token(models.UserProfile)
def xhs_phone_log_oper(request, oper_type, o_id):
    start_time = time.time()
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    # print('request.POST -->', request.POST)
    if request.method == "POST":
        #
        if oper_type == "add":

            form_data = {
                'log_msg': request.POST.get('log_msg'),
                'macaddr': request.POST.get('macaddr'),
                'ip_addr': request.POST.get('ip_addr'),
                'iccid': request.POST.get('iccid'),
                'imsi': request.POST.get('imsi'),
                'phone_type': request.POST.get('phone_type', 1),
            }
            xhs_version = request.POST.get('xhs_version')

            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                stop_time = time.time() - start_time
                print(stop_time, "cleaned_data --> ", forms_obj.cleaned_data)
                log_msg = forms_obj.cleaned_data.get('log_msg')
                macaddr = forms_obj.cleaned_data.get('macaddr')
                ip_addr = forms_obj.cleaned_data.get('ip_addr')
                iccid = forms_obj.cleaned_data.get('iccid')
                imsi = forms_obj.cleaned_data.get('imsi')
                phone_type = int(forms_obj.cleaned_data.get('phone_type'))

                # 查覆盖的机器
                if phone_type == 1:
                    objs = models.XiaohongshuPhone.objects.filter(
                        phone_type=phone_type,
                        macaddr=macaddr
                    )
                    if objs:
                        obj = objs[0]
                        obj.ip_addr = ip_addr
                        obj.save()

                    else:
                        obj = models.XiaohongshuPhone.objects.create(macaddr=macaddr, ip_addr=ip_addr)

                else:
                    data = {
                        "phone_type": phone_type,
                        "imsi": imsi,
                        "iccid": iccid
                    }
                    ip = request.META['HTTP_X_FORWARDED_FOR']

                    objs = models.XiaohongshuPhone.objects.filter(**data)
                    request_type = request.GET.get('request_type', None)
                    if request_type and objs:
                        response.code = 301
                        response.msg = '设备已存在, 请联系负责人处理'
                        response.data = {
                            'imsi':imsi,
                            'iccid':iccid,
                        }
                        return JsonResponse(response.__dict__)

                    if objs:
                        obj = objs[0]
                        obj.ip_addr = ip_addr
                        obj.request_ip_addr = ip
                        obj.save()
                    else:
                        obj = models.XiaohongshuPhone.objects.create(**data)

                if log_msg == '已查询完评论信息': # 记录 创建评论日志 最后一次更新时间
                    obj.comment_last_updated = datetime.datetime.today()
                    obj.save()

                redis_obj = get_redis_obj()
                redis_key = str(iccid + imsi)
                if not redis_obj.get(redis_key):
                    redis_obj.set(redis_key, 1)
                    redis_obj.expire(redis_key, 30)
                    # 更新最后一次 签到时间
                    models.XiaohongshuPhone.objects.filter(
                        iccid=iccid,
                        imsi=imsi
                    ).update(last_sign_in_time=datetime.datetime.today())

                # models.XiaohongshuPhoneLog.objects.create(
                #     log_msg=log_msg,
                #     parent=obj
                # )
                #  将日志存入redis中

                phone_log_id_key = "phone_log_{phone_id}".format(phone_id=obj.id)
                phone_log_list_key = "phone_log_list"
                if redis_obj.llen(phone_log_id_key) > 500:
                    redis_obj.rpop(phone_log_id_key)
                redis_obj.lpush(phone_log_id_key, json.dumps({
                    "log_msg": log_msg,
                    "create_date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }))

                stop_time = time.time() - start_time
                print("redis_stop -->", stop_time, "cleaned_data --> ", forms_obj.cleaned_data)

                phone_id = obj.id
                phone_name = obj.name

                phone_objs = models.XiaohongshuUserProfile.objects.filter(
                    phone_id_id=phone_id
                )
                if xhs_version and phone_id:
                    phone_objs.update(
                        xhs_version=xhs_version,
                    ) # 更新版本号

                if log_msg.startswith('没有找到回复私信用户'): # 报错
                    if phone_type == 1:
                        text_type = '查覆盖'
                    else:
                        text_type = '任务发布'

                    text = '类型:{}, 设备名称:{}, 日志:{}'.format(text_type, phone_name, log_msg)

                    content = """{} \n小红书添加日志中出现-->没有找到回复私信用户，请及时处理:  \n{}""".format(datetime.datetime.today(), text)
                    send_error_msg(content, 6) # 发送消息

                now_date_time = datetime.datetime.today()
                if log_msg.startswith('自动更新日志'): # 判断时间 与当前时间相差五分钟 and 版本号是否为最新

                    send_msg_flag = False # 是否发送错误提示
                    content = ''

                    json_data = json.loads(log_msg.split((log_msg.split(':')[0]) + ':')[1])
                    if json_data.get('runtime'):

                        deletionTime = (now_date_time - datetime.timedelta(minutes=10))
                        if json_data.get('runtime'):

                            package_type = json_data.get('package_type')
                            current_version = json_data.get('current_version')
                            if 'unknown' not in json_data.get('runtime'):
                                runtime = datetime.datetime.strptime(json_data.get('runtime'), '%Y-%m-%d %H:%M:%S')

                                if runtime > deletionTime:
                                    phone_objs.update(package_version=current_version)

                                    # package_objs = models.InstallationPackage.objects.filter(
                                    #     package_type=package_type
                                    # ).order_by('-id')
                                    # if package_objs:
                                    #     package_obj = package_objs[0]
                                    #     if int(package_obj.id) != int(current_version):
                                    #         send_msg_flag = True
                                    #         content = '{}\n {} 移动设备 发布程序不是最新版,请及时更新'.format(now_date_time, phone_name)
                                    # else:
                                    #     send_msg_flag = True
                                    #     content = '{}\n {} 移动设备 发布程序没有版本,请及时查看'.format(now_date_time, phone_name)

                                else:
                                    objs.update(status=3)

                            else:
                                phone_objs.update(package_version=current_version)
                            #     send_msg_flag = True
                            #     content = '{}\n {} 移动设备 自动更新程序异常,请及时处理'.format(now_date_time, phone_name)

                        # else:
                        #     send_msg_flag = True
                        #     content = '{}\n {} 移动设备 自动更新程序异常runtime字符为空,请及时处理, \nlog_msg参数:{}'.format(now_date_time, phone_name, log_msg)

                        if send_msg_flag:
                            send_error_msg(content, 6)

                if log_msg.startswith('请求接口异常'):
                    create_xhs_admin_response(request, log_msg, 3)
                    # log_msg_one = log_msg.replace('请求接口异常: ', '')
                    # log_msg_one = log_msg_one.split('返回数据->')
                    # request_url = log_msg_one[0].split('api_url->')[1]
                    # response_data = ''
                    # if len(log_msg_one) > 2:
                    #     response_data = log_msg_one[1]
                    # obj = models.PhoneRequestsBackgroundRecords.objects.create(
                    #     request_url=request_url,
                    #     response_data=response_data
                    # )
                    # content = '{}\n 设备请求接口 非200 告警, \n 表名:PhoneRequestsBackgroundRecords, \n 报错日志ID：{}'.format(now_date_time,obj.id)
                    # send_error_msg(content, 1)
                    # last_there_days = (now_date_time - datetime.timedelta(days=1))
                    # models.PhoneRequestsBackgroundRecords.objects.filter(
                    #     create_datetime__lte=last_there_days
                    # ).delete()
                response.code = 200
                response.msg = "日志记录成功"


            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
            stop_time = time.time() - start_time
            print("stop_time -->", stop_time, "cleaned_data --> ", forms_obj.cleaned_data)
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)
