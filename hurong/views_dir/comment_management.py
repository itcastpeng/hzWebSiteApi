from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.comment_management import mobilePhoneReviews, ReplyCommentForm, SelectForm
import json, requests, base64, time, os


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

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


    else:

        # 查询 评论
        if oper_type == 'query_the_comments':

            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                user_id = request.GET.get('user_id')
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                    'cardbaldata': '__contains',
                    'select_number': '__contains',
                    'cardnumber': '__contains',
                    'create_datetime': '',
                }

                q = conditionCom(request, field_dict)

                objs = models.littleRedBookReviewForm.objects.filter()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]


            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 查询回复评论
        elif oper_type == '':
            pass

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)