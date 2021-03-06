
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
            title = request.POST.get('title')
            liked_count = request.POST.get('liked_count')

            objs = models.XhsKeywordsList.objects.filter(id=id)
            if objs:
                obj = objs[0]
                # obj.status = 2
                obj.total_count = total_count
                obj.save()

                models.ArticlesAndComments.objects.create(
                    keyword=obj,
                    liked_count=liked_count,
                    title=title,
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
                id=id,
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
                if not models.XhsUserId.objects.filter(xhs_user_id=user_id.strip()):
                    querysetlist.append(models.XhsUserId(
                        xhs_user_id=user_id.strip(),
                    ))
            models.XhsUserId.objects.bulk_create(querysetlist)

        # 创建 小红书登录数据
        elif oper_type == 'create_xhs_login_data':
            login_data = request.POST.get('login_data')
            phone_num = request.POST.get('phone_num')
            objs = models.XhsLoginData.objects.filter(phone_num=phone_num)
            if objs:
                objs.update(
                    login_data=login_data
                )
            else:
                models.XhsLoginData.objects.create(
                    login_data=login_data,
                    phone_num=phone_num
                )
            response.code = 200
            response.msg = '更新成功'

    else:
        now = datetime.date.today()
        now_date = datetime.datetime.today()
        deletionTime = (now_date + datetime.timedelta(hours=1))

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
                        'title': obj.title,
                        'note_id': obj.note_id,
                        'liked_count': obj.liked_count,
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

        # 获取任务(VPS) 分配什么任务(内容直接返回)
        elif oper_type == 'get_task':
            """
            type_status = 0 无任务  
            type_status = 1 为笔记任务  获取该关键词对应条数笔记
            type_status = 2 为评论任务  获取该笔记所有评论
            type_status = 3 为获取小红书用户ID任务 获取用户ID  
            """
            flag = False
            type_status = 0  # 无任务

            data = {}
            if not flag:# 笔记任务
                query_q = Q()
                query_q.add(Q(last_select_time__lt=now) | Q(last_select_time__isnull=True), Q.AND)
                print('query_q----> ', query_q)
                objs = models.XhsKeywordsList.objects.filter(query_q).exclude(is_success_time__gte=datetime.date.today())
                if objs:
                    obj = objs[0]
                    models.ArticlesAndComments.objects.filter(keyword_id=obj.id).delete()
                    flag = True
                    obj.last_select_time = deletionTime
                    obj.save()
                    data['id'] = obj.id
                    data['keyword'] = obj.keyword
                    data['number'] = obj.number
                    type_status = 1

            if not flag:# 评论任务
                comment_q = Q()
                comment_q.add(Q(last_select_time__isnull=True) | Q(last_select_time__lt=now) | Q(article_comment__isnull=True), Q.AND)
                objs = models.ArticlesAndComments.objects.filter(comment_q)
                if objs:
                    type_status = 2
                    comment_obj = objs[0]
                    comment_obj.last_select_time = now_date
                    comment_obj.save()
                    note_id = comment_obj.note_id
                    data['id'] = comment_obj.id
                    data['note_id'] = note_id


            data['type_status'] = type_status # 1 为查笔记内容 2为查评论
            response.code = 200
            response.msg = '查询成功'
            response.data = data

        # 更改完成时间
        elif oper_type == 'update_task_status':
            uid = request.GET.get('uid')
            q = Q()

            comment_obj = models.ArticlesAndComments.objects.get(id=uid)
            q.add(Q(keyword_id=comment_obj.keyword_id), Q.AND)
            q.add(Q(last_select_time=datetime.date.today()) & Q(article_comment__isnull=True), Q.OR)
            q.add(Q(last_select_time__isnull=True) | Q(last_select_time=datetime.date.today()) & Q(article_comment__isnull=True), Q.AND)
            # q.add(Q(last_select_time__lte=datetime.date.today()) & Q(keyword_id=uid) | Q(article_comment__isnull=True), Q.AND)

            print('q-------> ', q)
            comments_count = models.ArticlesAndComments.objects.filter(q).count()
            print('comments_count-------------------提交剩余数量=------------》', comments_count)
            response.code = 200

            if comments_count <= 0:
                objs = models.XhsKeywordsList.objects.filter(id=comment_obj.keyword_id)
                now = datetime.datetime.today()
                objs.update(
                    is_success_time=now
                )
                if objs:
                    obj = objs[0]
                    # 通知小红书 完成数据
                    url = 'http://zmtxiansuo.bjhzkq.com/api/keyword/query-update'
                    data = {
                        'time_stamp':now,
                        'id':obj.uid,
                    }
                    requests.post(url, data=data)
            response.msg = '未完成数量:{}'.format(comments_count)

        # 查询是否有可用 小红书登录数据
        elif oper_type == 'query_whether_login_data_available':
            deletionTime = (now + datetime.timedelta(hours=2))  # 当前时间减去两小时
            q = Q()
            q.add(Q(update_time__isnull=True) | Q(update_time__lte=datetime.datetime.today()), Q.AND)
            print('q-----> ', q)
            objs = models.XhsLoginData.objects.filter(q)
            flag = False
            login_data = {}
            if objs:
                flag = True
                obj = objs[0]
                login_data = json.loads(obj.login_data)
                obj.update_time = deletionTime
                obj.save()

            response.code = 200
            response.data = {
                'flag': flag,
                'login_data': login_data
            }

        else:
            response.code = 402
            response.msg = '请求异常'



    return JsonResponse(response.__dict__)






