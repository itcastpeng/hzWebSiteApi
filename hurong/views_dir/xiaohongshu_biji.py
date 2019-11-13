from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.public_form import SelectForm as select_form
from hurong.forms.xiaohongshu_biji import SelectForm, AddForm, GetReleaseTaskForm, UploadUrlForm, UpdateReding, \
    InsteadAbnormalReleaseNotes, PublishedNotesBackChain, UpdateExistContentForm, RepublishInsteadForm, ChangePendingReview
from hz_website_api_celery.tasks import asynchronous_transfer_data, asynchronous_synchronous_trans
from publicFunc.base64_encryption import b64decode, b64encode
from django.db.models import Q
from publicFunc.public import create_xhs_admin_response, get_existing_url
import requests, datetime, json, re


@account.is_token(models.UserProfile)
def xiaohongshu_biji(request):
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

            # print('q -->', q)
            objs = models.XiaohongshuFugai.objects.filter(q).order_by(order)
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

                'exist_content': "比较是否存在内容"
            }
        else:
            # print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.UserProfile)
def xiaohongshu_biji_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    # print('request.POST -->', request.POST)
    if request.method == "POST":
        # 添加
        if oper_type == "add":
            form_data = {
                'xiaohongshu_id': request.POST.get('xiaohongshu_id'),
                'content': request.POST.get('content'),
                'release_time': request.POST.get('release_time', datetime.datetime.now())
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")


                xiaohongshu_id = forms_obj.cleaned_data.get('xiaohongshu_id')
                title, content, biji_type = forms_obj.cleaned_data.get('content')
                release_time = forms_obj.cleaned_data.get('release_time')
                platform = request.POST.get('platform', 1)
                xiaohongshu_user_objs = models.XiaohongshuUserProfile.objects.filter(xiaohongshu_id=xiaohongshu_id, platform=platform)
                if xiaohongshu_user_objs:
                    xiaohongshu_user_obj = xiaohongshu_user_objs[0]

                    biji_id = request.POST.get('biji_id') # 如果有 该值 则更新 待审核状态
                    if biji_id:
                        biji_objs = models.XiaohongshuBiji.objects.filter(id=biji_id)
                        obj = biji_objs[0]
                        biji_objs.update(status=3, content=content, release_time=release_time, title=title, biji_type=biji_type, user_id_id=xiaohongshu_user_obj.id)
                        response.code = 200
                        response.msg = "更新成功"

                    else:
                        objs = models.XiaohongshuBiji.objects.filter(
                            title=title,
                            user_id_id=xiaohongshu_user_obj.id,
                            user_id__platform=platform
                        )
                        if objs:
                            response.code = 301
                            response.msg = '笔记已存在, 请勿重复添加'
                            return JsonResponse(response.__dict__)

                        else:
                            obj = models.XiaohongshuBiji.objects.create(
                                user_id=xiaohongshu_user_obj,
                                content=content,
                                release_time=release_time,
                                title=title,
                                biji_type=biji_type
                            )
                            response.msg = "添加成功"
                        response.code = 200
                    response.data = {
                        'biji_id': obj.id
                    }
                else:
                    response.code = 0
                    response.msg = "添加失败, 小红书id不存在"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
            create_xhs_admin_response(request, response, 2)

        # 提交反链
        elif oper_type == "upload_url":
            form_data = {
                'task_id': request.POST.get('task_id'),
                'url': request.POST.get('url'),
            }
            forms_obj = UploadUrlForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                task_id = forms_obj.cleaned_data.get('task_id')
                url = forms_obj.cleaned_data.get('url')
                link = get_existing_url(url) # 获取真实链接

                completion_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                biji_objs = models.XiaohongshuBiji.objects.filter(id=task_id)
                biji_objs.update(
                    biji_existing_url=link,
                    biji_url=link,
                    status=2,
                    completion_time=completion_time
                )

                api_url = "https://www.ppxhs.com/api/v1/sync/sync-screen-article"
                data = {
                    "id": task_id,
                    "link": url,
                    "platform": biji_objs[0].user_id.platform,
                    "pubTime": completion_time,
                    "online_pic": "http://qiniu.bjhzkq.com/xiaohongshu_fabu_1560934704790"
                }
                ret = requests.post(url=api_url, data=data)
                create_xhs_admin_response(request, ret.json(), 1, url=api_url, req_type=2)  # 记录请求日志
                response.code = 200
                response.msg = "提交成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
            create_xhs_admin_response(request, response, 3)

        # 发布笔记(后台)
        elif oper_type == 'published_articles':
            now = datetime.datetime.today()
            flag = False
            hms_date = datetime.datetime.today().strftime('%H:%M:%S')
            hms_date = datetime.datetime.strptime(hms_date, '%H:%M:%S')

            if datetime.datetime.strptime('8:30:00', '%H:%M:%S') >= hms_date >= datetime.datetime.strptime('7:30:00', '%H:%M:%S'):
                flag = True
            elif datetime.datetime.strptime('13:30:00', '%H:%M:%S') >= hms_date >= datetime.datetime.strptime('12:00:00', '%H:%M:%S'):
                flag = True
            elif datetime.datetime.strptime('21:30:00', '%H:%M:%S') >= hms_date >= datetime.datetime.strptime('17:00:00', '%H:%M:%S'):
                flag = True

            if flag:
                id_list = json.loads(request.POST.get('id_list'))
                objs = models.XiaohongshuBiji.objects.filter(id__in=id_list)
                for obj in objs:
                    obj.status = 1
                    obj.save()
                response.code = 200
                response.msg = '发布成功'

            else:
                response.code = 301
                response.msg = '当前时间不在发布时间段'
            create_xhs_admin_response(request, response, 3)  # 创建请求日志(手机端)

        # 阅读量更改(后台)
        elif oper_type == 'update_reding':
            """
            o_id: 笔记ID
            reading_num: 阅读量
            """
            form_data = {
                'o_id': o_id,
                'reading_num': request.POST.get('reading_num')
            }

            form_obj = UpdateReding(form_data)
            if form_obj.is_valid():
                o_id = form_obj.cleaned_data.get('o_id')
                reading_num = int(form_obj.cleaned_data.get('reading_num'))
                if reading_num > 0:

                    objs = models.XiaohongshuBiji.objects.filter(
                        id=o_id
                    )
                    objs.update(
                        reading_num=reading_num,
                        update_reding_num_time=datetime.datetime.today()
                    )
                    form_data['num'] = reading_num
                    form_data['transfer_type'] = 3
                    form_data['id'] = o_id
                    form_data['platform'] = objs[0].user_id.platform
                    asynchronous_transfer_data.delay(form_data) # 传递到小红书后台
                response.code = 200
                response.msg = '阅读量更新完成'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())
            create_xhs_admin_response(request, response, 3)

        # 发布中的笔记 可以改为发布异常(后台)
        elif oper_type == 'instead_abnormal_release_notes':
            form_data = {
                'o_id': o_id,
                'error_msg': request.POST.get('error_msg')
            }
            form_obj = InsteadAbnormalReleaseNotes(form_data)
            if form_obj.is_valid():
                o_id = form_obj.cleaned_data.get('o_id')
                error_msg = form_obj.cleaned_data.get('error_msg')
                obj = models.XiaohongshuBiji.objects.get(id=o_id)
                obj.status = 4
                obj.error_msg = error_msg
                obj.save()
                response.code = 200
                response.msg = '更改发布异常成功'

                form_data['transfer_type'] = 5
                form_data['id'] = o_id
                form_data['platform'] = obj.user_id.platform
                form_data['content'] = error_msg
                asynchronous_transfer_data.delay(form_data)  # 传递到小红书后台
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())
            create_xhs_admin_response(request, response, 2)

        # 已发布的可修改回链（后台）
        elif oper_type == 'published_notes_back_chain':
            form_data = {
                'o_id': o_id,
                'back_url': request.POST.get('back_url')
            }
            form_obj = PublishedNotesBackChain(form_data)
            if form_obj.is_valid():
                o_id = form_obj.cleaned_data.get('o_id')
                back_url, link = form_obj.cleaned_data.get('back_url')
                obj = models.XiaohongshuBiji.objects.get(id=o_id)
                obj.biji_url = back_url
                obj.biji_existing_url = link
                obj.save()
                response.code = 200
                response.msg = '修改反链成功'
                asynchronous_synchronous_trans.delay(o_id) # 异步更改小红书后台回链
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())
            create_xhs_admin_response(request, response, 1)

        # 修改笔记是否存在内容的状态
        elif oper_type == "update_exist_content":
            status = request.POST.get('status')
            form_data = {
                'status': request.POST.get('status'),
                'o_id': o_id,
            }
            print("status -->", status, type(status))
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = UpdateExistContentForm(form_data)
            if forms_obj.is_valid():
                status = forms_obj.cleaned_data.get('status')
                models.XiaohongshuBiji.objects.filter(id=o_id).update(exist_content=status)
                response.code = 200
                response.msg = "修改成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 已发布的笔记 改为重新发布(小红书后台) 404
        elif oper_type == 'republish_instead':
            form_data = {
                'o_id':o_id,
            }
            form_obj = RepublishInsteadForm(form_data)
            if form_obj.is_valid():
                o_id = form_obj.cleaned_data.get('o_id')
                models.XiaohongshuBiji.objects.filter(id=o_id).update(
                    status=5,
                    is_delete_old_biji=False
                )
                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())
            create_xhs_admin_response(request, response, 2)

        # 重新发布的笔记 改为待审核(后台)
        elif oper_type == 'change_pending_review':
            form_data = {
                'biji_id_list': request.POST.get('biji_id_list')
            }
            form_obj = ChangePendingReview(form_data)
            if form_obj.is_valid():
                biji_id_list = form_obj.cleaned_data.get('biji_id_list')
                objs = models.XiaohongshuBiji.objects.filter(
                    id__in=biji_id_list
                )
                objs.update(
                    is_delete_old_biji=True
                )
                for obj in objs:
                    url = 'https://www.ppxhs.com/api/v1/sync/screen-notfound'
                    data = {
                        'id':obj.id,
                        'platform':obj.user_id.platform
                    }
                    ret = requests.post(url, data=data)
                    models.AskLittleRedBook.objects.create(  # 更新日志
                        request_type=2,  # POST请求
                        request_url=url,
                        get_request_parameter='',
                        post_request_parameter=data,
                        response_data=ret.json(),
                        status=1
                    )
                response.code = 200
                response.msg = '删除成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())
            create_xhs_admin_response(request, response, 2)

        else:
            response.code = 402
            response.msg = "请求异常"

    else:
        # 获取发布任务
        if oper_type == "get_release_task":
            form_data = {
                'imsi': request.GET.get('imsi'),
                'iccid': request.GET.get('iccid'),
                'platform': request.GET.get('platform', 1),
            }
            forms_obj = GetReleaseTaskForm(form_data)
            if forms_obj.is_valid():
                iccid = forms_obj.cleaned_data['iccid']
                imsi = forms_obj.cleaned_data['imsi']
                platform = forms_obj.cleaned_data['platform']

                objs = models.XiaohongshuBiji.objects.select_related('user_id').filter(
                    user_id__platform=platform,
                    user_id__phone_id__iccid=iccid,
                    user_id__phone_id__imsi=imsi,
                    status=1,
                    release_time__lt=datetime.datetime.now()
                )

                if objs:
                    obj = objs[0]

                    response.data = {
                        "id": obj.id,
                        "content": obj.content,
                        "platform": obj.user_id.platform,
                    }
                else:
                    response.msg = "当前无任务"
                response.code = 200

            else:
                # print("forms_obj.errors -->", forms_obj.errors)
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())
            create_xhs_admin_response(request, response, 3)
        # 查询 小红书笔记(后台)
        elif oper_type == 'get_xhs_notes':
            forms_obj = select_form(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                    'uid': '__contains',
                    'status': '',
                    'biji_type': '',
                    'user_id__name': '__contains',
                    'is_delete_old_biji': '',
                    'user_id__phone_id__name': '',
                    'biji_existing_url': '__contains',
                    'reading_num': '',
                }
                q = conditionCom(request, field_dict)
                content = request.GET.get('content')
                xhs_user_id = request.GET.get('xhs_user_id')
                if content:
                    q.add(Q(title__contains=b64encode(content)), Q.AND)
                if xhs_user_id:
                    q.add(Q(user_id=xhs_user_id), Q.AND)
                objs = models.XiaohongshuBiji.objects.select_related('user_id').filter(
                    q,
                ).exclude(user_id_id=5).order_by(order)
                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                ret_data = []
                for obj in objs:
                    # biji_type = 'img'
                    # if json.loads(obj.content).get('type') and json.loads(obj.content).get('type') != 'images':
                    #     biji_type = 'video'
                    release_time = obj.release_time
                    if release_time:
                        release_time = obj.release_time.strftime('%Y-%m-%d %H:%M:%S')

                    completion_time = obj.completion_time
                    if completion_time:
                        completion_time = obj.completion_time.strftime('%Y-%m-%d %H:%M:%S')

                    update_reding_num_time = ''
                    if obj.update_reding_num_time:
                        update_reding_num_time = obj.update_reding_num_time.strftime('%Y-%m-%d %H:%M:%S')
                    result_data = {
                        'id': obj.id,
                        'user_id': obj.user_id_id,
                        'phone_id': obj.user_id.phone_id_id,
                        'phone_name': obj.user_id.phone_id.name,
                        'phone_number': obj.user_id.phone_id.phone_num,
                        'user_name': obj.user_id.name,
                        'status_id': obj.status,
                        'reading_num': obj.reading_num,
                        'status': obj.get_status_display(),
                        'release_time': release_time,
                        'completion_time': completion_time,
                        'biji_url': obj.biji_url,
                        'error_msg': obj.error_msg,
                        'biji_type_id': obj.biji_type,
                        'biji_type': obj.get_biji_type_display(),
                        'biji_existing_url': obj.biji_existing_url,
                        'is_delete_old_biji': obj.is_delete_old_biji,
                        'update_reding_num_time': update_reding_num_time,
                        'platform': obj.user_id.platform,
                        'exist_content': obj.exist_content,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    result_data['content'] = json.loads(obj.content)
                    ret_data.append(result_data)
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                    'status_choices': [{'id':i[0], 'name':i[1]} for i in models.XiaohongshuBiji.status_choices],
                    'biji_type_choices': [{'id':i[0], 'name':i[1]} for i in models.XiaohongshuBiji.biji_type_choices]
                }
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 获取 exist_content 字段为False的笔记链接，请求小红书接口进行获取数据，判断文章内容是否正常
        elif oper_type == "exist_content_get_url":
            objs = models.XiaohongshuBiji.objects.filter(status=2, exist_content=0)
            if objs:
                obj = objs[0]
                response.code = 200
                biji_id = obj.biji_existing_url.split('/')[-1]
                response.data = {
                    'biji_id': biji_id,
                    'task_id': obj.id
                }
            else:
                response.code = 0
                response.msg = "当前无任务"


        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)
