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

        if '我的评论:' in comments_content:
            comments_content = comments_content.split('我的评论:')[0]

        return comments_content

    def clean_nick_name(self):
        nick_name = self.data.get('nick_name')

        if '评论了你的笔记' in nick_name:
            nick_name = nick_name.replace('评论了你的笔记', '')
        # elif '回复了你的评论' in nick_name:
        #     nick_name = nick_name.replace('回复了你的评论', '')
        elif '回复' in nick_name:
            nick_name = nick_name.split('回复')[0]

        elif '评论' in nick_name:
            nick_name = nick_name.split('评论')[0]

        return nick_name

    def clean_screenshots_address(self):
        screenshots_address = self.data.get('screenshots_address')
        if screenshots_address.endswith('400'):
            screenshots_address = screenshots_address[:-3] + '150'
        return screenshots_address

    def clean_article_picture_address(self):
        article_picture_address = self.data.get('article_picture_address')
        if article_picture_address.endswith('400'):
            article_picture_address = article_picture_address[:-3] + '150'
        return article_picture_address


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
    comment_type = forms.IntegerField(
            required=True,
            error_messages={
                'required': "评论类型不能为空"
            }
        )

    def clean_comment_id(self):
        comment_id = self.data.get('comment_id')
        objs = models.littleRedBookReviewForm.objects.filter(id=comment_id)
        if objs:
            return comment_id
        else:
            self.add_error('comment_id', '回复的评论不存在')

    def clean_comment_type(self):
        comment_type = int(self.data.get('comment_type'))
        if comment_type in [1, 2]:
            return comment_type
        else:
            self.add_error('comment_type', '请选择正确的评论类型')


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

        if 'www.xiaohongshu.com' in notes_url:
            link = notes_url.split('?')[0]

        else:
            print("notes_url -->", notes_url)
            ret = requests.get(notes_url, allow_redirects=False)
            print(ret.text)
            link = re.findall('HREF="(.*?)"', ret.text)[0].split('?')[0]

        biji_objs = models.XiaohongshuBiji.objects.filter(biji_existing_url=link)
        if biji_objs:
            biji_obj = biji_objs[0]
            return notes_url, biji_obj.id
        else:
            self.add_error('notes_url', '笔记不存在')

# 手机获取回复评论任务
class QueryReplyTask(forms.Form):
    imsi = forms.CharField(
        required=True,
        error_messages={
            'required': "IMSI不能为空"
        }
    )
    iccid = forms.CharField(
        required=True,
        error_messages={
            'required': "ICCID不能为空"
        }
    )
    platform = forms.IntegerField(
        required=False,
        error_messages={
            'required': "平台不能为空"
        }
    )

    def clean_iccid(self):
        iccid = self.data.get('iccid')
        imsi = self.data.get('imsi')

        objs = models.XiaohongshuPhone.objects.filter(iccid=iccid, imsi=imsi)
        if objs:
            obj = objs[0]
            return obj.id
        else:
            self.add_error('iccid', '设备不存在')

# 删除评论
class DeleteComment(forms.Form):
    comment_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "评论ID不能为空"
        }
    )

    def clean_comment_id(self):
        comment_id = self.data.get('comment_id')
        objs = models.littleRedBookReviewForm.objects.filter(id=comment_id)
        if objs:
            return comment_id, objs

        else:
            self.add_error('comment_id', '该评论ID 不存在')

# 查询删除评论任务 (手机端)
class QueryDeleteComment(forms.Form):
    imsi = forms.CharField(
        required=True,
        error_messages={
            'required': "IMSI不能为空"
        }
    )
    iccid = forms.CharField(
        required=True,
        error_messages={
            'required': "ICCID不能为空"
        }
    )
    platform = forms.IntegerField(
        required=False,
        error_messages={
            'required': "平台不能为空"
        }
    )

    def clean_iccid(self):
        iccid = self.data.get('iccid')
        imsi = self.data.get('imsi')

        objs = models.XiaohongshuPhone.objects.filter(iccid=iccid, imsi=imsi)
        if objs:
            obj = objs[0]
            return obj.id
        else:
            self.add_error('iccid', '设备不存在')







