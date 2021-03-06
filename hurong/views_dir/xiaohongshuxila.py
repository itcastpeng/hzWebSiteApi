from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from publicFunc.send_email import SendEmail
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.xiaohongshu import CheckForbiddenTextForm, SelectForm, AddForm, DeleteForm
from django.db.models import Q
import redis
import json
import requests


@account.is_token(models.UserProfile)
def xiaohongshuxila(request):
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
                'keywords': '__contains',
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            # print('q -->', q)
            objs = models.XiaohongshuXiaLaKeywords.objects.filter(q).order_by(order)
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
                ret_data.append({
                    'id': obj.id,
                    'keywords': obj.keywords,
                    'status': obj.get_status_display(),
                    'status_id': obj.status,
                    'biji_num': obj.biji_num,
                    'xialaci_num': obj.xialaci_num,
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
            }
            response.note = {
                'id': "下拉词id",
                'keywords': "搜索词",
                'status': "状态名称",
                'status_id': "状态值",
                'biji_num': "笔记数",
                'xialaci_num': "下拉词数",
                'send_email_content': "发送邮件内容",
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
def xiaohongshuxila_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    # print('request.POST -->', request.POST)
    if request.method == "POST":
        # 添加用户
        if oper_type == "add":
            form_data = {
                'create_user_id': request.GET.get('user_id'),
                'keywords_list': request.POST.get('keywords_list')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                keywords_list = forms_obj.cleaned_data.get('keywords_list')
                create_user_id = forms_obj.cleaned_data.get('create_user_id')

                query = []
                for keywords in keywords_list:
                    keywords = keywords.strip()
                    if keywords and not models.XiaohongshuXiaLaKeywords.objects.filter(keywords=keywords):
                        query.append(
                            models.XiaohongshuXiaLaKeywords(create_user_id=create_user_id, keywords=keywords)
                        )
                        if len(query) > 500:
                            models.XiaohongshuXiaLaKeywords.objects.bulk_create(query)
                            query = []
                if len(query) > 0:
                    models.XiaohongshuXiaLaKeywords.objects.bulk_create(query)

                response.code = 200
                response.msg = "添加成功"

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
                task_list_objs = models.XiaohongshuXiaLaKeywords.objects.filter(id__in=delete_id_list)
                if task_list_objs:
                    task_list_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
            #
            # task_list_objs = models.XiaohongshuXiaLaKeywords.objects.filter(id=o_id)
            # if task_list_objs:
            #     if task_list_objs[0].status == 1:
            #         task_list_objs.delete()
            #         response.code = 200
            #         response.msg = "删除成功"
            #     else:
            #         response.code = 300
            #         response.msg = "该任务在操作中或者已完成，不能删除"

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
                    'keywords': '__contains',
                    'create_datetime': '',
                }

                q = conditionCom(request, field_dict)

                select_keywords = request.GET.get('select_keywords')
                if select_keywords:
                    q.add(Q(**{'parent__keywords': select_keywords}), Q.AND)
                else:
                    q.add(Q(**{'parent_id': o_id}), Q.AND)

                # print('q -->', q)
                objs = models.XiaohongshuXiaLaKeywordsChildren.objects.select_related('parent').filter(q).order_by(order)
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
                        'biji_num': obj.parent.biji_num,
                        'keywords': obj.keywords,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                biji_num = 0
                if objs:
                    biji_num = objs[0].parent.biji_num
                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'biji_num': biji_num,
                    'data_count': count,
                }
                response.note = {
                    'id': "下拉词id",
                    'keywords': "搜索词",
                    'create_datetime': "创建时间",
                }
            else:
                # print("forms_obj.errors -->", forms_obj.errors)
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)
