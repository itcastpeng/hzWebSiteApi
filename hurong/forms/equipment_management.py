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
    select_number = forms.CharField(
        required=True,
        error_messages={
            'required': "查询号码不能为空",
        }
    )


    def clean_select_number(self):
        select_number = self.data.get('select_number')
        data_list = []
        print('select_number------->', select_number)
        for i in select_number.split('\n'):
            if i:
                objs = models.MobileTrafficInformation.objects.filter(select_number=i)
                if objs:
                    continue
                if not i.strip().isdigit():
                    continue
                if i.strip() not in data_list:
                    data_list.append(i.strip())

        return data_list

class UpdateForm(forms.Form):
    select_number = forms.IntegerField(
        required=True,
        error_messages={
            'required': "查询号码不能为空",
        }
    )

    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改的ID不能为空",
        }
    )
    def clean_select_number(self):
        o_id = self.data.get('o_id')
        select_number = self.data.get('select_number')
        objs = models.MobileTrafficInformation.objects.filter(select_number=select_number).exclude(id=o_id)
        if objs:
            self.add_error('select_number', '该号码已存在')
        else:
            return select_number
