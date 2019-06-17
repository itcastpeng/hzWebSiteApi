from django import forms

from hurong import models
from publicFunc import account
import re
import json


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


# 添加
class AddForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "小红书账户id不能为空",
            'invalid': "数据类型错误"
        }
    )

    content = forms.CharField(
        required=True,
        error_messages={
            'required': "笔记内容不能为空"
        }
    )

    release_time = forms.DateTimeField(
        required=True,
        error_messages={
            'required': "发布时间不能为空",
            'invalid': "发布时间格式错误"
        }
    )

    def clean_user_id(self):
        user_id = self.data['user_id']

        objs = models.XiaohongshuUserProfile.objects.filter(id=user_id)
        if objs:
            return user_id
        else:
            self.add_error('user_id', "小红书账户不存在")


class GetReleaseTaskForm(forms.Form):
    imsi = forms.IntegerField(
        required=True,
        error_messages={
            'required': "SIM卡ID不能为空"
        }
    )

    iccid = forms.IntegerField(
        required=True,
        error_messages={
            'required': "设备IMSI号不能为空"
        }
    )