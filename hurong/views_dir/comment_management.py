from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hz_website_api_celery.tasks import asynchronous_transfer_data
from hurong.forms.comment_management import mobilePhoneReviews, ReplyCommentForm, SelectForm, ReplyCommentIsSuccess
import json, requests, base64, time, os, datetime


# 评论管理
@account.is_token(models.UserProfile)
def comment_management(request, oper_type):
    response = Response.ResponseObj()

    if request.method == 'POST':


        # 手机端添加接口  (获取用户的评论内容提交到接口保存)
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
                    }
                    forms_obj = mobilePhoneReviews(form_data)
                    if forms_obj.is_valid():
                        models.littleRedBookReviewForm.objects.create(**forms_obj.cleaned_data)
                        response.code = 200
                        response.msg = '创建成功'

                        # 异步传递给小红书后台
                        # form_data['transfer_type'] = 1 # 传递到小红书后台
                        # asynchronous_transfer_data.delay(form_data)
                    else:
                        response.code = 301
                        response.msg = json.loads(forms_obj.errors.as_json())


        # 创建回复评论 小红书后台添加接口   (博主回复内容)
        elif oper_type == 'reply_comment':
            form_data = {
                'comment_id': request.POST.get('comment_id'),           # 回复哪个评论ID
                'comment_response': request.POST.get('comment_response'), # 回复评论内容
                # 'comment_completion_time': request.POST.get('comment_completion_time'), # 回复评论完成时间
            }

            forms_obj = ReplyCommentForm(form_data)
            if forms_obj.is_valid():
                models.commentResponseForm.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = '创建成功'

                # 异步传递给手机
                form_data['transfer_type'] = 2  # 传递到手机
                asynchronous_transfer_data.delay(form_data)

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 手机端 通知回复消息是否成功
        elif oper_type == 'reply_comment_is_success':
            form_data = {
                'comment_id': request.POST.get('comment_id'),  # 回复的消息ID
                # 'is_success': request.POST.get('is_success'),  # 回复的消息是否成功 (0 失败, 1 成功)
            }

            form_objs = ReplyCommentIsSuccess(form_data)
            if form_objs.is_valid():
                comment_id = form_objs.cleaned_data.get('comment_id')

                objs = models.commentResponseForm.objects.filter(id=comment_id)
                objs.update(
                    comment_completion_time=datetime.datetime.today()
                )
                response.code = 200
                response.msg = '成功'

                # 异步传递给小红书后台
                form_data['transfer_type'] = 3  # 传递到手机
                asynchronous_transfer_data.delay(form_data)

            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())

        # 关联 笔记链接 和 文章截图
        elif oper_type == 'associated_screenshots':
            screenshots = request.POST.get('screenshots')  # 文章截图
            notes_url = request.POST.get('notes_url')  # 笔记回链

            code = 301
            if not screenshots or not notes_url:
                msg = '参数异常'

            else:
                biji_objs = models.XiaohongshuBiji.objects.filter(biji_url=notes_url)
                if biji_objs:
                    biji_obj = biji_objs[0]

                    objs = models.noteAssociationScreenshot.objects.filter(
                        screenshots=screenshots,
                        notes_id=biji_obj.id
                    )
                    if not objs:

                        models.noteAssociationScreenshot.objects.create(
                            screenshots=screenshots,
                            notes_id=biji_obj.id
                        )

                        code = 200
                        msg = '关联成功'
                        response.data = biji_obj.id
                    else:
                        msg = '重复关联'
                else:
                    msg = '笔记不存在'

            response.code = code
            response.msg = msg


    else:

        # 查询 截图和 笔记是否关联
        if oper_type == 'determine_correlation':

            flag = False
            screenshots = request.GET.get('screenshots') # 文章截图
            # notes_url = request.GET.get('notes_url') # 笔记回链

            if screenshots:
                objs = models.noteAssociationScreenshot.objects.filter(
                    screenshots=screenshots,
                )
                if objs:
                    flag = True

                response.code = 200
                response.msg = '查询完成'
                response.data = flag

            else:
                response.code = 301
                response.msg = '参数异常'

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)