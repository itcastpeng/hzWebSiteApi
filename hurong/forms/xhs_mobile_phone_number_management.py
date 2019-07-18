from django import forms

from hurong import models
from publicFunc import account
from publicFunc.public import verify_phone_number
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


# 添加手机号
class AddForm(forms.Form):
    phone_number = forms.CharField(
        required=True,
        error_messages={
            'required': "手机号不能为空"
        }
    )
    # def clean_phone_number(self):
    #     phone_number = self.data.get('phone_number')
    #     if verify_phone_number(phone_number):
    #         return phone_number
    #     else:
    #         self.add_error('phone_number', '手机号异常')


# 修改手机号
class UpdateForm(forms.Form):
    id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "手机号ID不能为空"
        }
    )
    phone_number = forms.CharField(
        required=True,
        error_messages={
            'required': "手机号不能为空"
        }
    )
    remark = forms.CharField(
        required=False,
        error_messages={
            'required': "备注类型错误"
        }
    )
    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        if verify_phone_number(phone_number):
            return phone_number
        else:
            self.add_error('phone_number', '手机号异常')

    def clean_id(self):
        id = self.data.get('id')
        objs = models.PhoneNumber.objects.filter(id=id)
        if objs:
            return id
        else:
            self.add_error('id', '手机号不存在')

# 删除手机号
class DeleteForm(forms.Form):
    id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "手机号ID不能为空"
        }
    )
    models.text_messages_received_cell_phone_number.objects.filter(

    )


