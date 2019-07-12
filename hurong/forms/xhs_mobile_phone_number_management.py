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

    log_msg = forms.CharField(
        required=True,
        # error_messages={
        #     'required': "日志信息不能为空"
        # }
    )


# 修改用户
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改id不能为空",
            'invalid': "数据类型错误"
        }
    )
