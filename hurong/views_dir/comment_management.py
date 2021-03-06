from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hz_website_api_celery.tasks import asynchronous_transfer_data
from hurong.forms.comment_management import mobilePhoneReviews, ReplyCommentForm, \
    SelectForm, ReplyCommentIsSuccess, AssociatedScreenshots, QueryReplyTask, DeleteComment, QueryDeleteComment
from publicFunc.public import create_xhs_admin_response, send_error_msg
from publicFunc.base64_encryption import b64decode
import json, base64, datetime, requests


# 评论管理
@account.is_token(models.UserProfile)
def comment_management(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == 'POST':


        # 手机端添加接口  (获取用户的评论内容提交到接口保存)③
        if oper_type == "mobile_phone_reviews":
            iccid = request.POST.get('iccid')
            imsi = request.POST.get('imsi')

            objs = models.XiaohongshuPhone.objects.filter(
                iccid=iccid,
                imsi=imsi
            )
            if not objs:
                response.code = 301
                response.msg = '该设备不存在'

            else:
                obj = objs[0]
                user_objs = obj.xiaohongshuuserprofile_set.all()
                if not user_objs:
                    response.code = 301
                    response.msg = '该设备 未关联小红书客户'
                else:
                    xhs_user_id = user_objs[0].id
                    form_data = {
                        'xhs_user_id': xhs_user_id, # 小红书用户
                        'head_portrait': request.POST.get('head_portrait'), # 头像
                        'nick_name': request.POST.get('nick_name'), # 昵称
                        'comments_status': request.POST.get('comments_status'), # 评论类型
                        'comments_content': request.POST.get('comments_content'), # 评论内容
                        'article_picture_address': request.POST.get('article_picture_address'), # 文章图片地址
                        'article_notes_id': request.POST.get('article_notes_id'), # 文章笔记
                        'screenshots_address': request.POST.get('screenshots_address'), # 截图地址
                    }
                    forms_obj = mobilePhoneReviews(form_data)
                    if forms_obj.is_valid():
                        forms_data = forms_obj.cleaned_data
                        article_picture_address = forms_data.get('article_picture_address')
                        nick_name = forms_data.get('nick_name')
                        comments_content = forms_data.get('comments_content')
                        response.code = 200



                        rule_not_message_flag = True # 是否创建
                        rule_not_message = ['通知消息', '已被删除', '违规', '收藏', '新增关注', '评记']
                        for i in rule_not_message:
                            if i in comments_content:
                                rule_not_message_flag = False
                                break
                        article_notes_id = forms_data.get('article_notes_id')
                        if rule_not_message_flag and article_picture_address: # 如果没有截图不记录
                            objs = models.littleRedBookReviewForm.objects.filter(
                                        xhs_user_id=xhs_user_id,
                                        nick_name=nick_name,
                                        comments_content=comments_content
                                    )
                            print("**forms_obj.cleaned_data -->", forms_obj.cleaned_data)

                            if not objs and forms_data.get('comments_content') != "该评论已被删除":
                                obj = models.littleRedBookReviewForm.objects.create(**forms_obj.cleaned_data)
                                # 异步传递给小红书后台
                                form_data['link'] = forms_data.get('screenshots_address')
                                form_data['name'] = forms_data.get('nick_name')
                                form_data['content'] = forms_data.get('comments_content')
                                form_data['head_portrait'] = forms_data.get('head_portrait')
                                form_data['comment_id'] = obj.id
                                form_data['id'] = article_notes_id
                                form_data['transfer_type'] = 1  # 传递到小红书后台
                                form_data['platform'] = obj.xhs_user.platform
                                asynchronous_transfer_data.delay(form_data)
                                response.msg = '创建成功'
                        else:
                            response.msg = '通知消息, 未收录'


                    else:
                        response.code = 301
                        response.msg = json.loads(forms_obj.errors.as_json())

            create_xhs_admin_response(request, response, 3) # 创建请求日志(手机)

        # 创建回复评论 小红书后台添加接口   (博主回复内容)④
        elif oper_type == 'reply_comment':
            form_data = {
                'comment_id': request.POST.get('comment_id'),               # 回复哪个评论ID
                'comment_type': request.POST.get('comment_type'),           # (回复评论类型 1回复评论 2 回复私信)
                'comment_response': request.POST.get('comment_response'),   # 回复评论内容
            }

            forms_obj = ReplyCommentForm(form_data)
            if forms_obj.is_valid():
                comment_type = forms_obj.cleaned_data.get('comment_type')

                is_perform = True
                # if comment_type in [2, '2']:
                #     is_perform = False

                data = {
                    'comment_id': forms_obj.cleaned_data.get('comment_id'),
                    'comment_response': forms_obj.cleaned_data.get('comment_response'),
                    'comment_type': comment_type,
                    'is_perform': is_perform,
                }
                print(data)
                obj = models.commentResponseForm.objects.create(**data)
                response.code = 200
                response.msg = '创建成功'
                response.data = obj.id

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
            create_xhs_admin_response(request, response, 2) # 创建请求日志(小红书后台请求后台)

        # 刪除评论(小红书请求)
        elif oper_type == 'delete_comment':
            form_data = {
                'comment_id': request.POST.get('comment_id'),  # 删除哪个评论ID
            }
            form_obj = DeleteComment(form_data)
            if form_obj.is_valid():
                comment_id, objs = form_obj.cleaned_data.get('comment_id')
                delete = 2
                if objs[0].comments_content in ['该评论已被删除', '该评论违规']:
                    models.commentResponseForm.objects.filter(comment=objs).delete()
                    delete = 3
                    msg = '删除成功'
                    code = 0

                else:
                    code = 200
                    msg = '操作成功, 等待删除...'

                objs.update(delete=delete)
                response.code = code
                response.msg = msg

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())
            create_xhs_admin_response(request, response, 2) # 创建请求日志(小红书后台请求后台)

        # 手机端 删除评论是否完成
        elif oper_type == 'reply_comment_is_delete':
            id = request.POST.get('comment_id')      # 删除的消息ID
            objs = models.littleRedBookReviewForm.objects.filter(
                id=id
            )
            if objs:
                models.commentResponseForm.objects.filter(comment_id=id).delete()
                objs.update(
                    delete=3
                )
                data = {
                    'transfer_type': 4,
                    'id': id
                }
                asynchronous_transfer_data.delay(data)
                create_xhs_admin_response(request, response, 3)  # 创建请求日志(手机端)
            response.code = 200
            response.msg = '操作完成'

        # 手机端 通知回复消息完成时间⑥
        elif oper_type == 'reply_comment_is_success':
            now = datetime.datetime.today()
            form_data = {
                'id': request.POST.get('comment_id'),  # 回复的消息ID
                'comment_completion_time': request.POST.get('comment_completion_time', now),  # 完成时间
            }

            form_objs = ReplyCommentIsSuccess(form_data)
            if form_objs.is_valid():
                comment_id = form_objs.cleaned_data.get('id')
                comment_completion_time = form_objs.cleaned_data.get('comment_completion_time')

                objs = models.commentResponseForm.objects.filter(id=comment_id)
                objs.update(
                    comment_completion_time=comment_completion_time
                )
                response.code = 200
                response.msg = '成功'

                # 异步传递给小红书后台
                form_data['transfer_type'] = 2
                form_data['platform'] = objs[0].comment.xhs_user.platform
                asynchronous_transfer_data.delay(form_data)

            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())
            create_xhs_admin_response(request, response, 3)  # 创建请求日志(手机端)

        # 关联 笔记链接 和 文章截图②
        elif oper_type == 'associated_screenshots':
            form_data = {
                'notes_url': request.POST.get('notes_url'),  # 笔记回链
                'screenshots': request.POST.get('screenshots')  # 文章截图
            }
            print('form_data-----------> ', form_data)
            code = 301
            form_obj = AssociatedScreenshots(form_data)
            if form_obj.is_valid():
                forms_data = form_obj.cleaned_data
                screenshots = forms_data.get('screenshots')
                screenshots = screenshots.split('?')[0]
                notes_url, biji_id = forms_data.get('notes_url')

                objs = models.noteAssociationScreenshot.objects.filter(
                    screenshots=screenshots,
                    notes_id=biji_id
                )
                if not objs:

                    models.noteAssociationScreenshot.objects.create(
                        screenshots=screenshots,
                        notes_id=biji_id
                    )

                    code = 200
                    msg = '关联成功'
                    response.data = biji_id
                else:
                    code = 200
                    msg = '重复关联'
                    response.data = biji_id

            else:
                iccid = request.POST.get('iccid')
                imsi = request.POST.get('imsi')
                phone_objs = models.XiaohongshuPhone.objects.filter(iccid=iccid, imsi=imsi)
                device_number = '设备不存在, iccid:{}, imsi:{}'.format(iccid, imsi)
                if phone_objs:
                    device_number = phone_objs[0].name
                content = '{datetime}关联笔记截图异常, \n设备号:{device_number}, \n笔记回链:{notes_url}'.format(
                    datetime=datetime.datetime.today(),
                    device_number=device_number,
                    notes_url=form_data.get('notes_url')
                )
                send_error_msg(content, 2)
                msg = json.loads(form_obj.errors.as_json())

            response.code = code
            response.msg = msg
            create_xhs_admin_response(request, response, 3)  # 创建请求日志(手机端)

        # 修改 回复(管理/私信) 是否开放
        elif oper_type == 'whether_the_modification_open':
            comment_id = request.POST.get('comment_id')
            objs = models.commentResponseForm.objects.filter(id=comment_id)
            if objs:
                obj = objs[0]
                obj.is_perform = bool(1-obj.is_perform)
                obj.save()
                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = '修改的任务不存在'



        # 回复评论管理 发布异常(手机)
        elif oper_type == 'comment_management_changed_publish_exceptions':
            comment_id = request.POST.get('comment_id')
            objs = models.commentResponseForm.objects.filter(
                id=comment_id,
                comment_completion_time__isnull=True
            )
            if objs:
                objs.update(
                    is_error=True,
                    comment_completion_time=datetime.datetime.today()
                )
                response.code = 200
                response.msg = '发布异常成功'
            else:
                response.code = 301
                response.msg = '该任务不存在或已发布'

        # 回复评论管理 发布正常(后台)
        elif oper_type == 'reply_comment_management_release_normal':
            comment_id = request.POST.get('comment_id')
            objs = models.commentResponseForm.objects.filter(id=comment_id)
            if objs:
                objs.update(
                    is_error=False,
                    comment_completion_time=None,
                )
                response.code = 200
                response.msg = '重新发布成功'

            else:
                response.code = 301
                response.msg = '该任务不存在'

        # 评论改为删除异常 (手机)
        elif oper_type == 'comment_post_exception_instead':
            comment_id = request.POST.get('comment_id')
            objs = models.littleRedBookReviewForm.objects.filter(id=comment_id)
            if objs and objs[0].is_error == False:
                objs.update(is_error=True)
                response.code = 200
                response.msg = '删除异常成功'

            else:
                if objs:
                    response.msg = '该评论不存在'
                else:
                    response.msg = '该评论已经为删除异常'
                response.code = 301


        """当 手机找不到 评论 和 回复评论 时 改为发布异常"""

    else:

        order = request.GET.get('order', '-create_datetime')

        # 查询 截图和 笔记是否关联①
        if oper_type == 'determine_correlation':

            flag = False
            iccid = request.GET.get('iccid')
            imsi = request.GET.get('imsi')
            screenshots = request.GET.get('screenshots') # 文章截图
            # notes_url = request.GET.get('notes_url') # 笔记回链
            biji_id = ''
            if screenshots:
                objs = models.noteAssociationScreenshot.objects.filter(
                    screenshots=screenshots,
                    notes__user_id__phone_id__iccid=iccid,
                    notes__user_id__phone_id__imsi=imsi,
                )
                if objs:
                    obj = objs[0]
                    biji_id = obj.notes_id
                    flag = True

                response.code = 200
                response.msg = '查询完成'
                response.data = {
                    'flag': flag,
                    'biji_id': biji_id
                }

            else:
                response.code = 301
                response.msg = '参数异常'
            create_xhs_admin_response(request, response, 3)  # 创建请求日志(手机端)

        # 查询回复任务（手机）⑤
        elif oper_type == 'query_reply_task':
            form_data = {
                'imsi': request.GET.get('imsi'),
                'iccid': request.GET.get('iccid'),
                'platform': request.GET.get('platform', 1),
            }
            form_obj = QueryReplyTask(form_data)
            if form_obj.is_valid():
                iccid = form_obj.cleaned_data.get('iccid')
                platform = form_obj.cleaned_data.get('platform')

                objs = models.commentResponseForm.objects.select_related('comment').filter(
                    comment__xhs_user__phone_id_id=iccid,
                    comment_completion_time__isnull=True,
                    comment__isnull=False,
                    comment_response__isnull=False,
                    is_perform=True,
                    is_error=False,
                    comment__xhs_user__platform=platform
                ).order_by('create_datetime')

                if objs:
                    obj = objs[0]
                    comment_response = obj.comment_response

                    ret_data = {
                        'comment_type': obj.comment_type,
                        'comments_content': obj.comment.comments_content,
                        'nick_name': obj.comment.nick_name,
                        'article_picture_address': obj.comment.article_picture_address,
                        'screenshots_address': obj.comment.screenshots_address,
                        'id': obj.id,
                        'platform': obj.comment.xhs_user.platform,
                        'comment_response': comment_response,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    }

                    response.msg = '查询成功'
                    response.data = ret_data
                    response.note = {
                        'id': '回复评论ID',
                        'comment_response': '回复评论内容',
                        'create_datetime': '创建时间',
                        'screenshots_address': '文章截图',
                        'nick_name': '昵称',
                        'comments_content': '评论内容',
                        'comment_type': '评论类型 1为回复评论 2为回复私信',
                    }

                else:
                    response.msg = '无任务'

                response.code = 200
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())
            create_xhs_admin_response(request, response, 3)  # 创建请求日志(手机端)

        # 查询删除评论任务(手机)
        elif oper_type == 'query_delete_comment':
            form_data = {
                'imsi': request.GET.get('imsi'),
                'iccid': request.GET.get('iccid'),
                'platform': request.GET.get('platform'),
            }
            form_obj = QueryDeleteComment(form_data)
            if form_obj.is_valid():
                iccid = form_obj.cleaned_data.get('iccid')
                platform = form_obj.cleaned_data.get('platform')

                objs = models.littleRedBookReviewForm.objects.filter(
                    xhs_user__phone_id_id=iccid,
                    delete=2,
                    is_error=False,
                    xhs_user__platform=platform
                )
                data = {}
                if objs:
                    obj = objs[0]
                    data = {
                        'id': obj.id,
                        'comments_content':obj.comments_content,
                        'screenshots_address':obj.screenshots_address,
                        'phone_name':obj.xhs_user.phone_id.name,
                        'user_name':obj.nick_name,
                        'platform':obj.xhs_user.platform,
                    }

                else:
                    response.msg = '无任务'
                response.code = 200
                response.data = data
                response.note = {
                    'id': '删除评论ID',
                    'comments_content': '删除评论',
                    'screenshots_address': '截图',
                    'phone_name': '设备名称',
                    'user_name': '小红书博主名称',
                }

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())
            create_xhs_admin_response(request, response, 3)  # 创建请求日志(手机端)

        # 查询评论（胡蓉后台）
        elif oper_type == 'query_comments':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                field_dict = {
                    'id': '',
                    'comments_status': '',
                    'xhs_user_id': '',
                    'xhs_user__phone_id__name': '__contains',
                    'delete': '',
                    'xhs_user__name': '__contains',
                    'comments_content': '__contains',
                    'article_notes__isnull': '',
                }

                q = conditionCom(request, field_dict)

                objs = models.littleRedBookReviewForm.objects.filter(q).order_by(order)

                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    article_notes_title = ''
                    article_notes_id = ''
                    if obj.article_notes:
                        article_notes_id = obj.article_notes_id
                        article_notes_title = b64decode(obj.article_notes.title)

                    ret_data.append({
                        'id': obj.id,
                        'phone_name': obj.xhs_user.phone_id.name,
                        'phone_id': obj.xhs_user.phone_id_id,
                        'phone_number': obj.xhs_user.phone_id.phone_num,
                        'xhs_user_id': obj.xhs_user_id,
                        'xhs_user_name': obj.xhs_user.name,
                        'head_portrait': obj.head_portrait,
                        'screenshots_address': obj.screenshots_address,
                        'nick_name': obj.nick_name,
                        'comments_status_id': obj.comments_status,
                        'comments_status': obj.get_comments_status_display(),
                        'comments_content': obj.comments_content,
                        'article_picture_address': obj.article_picture_address,
                        'delete_id': obj.delete,
                        'delete': obj.get_delete_display(),
                        'article_notes_id': article_notes_id,
                        'article_notes_title': article_notes_title,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                response.note = {
                    'xhs_user_id': '小红书用户ID',
                    'xhs_user_name': '小红书用户名称',
                    'head_portrait': '头像',
                    'nick_name': '昵称',
                    'comments_status_id': '评论类型ID',
                    'screenshots_address': '截图地址',
                    'comments_status': '评论类型',
                    'comments_content': '评论内容',
                    'article_picture_address': '文章图片地址',
                    'article_notes_id': '笔记ID',
                    'create_datetime': '创建时间',
                }
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data':ret_data,
                    'count':count,
                    'comments_choices': [{'id':i[0], 'name':i[1]} for i in models.littleRedBookReviewForm.comments_choices],
                    'delete_choices': [{'id':i[0], 'name':i[1]} for i in models.littleRedBookReviewForm.delete_choices],
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 查询回复评论（胡蓉后台）
        elif oper_type == 'query_reply_comment':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                field_dict = {
                    'id': '',
                    'comment_id': '',
                    'comment_type': '',
                    'comment_response': '',
                    'comment_completion_time': '__isnull',
                    'comment__xhs_user__name': '__contains',
                    'comment__xhs_user__phone_id__name': '__contains',
                }

                q = conditionCom(request, field_dict)
                objs = models.commentResponseForm.objects.filter(q).order_by(order)

                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                ret_data = []
                for obj in objs:
                    comment_completion_time = obj.comment_completion_time
                    if comment_completion_time:
                        comment_completion_time = obj.comment_completion_time.strftime('%Y-%m-%d %H:%M:%S')

                    phone_id = ''
                    phone_name = ''
                    phone_number = ''
                    if obj.comment.xhs_user.phone_id:
                        phone_id = obj.comment.xhs_user.phone_id_id
                        phone_name = obj.comment.xhs_user.phone_id.name
                        phone_number = obj.comment.xhs_user.phone_id.phone_num

                    try:
                        comment_response =  str(base64.b64decode(obj.comment_response), 'utf8')
                    except Exception:
                        comment_response = obj.comment_response

                    ret_data.append({
                        'id': obj.id,
                        'phone_id': phone_id,
                        'phone_name': phone_name,
                        'phone_number': phone_number,
                        'xhs_user_name': obj.comment.xhs_user.name,
                        'nick_name': obj.comment.nick_name,
                        'head_portrait': obj.comment.head_portrait,
                        'comments_content': obj.comment.comments_content,
                        'comment_id': obj.comment_id,
                        'comment_response':comment_response,
                        'comment_type_id':obj.comment_type,
                        'comment_type':obj.get_comment_type_display(),
                        'is_perform':obj.is_perform,
                        'is_error':obj.is_error,
                        'comment_completion_time': comment_completion_time,
                        'create_datetime':obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                    'comment_type_choices': [{'id':i[0], 'name':i[1]} for i in models.commentResponseForm.comment_type_choices]
                }

        # 查询评论最后一次更新时间
        elif oper_type == 'query_when_comments_were_last_updated':
            form_data = {
                'iccid':request.GET.get('iccid'),
                'imsi': request.GET.get('imsi')
            }
            objs = models.XiaohongshuPhone.objects.filter(**form_data)
            if objs:
                obj = objs[0]
                comment_last_updated = obj.comment_last_updated
                deletionTime = (datetime.datetime.today() - datetime.timedelta(hours=12))  # 当前时间减去12小时
                more_than_12_hours = False
                if comment_last_updated:
                    comment_last_updated = comment_last_updated.strftime('%Y-%m-%d %H:%M:%S')
                    if deletionTime > obj.comment_last_updated:
                        more_than_12_hours = True
                else:
                    more_than_12_hours = True

                response.data = {
                    'comment_last_updated': comment_last_updated,
                    'more_than_12_hours': more_than_12_hours,
                }
                response.note = {
                    'comment_last_updated': '最后一次提交评论时间',
                    'more_than_12_hours': '最后一次提交评论时间 是否超过12小时 True已超过 False未超过',
                }
            response.code = 200

        # 手动关联评论/笔记 (胡蓉后台)
        elif oper_type == 'manually_associate_comments_notes':
            article_notes_id = request.GET.get('article_notes_id')
            comment_id = request.GET.get('comment_id')
            code = 301

            objs = models.littleRedBookReviewForm.objects.filter(id=comment_id)
            if objs:
                if not models.XiaohongshuBiji.objects.filter(id=article_notes_id):
                    msg = '笔记不存在'

                else:
                    objs.update(article_notes_id=article_notes_id)
                    code = 200
                    msg = '修改成功'
                    form_data = {
                        'transfer_type': 7,
                        'id': article_notes_id,
                        'comment_id': comment_id,
                    }
                    asynchronous_transfer_data.delay(form_data)

            else:
                msg = '评论不存在'

            response.code = code
            response.msg = msg

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)