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
            form_data = {
                'xhs_user_id': request.POST.get('xhs_user_id'), # 小红书账号ID
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
                form_data['transfer_type'] = 1 # 传递到小红书后台
                asynchronous_transfer_data.delay(form_data)
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

    else:

        #
        if oper_type == 'xxx':
            pass

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)