# from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from publicFunc import send_email as SendEmail
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.task_list import SelectForm, AddForm, UpdateForm, TestForm
import json
from django.db.models import Q


@account.is_token(models.UserProfile)
def task_list(request):
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
                'name': '__contains',
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            # q.add(Q(**{k + '__contains': value}), Q.AND)
            role_id = models.UserProfile.objects.get(id=user_id).role_id_id
            if role_id != 1:    # 非管理员角色只能看自己的
                q.add(Q(**{'create_user_id': user_id}), Q.AND)

            objs = models.TaskList.objects.filter(is_delete=False).filter(q).order_by(order)
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
                    'name': obj.name,
                    'status': obj.get_status_display(),
                    'status_id': obj.status,
                    'percentage_progress': obj.percentage_progress,
                    'send_email_title': obj.send_email_title,
                    'send_email_content': obj.send_email_content,
                    'create_user__username': obj.create_user.username,
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
                'id': "任务id",
                'name': "任务名称",
                'percentage_progress': "任务进度",
                'send_email_title': "发送邮件标题",
                'send_email_content': "发送邮件内容",
                'create_user__username': "创建人",
                'create_datetime': "创建时间",
                'status': "状态名称",
                'status_id': "状态值",
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
def task_list_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "POST":
        # 添加用户
        if oper_type == "add":
            form_data = {
                'create_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'send_email_title': request.POST.get('send_email_title'),
                'send_email_content': request.POST.get('send_email_content'),
                'send_email_list': request.POST.get('send_email_list'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                create_data = {
                    'create_user_id': forms_obj.cleaned_data.get('create_user_id'),
                    'name': forms_obj.cleaned_data.get('name'),
                    'send_email_title': forms_obj.cleaned_data.get('send_email_title'),
                    'send_email_content': forms_obj.cleaned_data.get('send_email_content'),
                }
                send_email_list = forms_obj.cleaned_data.get('send_email_list')
                print('create_data -->', create_data, send_email_list)
                obj = models.TaskList.objects.create(**create_data)

                query = []
                for send_email in send_email_list:
                    query.append(
                        models.TaskInfo(to_email=send_email, task_list=obj)
                    )
                models.TaskInfo.objects.bulk_create(query)

                response.code = 200
                response.msg = "添加成功"
                response.data = {
                    'testCase': 1,
                    'id': 1,
                }
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            task_list_objs = models.TaskList.objects.filter(id=o_id)
            if task_list_objs:
                if task_list_objs[0].status == 1:
                    task_list_objs.update(is_delete=True)
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 300
                    response.msg = "该任务正在操作中，不能删除"

        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'password': request.POST.get('password'),
                'status': request.POST.get('status'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data['o_id']
                update_data = {
                    'status': forms_obj.cleaned_data['status'],
                }
                password = forms_obj.cleaned_data['password']
                if password:
                    update_data['password'] = password

                # 更新数据
                models.UserProfile.objects.filter(id=o_id).update(**update_data)

                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "test":
            form_data = {
                'send_email_title': request.POST.get('send_email_title'),
                'send_email_content': request.POST.get('send_email_content'),
                'send_email_list': request.POST.get('send_email_list'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = TestForm(form_data)
            if forms_obj.is_valid():
                email_user_obj = models.EmailUserInfo.objects.all().order_by('use_number')[0]
                email_user_obj.use_number += 1
                email_user_obj.save()
                email_user = email_user_obj.email_user
                email_pwd = email_user_obj.email_pwd
                print(email_user, email_pwd)
                send_email_title = forms_obj.cleaned_data.get('send_email_title')
                send_email_content = forms_obj.cleaned_data.get('send_email_content')
                send_email_list = forms_obj.cleaned_data.get('send_email_list')
                SendEmail.send_email(email_user, email_pwd, send_email_list, send_email_title, send_email_content)

                response.code = 200
                response.msg = "发送成功"
                response.data = {
                    'testCase': 1,
                    'id': 1,
                }
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)
