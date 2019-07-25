
from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from hurong.forms.little_red_book_crawler import GeneratedTask, GeavyCheckTask, DeleteTasks, QueryComments, SelectForm
from publicFunc.condition_com import conditionCom
from django.db.models import Q
from publicFunc.base64_encryption import b64decode
import json, datetime, redis, requests

# 小红书爬虫
def little_red_book_crawler(request, oper_type):
    response = Response.ResponseObj()

    # redis_obj = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)
    redis_obj = redis.StrictRedis(host='redis', port=6381, db=0, decode_responses=True)
    redis_hash_name = 'xhs_comments_name'  # redis_name

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
            total_count = request.POST.get('total_count')  # 总数
            note_id = request.POST.get('note_id')
            article_content = request.POST.get('article_content')
            video_url = request.POST.get('video_url')
            note_type = request.POST.get('note_type')
            img_list = request.POST.get('img_list')
            desc = request.POST.get('desc')

            objs = models.XhsKeywordsList.objects.filter(id=id)
            if objs:
                obj = objs[0]
                obj.status = 2
                obj.total_count = total_count
                obj.save()

                models.ArticlesAndComments.objects.create(
                    keyword=obj,
                    nick_name=nick_name,
                    desc=desc,
                    note_id=note_id,
                    heading=heading,
                    article_content=article_content,
                    video_url=video_url,
                    note_type=note_type,
                    img_list=img_list,
                )
            response.code = 200

        # 更新评论
        elif oper_type == 'update_comments':
            id = request.POST.get('id')
            note_id = request.POST.get('note_id')
            comments_list = request.POST.get('comments_list')
            num = request.POST.get('num') # 当前查询条数
            one_comments_list_count = request.POST.get('one_comments_list_count') # 一级评论总数
            comments_list_count = request.POST.get('comments_list_count') # 评论总数
            redis_key = str(note_id + id + '_' + num)

            models.ArticlesAndComments.objects.filter(
                keyword_id=id,
                note_id=note_id
            ).update(
                article_comment=redis_key.split('_')[0],
                one_comments_list_count=one_comments_list_count,
                comments_list_count=comments_list_count
            )

            get_redis_data = redis_obj.hget(redis_hash_name, redis_key)

            if get_redis_data: # 如果存在 这个文章的评论
                redis_obj.hdel(redis_hash_name, redis_key)
                redis_obj.hset(redis_hash_name, redis_key, comments_list)

            else: # 如果不存在这个文章评论
                redis_obj.hset(redis_hash_name, redis_key, comments_list)

            response.code = 200

        # 创建小红书user_id
        elif oper_type == 'create_xhs_user_id':
            user_id_list = request.POST.get('user_id_list')
            user_id_list = eval(user_id_list)
            querysetlist = []
            for user_id in user_id_list:
                if not models.XhsUserId.objects.filter(xhs_user_id=user_id):
                    querysetlist.append(models.XhsUserId(
                        xhs_user_id=user_id,
                    ))
            models.XhsUserId.objects.bulk_create(querysetlist)

        # 提交用户ID
        elif oper_type == 'update_xhs_user_id':
            info = request.POST.get('info')
            xhs_user_id = request.POST.get('xhs_user_id')

            models.XhsUserId.objects.filter(xhs_user_id=xhs_user_id).update(
                success_time=datetime.datetime.today()
            )
            redis_name = 'xhs_user_id_name'

            redis_obj.hset(redis_name, xhs_user_id, info)


    else:
        now = datetime.date.today()
        now_date = datetime.datetime.today()
        deletionTime = (now_date + datetime.timedelta(hours=1))
        query_q = Q()
        query_q.add(Q(last_select_time__lt=now_date) | Q(last_select_time__isnull=True), Q.OR)
        query_q.add(Q(last_select_comments_time__lt=now_date) | Q(last_select_comments_time__isnull=True), Q.OR)

        # 查询评论(小红书后台)
        if oper_type == 'query_comments':
            form_data = {
                'article_comment': request.GET.get('article_comment'),
            }
            form_obj = QueryComments(form_data)
            if form_obj.is_valid():
                article_comment = form_obj.cleaned_data.get('article_comment')
                redis_key_objs = redis_obj.hget(redis_hash_name, article_comment)
                if redis_key_objs:
                    comments_data = json.loads(redis_key_objs)
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = comments_data

                else:
                    response.code = 301
                    response.msg = '该笔记没有评论'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 查询笔记(小红书后台)
        elif oper_type == 'query_notes':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', 'create_datetime')
                field_dict = {
                    'keyword__uid': '',
                }

                q = conditionCom(request, field_dict)
                objs = models.ArticlesAndComments.objects.filter(q).order_by(order)
                count = objs.count()
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
                # if objs and int(stop_line) <= int(objs[0].keyword.number):

                ret_data = []
                for obj in objs:
                    ret_data.append({
                        'nick_name': obj.nick_name,
                        'heading': obj.heading,
                        'article_content': obj.article_content,
                        'article_comment': obj.article_comment,
                        'one_comments_list_count': obj.one_comments_list_count,
                        'comments_list_count': obj.comments_list_count,
                        'note_type': obj.note_type,
                        'desc': obj.desc,
                        'note_id': obj.note_id,
                        'video_url': obj.video_url,
                        'img_list': json.loads(obj.img_list),
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                    'note_type_choices': [{'id':i[0], 'name': i[1]} for i in models.ArticlesAndComments.note_type_choices],
                }
                response.note = {
                    'ret_data':{
                        'nick_name': '小红书昵称',
                        'heading': '小红书头像',
                        'article_content': '文章内容',
                        'article_comment': '文章评论键',
                        'desc': '文章标题',
                        'one_comments_list_count': '首级评论总数',
                        'comments_list_count': '评论总数',
                        'note_type': '笔记类型',
                        'video_url': '视频链接',
                        'img_list': '图片链接/封面链接',
                    },
                    'count': '总数',
                    'note_type_choices': '笔记类型'
                }
                # else:
                #     response.code = 301
                #     response.msg = '获取笔记条数 大于爬取条数'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 查询是否有任务(VPS)
        elif oper_type == 'query_whether_task':
            query_q.add(Q(success_time__lt=now) | Q(success_time__isnull=True), Q.AND)
            objs = models.XhsKeywordsList.objects.filter(query_q)
            flag = False
            if objs:
                flag = True
            response.code = 200
            response.msg = '查询成功'
            response.data = flag

        # 获取任务(VPS) 分配什么任务(内容直接返回)
        elif oper_type == 'get_task':

            objs = models.XhsKeywordsList.objects.filter(query_q)
            data = {}
            if objs:
                obj = objs[0]
                now = now.strftime('%Y-%m-%d')
                last_time = obj.last_select_time
                if last_time:
                    last_time = obj.last_select_time.strftime('%Y-%m-%d')
                print('last_time-----> ', last_time, now)
                if last_time and last_time == now:
                    type_status = 2
                    obj.last_select_comments_time = deletionTime

                else:
                    models.ArticlesAndComments.objects.filter(keyword_id=obj.id).delete()
                    type_status = 1

                obj.last_select_time = deletionTime
                obj.save()
                data['id'] = obj.id
                data['keyword'] = obj.keyword
                data['number'] = obj.number
                data['type'] = type_status # 1 为查笔记内容 2为查评论

            response.code = 200
            response.msg = '查询成功'
            response.data = data

        # 获取评论任务
        elif oper_type == 'get_comments_task':
            keyword_id = request.GET.get('keyword_id')
            q = Q()
            q.add(Q(last_select_time__isnull=True) | Q(last_select_time__lt=now), Q.AND)
            objs = models.ArticlesAndComments.objects.filter(q, keyword_id=keyword_id)
            code = 301
            data = {}
            if objs:
                obj = objs[0]
                code = 200
                obj.last_select_time = deletionTime
                obj.save()

                data['note_id'] = obj.note_id
            response.code = code
            response.data = data

        # 更改完成时间
        elif oper_type == 'update_task_status':
            uid = request.GET.get('uid')
            objs = models.XhsKeywordsList.objects.filter(id=uid)
            now = datetime.datetime.today()
            objs.update(
                success_time=now
            )
            response.code = 200
            if objs:
                obj = objs[0]

                # 通知小红书 完成数据
                url = 'http://xhs.cn/api/v1/tools/keyword/check'
                data = {
                    'time_stamp':now,
                    'id':obj.uid,
                }
                requests.post(url, data=data)

        # 判断是否有查询 用户ID 任务
        elif oper_type == 'get_user_id_task':
            deletionTime = (now_date + datetime.timedelta(minutes=5))
            q = Q()
            q.add(Q(success_time__isnull=True), Q.AND)
            q.add(Q(last_select_time__lt=now_date) | Q(last_select_time__isnull=True), Q.AND)
            objs = models.XhsUserId.objects.filter(q)
            data_list = []
            for obj in  objs:
                data_list.append(obj.xhs_user_id)
                obj.last_select_time = deletionTime
                obj.save()
                response.code = 200
                response.data = data_list

            if len(data_list) < 1:
                response.code = 301

        else:
            response.code = 402
            response.msg = '请求异常'



    return JsonResponse(response.__dict__)






