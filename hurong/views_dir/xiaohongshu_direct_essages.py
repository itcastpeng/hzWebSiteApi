from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.xiaohongshu_direct_essages import SelectForm, AddForm, GetReleaseTaskForm, SaveScreenshotsForm, ReplyForm, GetReplyForm
from django.db.models import Q
from publicFunc.redisOper import get_redis_obj
from publicFunc.qiniu.auth import Auth
from publicFunc.public import create_xhs_admin_response
import base64, time, os, datetime, json, requests

@account.is_token(models.UserProfile)
def xiaohongshu_direct_essages(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'name': '',
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            xiaohongshu_id = request.GET.get('xiaohongshu_id')
            if xiaohongshu_id:
                q.add(Q(**{'user_id__xiaohongshu_id': xiaohongshu_id}), Q.AND)

            # print('q -->', q)
            objs = models.XiaohongshuDirectMessages.objects.select_related('user_id').filter(q).order_by(order)
            # print(objs)
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
                ret_data.append({
                    'id': obj.id,
                    'xiaohongshu_id': obj.user_id.xiaohongshu_id,
                    'name': obj.name,
                    'img_url': obj.img_url,
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
                'id': "小红书私信截图id",
                'xiaohongshu_id': "博主小红书id",
                'name': "私信博主名称",
                'img_url': "私信截图url",
                'create_datetime': "创建时间",
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
def xiaohongshu_direct_essages_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    # print('request.POST -->', request.POST)
    if request.method == "POST":
        # 保存私信截图
        if oper_type == "save_screenshots":
            form_data = {
                'name': request.POST.get('name'),
                'iccid': request.POST.get('iccid'),
                'imsi': request.POST.get('imsi'),
                'img_base64_data': request.POST.get('img_base64_data')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = SaveScreenshotsForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                name = forms_obj.cleaned_data.get('name')
                iccid = forms_obj.cleaned_data.get('iccid')
                imsi = forms_obj.cleaned_data.get('imsi')
                img_base64_data = forms_obj.cleaned_data.get('img_base64_data')
                img_base64_data = img_base64_data.replace(' ', '+')

                objs = models.XiaohongshuUserProfile.objects.filter(
                    phone_id__iccid=iccid,
                    phone_id__imsi=imsi
                )
                if objs:
                    imgdata = base64.b64decode(img_base64_data)

                    with open('t.png', 'wb') as f:
                        f.write(imgdata)

                    redis_obj = get_redis_obj()
                    upload_token = redis_obj.get('qiniu_upload_token')
                    if not upload_token:
                        qiniu_data_path = os.path.join(os.getcwd(), "publicFunc", "qiniu", "qiniu_data.json")
                        with open(qiniu_data_path, "r", encoding="utf8") as f:
                            data = json.loads(f.read())
                            access_key = data.get('access_key')
                            secret_key = data.get('secret_key')
                            obj = Auth(access_key, secret_key)
                            upload_token = obj.upload_token("xcx_wgw_zhangcong")

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13'
                    }

                    url = 'https://up-z1.qiniup.com/'

                    files = {
                        'file': imgdata
                    }
                    data = {
                        'token': upload_token,
                        'key': "xiaohongshu_fabu_" + str(int(time.time() * 1000))
                    }

                    ret = requests.post(url, data=data, files=files, headers=headers)
                    # print("ret.text -->", ret.json)
                    key = ret.json()["key"]
                    img_url = "http://qiniu.bjhzkq.com/{key}?imageView2/0/h/400".format(key=key)
                    obj = objs[0]
                    direct_message_obj = models.XiaohongshuDirectMessages.objects.create(
                        user_id=obj,
                        img_url=img_url,
                        name=name
                    )

                    from_blogger = 0
                    if request.POST.get('from_blogger'):
                        from_blogger = 1

                    # 把私信截图发送给小红书后台
                    for i in range(3):
                        try:
                            data = {
                                "id": direct_message_obj.id,
                                "name": name,
                                "img_url": img_url,
                                "xiaohongshu_id": obj.xiaohongshu_id,
                                "from_blogger": from_blogger,
                                "create_datetime": direct_message_obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                            }
                            api_url = 'https://www.ppxhs.com/api/v1/sync/sync-chat'
                            ret = requests.post(api_url, data=data)
                            print("ret.json", ret.json())
                            create_xhs_admin_response(request, ret.json(), 1, url=api_url, req_type=2)
                            break
                        except:
                            pass

                response.code = 200
                response.msg = "保存成功"
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 回复私信
        elif oper_type == "reply":
            form_data = {
                'xiaohongshu_id': request.POST.get('xiaohongshu_id'),
                'name': request.POST.get('name'),
                'msg': request.POST.get('msg')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = ReplyForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                xiaohongshu_id = forms_obj.cleaned_data.get('xiaohongshu_id')
                name = forms_obj.cleaned_data.get('name')
                msg = forms_obj.cleaned_data.get('msg')

                objs = models.XiaohongshuUserProfile.objects.filter(
                    xiaohongshu_id=xiaohongshu_id
                )
                if objs:
                    obj = objs[0]

                    if models.XiaohongshuDirectMessages.objects.filter(user_id=obj, name=name):
                        msg_reply_obj = models.XiaohongshuDirectMessagesReply.objects.create(
                            user_id=obj,
                            name=name,
                            msg=msg
                        )

                        response.code = 200
                        response.msg = "添加成功"
                        response.data = {
                            "id": msg_reply_obj.id
                        }
                    else:
                        response.code = 0
                        response.msg = "私信用户不存在"

                else:
                    response.code = 0
                    response.msg = "博主账号不存在"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 手机操作回复完成后,修改状态和更新时间
        elif oper_type == "reply_save":
            task_id = request.POST.get('task_id')
            objs = models.XiaohongshuDirectMessagesReply.objects.filter(id=task_id)
            objs.update(
                status=2,
                update_datetime=datetime.datetime.now()
            )

            post_data = {
                "id": objs[0].id
            }
            api_url = 'https://www.ppxhs.com/api/v1/sync/sync-chat-log'
            ret = requests.post(api_url, data=post_data)
            print(ret.text)
            create_xhs_admin_response(request, ret.json(), 1, url=api_url, req_type=2) # 记录请求日志

        else:
            response.code = 402
            response.msg = "请求异常"

    else:
        # 获取回复私信任务
        if oper_type == "get_reply":
            form_data = {
                'imsi': request.GET.get('imsi'),
                'iccid': request.GET.get('iccid'),
            }
            forms_obj = GetReplyForm(form_data)
            if forms_obj.is_valid():
                iccid = forms_obj.cleaned_data['iccid']
                imsi = forms_obj.cleaned_data['imsi']

                objs = models.XiaohongshuDirectMessagesReply.objects.filter(
                    user_id__phone_id__iccid=iccid,
                    user_id__phone_id__imsi=imsi,
                    status=1
                )

                if objs:
                    obj = objs[0]
                    response.code = 200
                    response.data = {
                        "id": obj.id,
                        "name": obj.name,
                        "msg": obj.msg
                    }
                else:
                    response.code = 0
                    response.msg = "当前无任务"

            else:
                print("forms_obj.errors -->", forms_obj.errors)
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        # 获取休息时间
        elif oper_type == "get_screenshot_time":
            form_data = {
                'imsi': request.GET.get('imsi'),
                'iccid': request.GET.get('iccid'),
            }
            forms_obj = GetReplyForm(form_data)
            if forms_obj.is_valid():
                iccid = forms_obj.cleaned_data['iccid']
                imsi = forms_obj.cleaned_data['imsi']

                objs = models.XiaohongshuUserProfile.objects.filter(
                    phone_id__imsi=imsi,
                    phone_id__iccid=iccid
                )

                now_date = datetime.datetime.today()
                now_hours = int(now_date.strftime('%H'))



                if objs:
                    obj = objs[0]
                    if now_hours > 8 and now_hours < 22:
                        screenshot_time = obj.screenshot_time
                    else:
                        screenshot_time = obj.late_screenshot_time

                    response.code = 200
                    response.data = {
                        "screenshot_time": screenshot_time,
                    }
                else:
                    response.code = 0
                    response.msg = "请求异常"

            else:
                print("forms_obj.errors -->", forms_obj.errors)
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        # 查询回复私信(胡蓉后台)
        elif oper_type == 'get_reply_info':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'user_id_id': '',
                    'user_id__name': '__contains',
                    'name': '__contains',
                    'msg': '__contains',
                    'status': '__contains',
                }

                q = conditionCom(request, field_dict)

                objs = models.XiaohongshuDirectMessagesReply.objects.select_related('user_id').filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:

                    update_datetime = obj.update_datetime
                    if update_datetime:
                        update_datetime = update_datetime.strftime('%Y-%m-%d %H:%M:%S')

                    ret_data.append({
                        'user_id': obj.user_id_id,
                        'user_name': obj.user_id.name,
                        'phone_name': obj.user_id.phone_id.name,
                        'phone_number': obj.user_id.phone_id.phone_num,
                        'phone_id': obj.user_id.phone_id_id,
                        'name': obj.name,
                        'msg': obj.msg,
                        'status_id': obj.status,
                        'status': obj.get_status_display(),
                        'update_datetime': update_datetime,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                    'status_choices': [{'id': i[0], 'name': i[1]} for i in models.XiaohongshuDirectMessagesReply.status_choices]
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 查询历史私信
        elif oper_type == 'inquire_historical_private_messages':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'user_id_id': '',
                    'name': '__contains',
                }

                q = conditionCom(request, field_dict)
                objs = models.XiaohongshuDirectMessages.objects.filter(q).order_by(order)
                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    user_id = ''
                    user_name = ''
                    if obj.user_id:
                        user_id = obj.user_id_id
                        user_name = obj.user_id.name

                    ret_data.append({
                        'user_id': user_id,
                        'name': obj.name,
                        'user_name': user_name,
                        'img_url': obj.img_url,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)
