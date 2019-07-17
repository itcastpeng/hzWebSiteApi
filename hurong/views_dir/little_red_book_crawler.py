
from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from hurong.forms.little_red_book_crawler import GeneratedTask, GeavyCheckTask, SelectForm, DeleteTasks
from publicFunc.condition_com import conditionCom
import json

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

    else:

        # 查询任务信息
        if oper_type == 'query_task_info':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                field_dict = {
                    'status': '',
                    'nick_name': '__contains',
                    'keyword': '__contains',
                    'uid': '__contains',
                    'note_content': '__contains',
                    'comments': '__contains',
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
                        'nick_name': obj.nick_name,
                        'heading': obj.heading,
                        'note_content': obj.note_content,
                        'comments': obj.comments,
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
                        'encryption_value': 'MD5加密值',
                        'keyword': '关键词',
                        'number': '查询条数',
                        'nick_name': '名称',
                        'heading': '头像',
                        'note_content': '笔记',
                        'comments': '评论',
                        'last_select_time': '最后一次查询时间',
                        'status_id': '状态ID',
                        'status': '状态',
                        'create_datetime': '创建时间',
                    },
                    'count': '总数',
                    'status_choices': '状态ID 和 名称'
                }

        else:
            response.code = 402
            response.msg = '请求异常'



    return JsonResponse(response.__dict__)






