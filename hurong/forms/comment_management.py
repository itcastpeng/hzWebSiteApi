from django import forms
from hurong import models
from publicFunc import account
import re, json, requests


# 手机端添加接口
class mobilePhoneReviews(forms.Form):
    xhs_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "小红书账号ID不能为空",
        }
    )
    head_portrait = forms.CharField(
        required=True,
        error_messages={
            'required': "头像不能为空"
        }
    )
    nick_name = forms.CharField(
        required=True,
        error_messages={
            'required': "昵称不能为空"
        }
    )
    comments_status = forms.IntegerField(
        required=True,
        error_messages={
            'required': "评论类型不能为空"
        }
    )
    comments_content = forms.CharField(
        required=True,
        error_messages={
            'required': "评论内容不能为空"
        }
    )
    article_picture_address = forms.CharField(
        required=True,
        error_messages={
            'required': "文章图片地址不能为空"
        }
    )
    article_notes_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "文章笔记不能为空"
        }
    )
    screenshots_address = forms.CharField(
        required=False,
        error_messages={
            'required': "截图地址不能为空"
        }
    )

    def clean_xhs_user_id(self):
        xhs_user_id = self.data.get('xhs_user_id')
        objs = models.XiaohongshuUserProfile.objects.filter(id=xhs_user_id)
        if objs:
            return xhs_user_id
        else:
            self.add_error('xhs_user_id', '小红书账号ID错误')

    def clean_article_notes_id(self):
        article_notes_id = self.data.get('article_notes_id')
        if article_notes_id:
            objs = models.XiaohongshuBiji.objects.filter(id=article_notes_id)
            if objs:
                return article_notes_id
            else:
                self.add_error('article_notes_id', '笔记不存在')

    def clean_comments_content(self):
        comments_content = self.data.get('comments_content')

        if '评论了你的笔记' in comments_content:
            comments_content = comments_content.replace('评论了你的笔记', '')
        elif '回复了你的评论' in comments_content:
            comments_content = comments_content.replace('回复了你的评论', '')
        elif '我的评论:' in comments_content:
            comments_content = comments_content.split('我的评论:')[0]
        else:
            comments_content = comments_content
        return comments_content




# 创建回复评论 小红书后台添加接口   (博主回复内容)
class ReplyCommentForm(forms.Form):

    comment_id = forms.IntegerField(
            required=True,
            error_messages={
                'required': "回复评论ID不能为空"
            }
        )
    comment_response = forms.CharField(
            required=True,
            error_messages={
                'required': "回复评论内容不能为空"
            }
        )


    def clean_comment_id(self):
        comment_id = self.data.get('comment_id')
        objs = models.littleRedBookReviewForm.objects.filter(id=comment_id)
        if objs:
            return comment_id
        else:
            self.add_error('comment_id', '回复的评论不存在')


# 判断是否是数字
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页显示数量类型错误"
        }
    )

    def clean_current_page(self):
        if 'current_page' not in self.data:
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length


# 回复评论是否成功
class ReplyCommentIsSuccess(forms.Form):
    id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "回复评论ID不能为空"
        }
    )
    comment_completion_time = forms.DateTimeField(
        required=True,
        error_messages={
            'required': "评论完成时间不能为空"
        }
    )
    def clean_comment_id(self):
        comment_id = self.data.get('comment_id')
        objs = models.commentResponseForm.objects.filter(id=comment_id)
        if objs:
            return comment_id
        else:
            self.add_error('comment_id', '回复评论ID不存在')

# 关联 截图 日记
class AssociatedScreenshots(forms.Form):
    screenshots = forms.CharField(
        required=True,
        error_messages={
            'required': "截图不能为空"
        }
    )
    notes_url = forms.CharField(
        required=True,
        error_messages={
            'required': "笔记回链不能为空"
        }
    )
    def clean_notes_url(self):
        notes_url = self.data.get('notes_url')
        ret = requests.get(notes_url, allow_redirects=False)
        link = re.findall('HREF="(.*?)"', ret.text)[0].split('?')[0]

        biji_objs = models.XiaohongshuBiji.objects.filter(biji_existing_url=link)
        if biji_objs:
            biji_obj = biji_objs[0]
            return notes_url, biji_obj.id
        else:
            self.add_error('notes_url', '笔记不存在')

