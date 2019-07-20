
from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from hurong.forms.little_red_book_crawler import GeneratedTask, GeavyCheckTask, SelectForm, DeleteTasks
from publicFunc.condition_com import conditionCom
from django.db.models import Q
from publicFunc.base64_encryption import b64decode
import json, datetime, redis

# 小红书爬虫
def little_red_book_crawler(request, oper_type):
    response = Response.ResponseObj()

    if request.method == 'POST':
        form_data = {
            'post_data':request.POST.get('post_data'),
        }

        # 生成任务
        if oper_type == 'generated_task':
            """
            post_data 参数：
            encryption_value    # 加密值
            keyword             # 关键词
            number              # 获取条数
            """
            form_obj = GeneratedTask(form_data)
            if form_obj.is_valid():
                response.msg = '创建任务成功'
                response.code = 200

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 重查任务
        elif oper_type == 'geavy_check_task':
            form_obj = GeavyCheckTask(form_data)
            if form_obj.is_valid():
                post_data = form_obj.cleaned_data.get('post_data')
                code = 301
                msg = '重查MD5信息不存在'
                if post_data:
                    code = 200
                    msg = '重查完成'

                response.code = code
                response.msg = msg

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 删除任务
        elif oper_type == 'delete_tasks':
            form_obj = DeleteTasks(form_data)
            if form_obj.is_valid():
                response.code = 200
                response.msg = '删除成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 更改状态(VPS) 获取昵称/头像/内容
        elif oper_type == 'update_task_status':
            id = request.POST.get('id')
            nick_name = request.POST.get('nick_name')
            heading = request.POST.get('heading')
            total_count = request.POST.get('total_count')
            note_id = request.POST.get('note_id')
            article_content = request.POST.get('article_content')

            objs = models.XhsKeywordsList.objects.filter(id=id)
            if objs:
                obj = objs[0]
                obj.status = 2
                obj.total_count = total_count
                obj.save()

                models.ArticlesAndComments.objects.create(
                    keyword=obj,
                    nick_name=nick_name,
                    note_id=note_id,
                    heading=heading,
                    article_content=article_content,
                )
            response.code = 200

        # 更新评论
        elif oper_type == 'update_comments':
            id = request.POST.get('id')
            note_id = request.POST.get('note_id')
            comments_list = request.POST.get('comments_list')
            time_stamp = request.POST.get('time_stamp') # 时间戳  判断是否为一次的评论

            redis_obj = redis.StrictRedis(host='redis', port=6381, db=0, decode_responses=True)
            redis_key = str(note_id + id)

            redis_hash_name = 'xhs_comments_name'
            get_redis_data = redis_obj.hget(redis_hash_name, redis_key)

            if get_redis_data: # 如果存在 这个文章的评论
                print()
            else: # 如果不存在这个文章评论
                redis_obj.hset(redis_hash_name, redis_key, comments_list)

            data = redis_obj.hget(redis_hash_name, redis_key)
            print('data----> ', data)

            # objs = models.ArticlesAndComments.objects.filter(
            #     keyword_id=id,
            #     note_id=note_id
            # )
            # if objs:
            #     obj = objs[0]
            #     if obj.comment_time == time_stamp: # 如果是一次的时间戳
            #         if not obj.article_comment:  # 没有评论
            #             obj.article_comment = comments_list
            #
            #         else:
            #             article_comment = json.loads(obj.article_comment)
            #             article_comment.extend(json.dumps(comments_list))
            #             obj.article_comment = article_comment
            #     else:
            #         obj.article_comment = comments_list
            #
            #     obj.comment_time = time_stamp
            #     obj.save()


            response.code = 200

    else:

        # 查询任务信息(小红书后台)
        if oper_type == 'query_task_info':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                field_dict = {
                    'uid': '',
                }

                q = conditionCom(request, field_dict)
                order = request.GET.get('order', '-create_datetime')
                objs = models.XhsKeywordsList.objects.filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:

                    last_select_time = obj.last_select_time
                    if last_select_time:
                        last_select_time = obj.last_select_time.strftime('%Y-%m-%d %H:%M:%S')

                    ret_data.append({
                        'uid': obj.uid,
                        'keyword': obj.keyword,
                        'number': obj.number,
                        'last_select_time': last_select_time,
                        'status_id': obj.status,
                        'status': obj.get_status_display(),
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                    'status_choices': [{'id': i[0], 'name': i[1]} for i in models.XhsKeywordsList.status_choices]
                }
                response.note = {
                    'ret_data': {
                        'uid': '小红书后台ID',
                        'keyword': '关键词',
                        'number': '查询条数',
                        'nick_name': '名称',
                        'heading': '头像',
                        'last_select_time': '最后一次查询时间',
                        'status_id': '状态ID',
                        'status': '状态',
                        'create_datetime': '创建时间',
                    },
                    'count': '总数',
                    'status_choices': '状态ID 和 名称'
                }

        # 查询是否有任务(VPS)
        elif oper_type == 'query_whether_task':
            objs = models.XhsKeywordsList.objects.filter(status=1)
            flag = False
            if objs:
                flag = True
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'flag': flag
            }

        # 获取任务(VPS)
        elif oper_type == 'get_task':
            now_date = datetime.datetime.today()
            deletionTime = (now_date - datetime.timedelta(minutes=5))
            q = Q()
            q.add(Q(last_select_time__lte=deletionTime) | Q(last_select_time__isnull=True,), Q.AND)
            objs = models.XhsKeywordsList.objects.filter(
                # q,
                status=1,
            )
            data = {}
            if objs:
                obj = objs[0]
                obj.last_select_time = now_date
                obj.save()

                data['id'] = obj.id
                data['keyword'] = obj.keyword
                data['number'] = obj.number
                data['related_keyword'] = obj.related_keyword

            response.code = 200
            response.msg = '查询成功'
            response.data = data

        # 临时
        elif oper_type == 'test':
            objs = models.ArticlesAndComments.objects.all()
            data = []
            for obj in objs:
                data.append({
                    'content': b64decode(obj.article_content)
                })
            response.data = data

        else:
            response.code = 402
            response.msg = '请求异常'



    return JsonResponse(response.__dict__)






