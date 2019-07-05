from hurong import models
from publicFunc import Response, account
from publicFunc.public import requests_log
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.public_form import SelectForm as select_form
from hurong.forms.xiaohongshu_biji import SelectForm, AddForm, GetReleaseTaskForm, UploadUrlForm
import requests, datetime, json


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


# 增删改
# token验证
@account.is_token(models.UserProfile)
def xiaohongshu_biji_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
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
                content = forms_obj.cleaned_data.get('content')
                release_time = forms_obj.cleaned_data.get('release_time')
                print(xiaohongshu_id)
                xiaohongshu_user_objs = models.XiaohongshuUserProfile.objects.filter(xiaohongshu_id=xiaohongshu_id)
                if xiaohongshu_user_objs:
                    xiaohongshu_user_obj = xiaohongshu_user_objs[0]
                    obj = models.XiaohongshuBiji.objects.create(
                        user_id=xiaohongshu_user_obj,
                        content=content,
                        release_time=release_time
                    )

                    response.code = 200
                    response.msg = "添加成功"
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

                models.XiaohongshuBiji.objects.filter(id=task_id).update(biji_url=url, status=2, completion_time=datetime.datetime.today())

                api_url = "https://www.ppxhs.com/api/v1/sync/sync-screen-article"
                data = {
                    "id": task_id,
                    "link": url,
                    "online_pic": "http://qiniu.bjhzkq.com/xiaohongshu_fabu_1560934704790"
                }
                ret = requests.post(url=api_url, data=data)
                print("ret.text -->", ret.text)
                requests_log(api_url, data, ret.json()) # 记录请求日志
                response.code = 200
                response.msg = "提交成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 发布笔记
        elif oper_type == 'published_articles':
            response.code = 301
            objs = models.XiaohongshuBiji.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                if obj.status == 2:
                    msg = '已经发布, 请勿重复操作'
                else:
                    response.code = 200
                    obj.status = 1
                    obj.save()
                    msg = '发布成功'
            else:
                msg = '该笔记不存在'
            response.msg = msg

        else:
            response.code = 402
            response.msg = "请求异常"

    else:
        # 获取发布任务
        if oper_type == "get_release_task":
            form_data = {
                'imsi': request.GET.get('imsi'),
                'iccid': request.GET.get('iccid'),
            }
            forms_obj = GetReleaseTaskForm(form_data)
            if forms_obj.is_valid():
                iccid = forms_obj.cleaned_data['iccid']
                imsi = forms_obj.cleaned_data['imsi']

                objs = models.XiaohongshuBiji.objects.filter(
                    user_id__phone_id__iccid=iccid,
                    user_id__phone_id__imsi=imsi,
                    status=1,
                    release_time__lt=datetime.datetime.now()
                )

                if objs:
                    obj = objs[0]

                    response.code = 200
                    response.data = {
                        "id": obj.id,
                        "content": obj.content
                    }
                else:
                    response.code = 0
                    response.msg = "当前无任务"

            else:
                print("forms_obj.errors -->", forms_obj.errors)
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        # 查询 小红书笔记
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
                }
                q = conditionCom(request, field_dict)

                objs = models.XiaohongshuBiji.objects.filter(
                    q,
                ).exclude(user_id_id=5).order_by(order)
                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                ret_data = []
                select_id = request.GET.get('id')
                for obj in objs:
                    release_time = obj.release_time
                    if release_time:
                        release_time = obj.release_time.strftime('%Y-%m-%d %H:%M:%S')

                    completion_time = obj.completion_time
                    if completion_time:
                        completion_time = obj.completion_time.strftime('%Y-%m-%d %H:%M:%S')

                    result_data = {
                        'id': obj.id,
                        'user_id': obj.user_id_id,
                        'phone_name': obj.user_id.phone_id.name,
                        'user_name': obj.user_id.name,
                        'status_id': obj.status,
                        'status': obj.get_status_display(),
                        'release_time': release_time,
                        'completion_time': completion_time,
                        'biji_url': obj.biji_url,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    # if select_id:
                    result_data['content'] = json.loads(obj.content)

                    ret_data.append(result_data)

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                    'status_choices': [{'id':i[0], 'name':i[1]} for i in models.XiaohongshuBiji.status_choices]
                }
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)
