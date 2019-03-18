from django import forms

from api import models
import re


def length_the_days(the_length):
    if int(the_length) == 2:
        renewal_number_days = 180
    elif int(the_length) == 3:
        renewal_number_days = 365
    elif int(the_length) == 4:
        renewal_number_days = 730
    else:
        renewal_number_days = 30

    return the_length, renewal_number_days


# 添加
class AddForm(forms.Form):
    price = forms.IntegerField(
        required=True,
        error_messages={
            'required': '价格不能为空'
        }
    )

    the_length = forms.IntegerField(
        required=True,
        error_messages={
            'required': "时长不能为空"
        }
    )
    original_price = forms.IntegerField(
        required=True,
        error_messages={
            'required': "原价不能为空"
        }
    )

    def clean_the_length(self):
        the_length = self.data.get('the_length')
        the_length, renewal_number_days = length_the_days(the_length)
        return the_length, renewal_number_days


# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章id不能为空'
        }
    )

    price = forms.IntegerField(
        required=True,
        error_messages={
            'required': '价格不能为空'
        }
    )

    the_length = forms.IntegerField(
        required=True,
        error_messages={
            'required': "时长不能为空"
        }
    )
    original_price = forms.IntegerField(
        required=True,
        error_messages={
            'required': "原价不能为空"
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.renewal_management.objects.filter(id=o_id)
        if objs:
            return o_id, objs
        else:
            self.add_error('o_id', '修改ID不存在')

    def clean_the_length(self):
        the_length = self.data.get('the_length')
        the_length, renewal_number_days = length_the_days(the_length)
        return the_length, renewal_number_days


# 删除
class DeleteForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "修改ID不能为空"
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.renewal_management.objects.filter(id=o_id)
        if objs:
            return o_id, objs
        else:
            self.add_error('o_id', '删除ID不存在')


# 查询
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


# 海报修改
class UpdatePosterInfoForm(forms.Form):
    title = forms.CharField(
        required=True,
        error_messages={
            'invalid': "标题不能为空"
        }
    )
    subtitle = forms.CharField(
        required=True,
        error_messages={
            'invalid': "副标题不能为空"
        }
    )
    phone = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "手机号不能为空"
        }
    )
    name = forms.CharField(
        required=True,
        error_messages={
            'invalid': "姓名不能为空"
        }
    )
    place = forms.CharField(
        required=True,
        error_messages={
            'invalid': "地点不能为空"
        }
    )

    time = forms.CharField(
        required=True,
        error_messages={
            'invalid': "时间不能为空"
        }
    )

    def clean_phone(self):
        phone = self.data.get('phone')
        phone_pat = re.compile("^(13\\d|14[5|7]|15\\d|166|17[3|6|7]|18\\d)\\d{8}$")
        res = re.search(phone_pat, phone)
        if res:
            return phone
        else:
            self.add_error('phone', '请填写正确电话号码')

    def clean_name(self):
        name = self.data.get('name')
        name_len = len(name)
        num = 0
        if name_len <= 10:
            for ch in name:  # Unicdoe 4E00~9FFF表示中文
                if '\u4e00' <= ch <= '\u9fff':
                    num += 1
            if name_len == num:
                return name
            else:
                self.add_error('name', '请输入中文姓名')
        else:
            self.add_error('name', '名字过长')

    def clean_title(self):
        title = self.data.get('title')
        if len(title) <= 15:
            return title
        else:
            self.add_error('title', '标题过长')

    def clean_subtitle(self):
        subtitle = self.data.get('subtitle')
        if len(subtitle) <= 15:
            return subtitle
        else:
            self.add_error('subtitle', '副标题过长')

    def clean_place(self):
        place = self.data.get('place')
        if len(place) <= 20:
            return place
        else:
            self.add_error('place', '地点过长')
