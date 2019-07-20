from django import forms
from hurong import models
import json




# 生成任务
class GeneratedTask(forms.Form):
    post_data = forms.CharField(
        required=True,
        error_messages={
            'required': "POST参数不能为空"
        }
    )


    def clean_post_data(self):
        post_data = eval(self.data.get('post_data'))
        for data in post_data:
            uid = data.get('uid')
            keyword = data.get('keyword')
            number = data.get('number')
            related_keyword = data.get('related_keyword')

            objs = models.XhsKeywordsList.objects.filter(uid=uid)
            if objs:
                objs.update(
                    uid=uid,
                    keyword=keyword,
                    number=number,
                    # related_keyword=related_keyword,
                    status=1,
                )
            else:
                if int(number) == 0:
                    number = 10
                models.XhsKeywordsList.objects.create(
                    uid=uid,
                    keyword=keyword,
                    number=number,
                    # related_keyword=related_keyword,
                )

# 重查任务
class GeavyCheckTask(forms.Form):
    post_data = forms.CharField(
        required=True,
        error_messages={
            'required': "POST参数不能为空"
        }
    )


    def clean_post_data(self):
        post_data = eval(self.data.get('post_data'))
        models.ArticlesAndComments.objects.filter(keyword__uid__in=post_data).delete()
        objs = models.XhsKeywordsList.objects.filter(uid__in=post_data)
        flag = False
        if objs:
            flag = True
            objs.update(
                last_select_time=None,
                total_count=0
            )
        return flag

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

# 删除任务
class DeleteTasks(forms.Form):
    post_data = forms.CharField(
        required=True,
        error_messages={
            'required': "POST参数不能为空"
        }
    )

    def clean_post_data(self):
        post_data = eval(self.data.get('post_data'))
        models.ArticlesAndComments.objects.filter(keyword__uid__in=post_data).delete()
        models.XhsKeywordsList.objects.filter(uid__in=post_data).delete()

# 查询任务
class QueryComments(forms.Form):
    article_comment = forms.CharField(
        required=True,
        error_messages={
            'required': "评论KEY不能为空"
        }
    )


