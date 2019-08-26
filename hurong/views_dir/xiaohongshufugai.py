from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from publicFunc.send_email import SendEmail
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.xiaohongshufugai import CheckForbiddenTextForm, SelectForm, AddForm, IsSelectedRankForm, DeleteForm
from django.db.models import Q
import redis
import json
import requests
import datetime
import re


@account.is_token(models.UserProfile)
def xiaohongshufugai(request):
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
def xiaohongshufugai_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        task_type = request.POST.get('task_type', 1) # 如果为2 等于收录任务
        if oper_type == "add":
            form_data = {
                'create_user_id': request.GET.get('user_id'),
                'keywords_list': request.POST.get('keywords_list'),
                'select_type': request.POST.get('select_type')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                keywords_list = forms_obj.cleaned_data.get('keywords_list')
                create_user_id = forms_obj.cleaned_data.get('create_user_id')
                select_type = forms_obj.cleaned_data.get('select_type')

                query = []
                try:
                    for item in keywords_list:
                        print('item -->', item)
                        # keywords, url = item.strip().split()
                        keywords = item.split('http')[0]
                        url = 'http' + item.split('http')[1].strip()


                        # 处理短链接
                        if url.startswith("http://t.cn"):
                            ret = requests.get(url, allow_redirects=False)

                            url = re.findall('HREF="(.*?)"', ret.text)[0].split('?')[0]

                        print(keywords, url)
                        if keywords and not models.XiaohongshuFugai.objects.filter(keywords=keywords, url=url, select_type=select_type):
                            query.append(
                                models.XiaohongshuFugai(
                                    create_user_id=create_user_id,
                                    keywords=keywords,
                                    url=url,
                                    select_type=select_type,
                                    task_type=task_type,
                                )
                            )
                            if len(query) > 500:
                                models.XiaohongshuFugai.objects.bulk_create(query)
                                query = []
                    if len(query) > 0:
                        models.XiaohongshuFugai.objects.bulk_create(query)

                    response.code = 200
                    response.msg = "添加成功"
                except ValueError:
                    forms_obj.add_error('keywords_list', "添加数据存在异常")
                    response.code = 301
                    response.msg = json.loads(forms_obj.errors.as_json())

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID

            form_data = {
                'delete_id_list': request.POST.get('delete_id_list')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = DeleteForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                delete_id_list = forms_obj.cleaned_data.get('delete_id_list')
                task_list_objs = models.XiaohongshuFugai.objects.filter(id__in=delete_id_list)
                if task_list_objs:
                    task_list_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 手机端当前任务是否已经查询到排名
        elif oper_type == "is_selected_rank":
            form_data = {
                'keywords': request.POST.get('keywords'),
                # 'url': request.POST.get('url')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = IsSelectedRankForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                keywords = forms_obj.cleaned_data.get('keywords')
                # url = forms_obj.cleaned_data.get('url')

                # 5分钟之前的时间
                five_minutes_ago_data = datetime.datetime.now() - datetime.timedelta(minutes=5)
                objs = models.XiaohongshuFugaiDetail.objects.select_related('keywords').filter(
                    keywords__keywords=keywords,
                    # keywords__url=url,
                    update_datetime__gt=five_minutes_ago_data
                ).order_by('-create_datetime')

                is_selected = False
                if objs and objs[0].rank > 0:  # 说明已经找到排名了
                    is_selected = True

                response.code = 200
                response.data = {
                    "is_selected": is_selected
                }
                response.msg = "查询成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        # 下拉词详情
        if oper_type == "detail":
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                    # 'keywords': '__contains',
                    'create_datetime': '',
                }

                q = conditionCom(request, field_dict)

                select_keywords = request.GET.get('select_keywords')
                url = request.GET.get('url')
                if select_keywords and url:
                    if url and url.startswith("http://t.cn"):
                        ret = requests.get(url, allow_redirects=False, timeout=10)
                        url = re.findall('HREF="(.*?)"', ret.text)[0].split('?')[0]

                    q.add(Q(**{'keywords__keywords': select_keywords}), Q.AND)
                    q.add(Q(**{'keywords__url': url}), Q.AND)
                    q.add(Q(**{'update_datetime__gte': datetime.datetime.now().strftime('%Y-%m-%d')}), Q.AND)

                else:
                    q.add(Q(**{'keywords_id': o_id}), Q.AND)

                print('q -->', q)
                objs = models.XiaohongshuFugaiDetail.objects.select_related('keywords').filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    #  将查询出来的数据 加入列表
                    ret_data.append({
                        'id': obj.id,
                        'keywords': obj.keywords.keywords,
                        'url': obj.keywords.url,
                        'rank': obj.rank,
                        'biji_num': obj.biji_num,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        'update_datetime': obj.update_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }
                response.note = {
                    'id': "下拉词id",
                    'keywords': "搜索词",
                    'url': "匹配链接",
                    'rank': "排名",
                    'biji_num': "笔记数",
                    'create_datetime': "创建时间",
                    'update_datetime': "更新时间",
                }
            else:
                print("forms_obj.errors -->", forms_obj.errors)
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        elif oper_type == "get_task":
            redis_obj1 = redis.StrictRedis(
                host='spider_redis',
                port=1111,
                db=13,
                password="Fmsuh1J50R%T*Lq15TL#IkWb#oMp^@0OYzx5Q2CSEEs$v9dd*mnqRFByoeGZ"
            )
            item = redis_obj1.rpop("xiaohongshu_task_list")
            if item:
                response.data = json.loads(item.decode('utf8'))

        # 查询收录是否完成
        elif oper_type == 'query_whether_inclusion_complete':
            q = Q()
            q.add(Q(update_datetime__lte=datetime.date.today()) | Q(update_datetime__isnull=False), Q.AND)
            has_been_completed_count = models.XiaohongshuFugai.objects.filter(
                q,
                task_type=2
            ).count()

            count = models.XiaohongshuFugai.objects.filter(
                task_type=2,
            ).count()


            is_success = 0
            if int(has_been_completed_count) > 0:
                is_success = 1

            data = {
                'is_success': is_success,
                'count': count,
                'has_been_completed_count': has_been_completed_count
            }
            response.code = 200
            response.msg = '查询成功'
            response.data = data
            response.note = {
                'is_success': '是否完成 1未完成 0完成',
                'count': '任务总数',
                'has_been_completed_count': '任务未完成总数'
            }

        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)
