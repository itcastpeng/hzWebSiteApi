from django import forms

from api import models
import json


# 添加
class AddForm(forms.Form):
    data = forms.CharField(
        required=True,
        error_messages={
            'required': "表单数据不能为空"
        }
    )
    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        }
    )

    template_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "模板id不能为空"
        }
    )


# 更新
class UpdateForm(forms.Form):
    status = forms.BooleanField(
        required=True,
        error_messages={
            'required': "表单数据不能为空"
        }
    )


# 判断是否是数字
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页显示数量类型错误"
        }
    )

    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
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