from django import forms
from api import models
from publicFunc.role_choice import admin_list
from publicFunc.public import verify_phone_number







# 添加
class AddForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "名称不能为空"
        }
    )
    phone = forms.CharField(
        required=False,
    )
    jobs = forms.CharField(
        required=False,
    )
    email = forms.CharField(
        required=False,
    )
    wechat_num = forms.CharField(
        required=False,
    )
    address = forms.CharField(
        required=False,
    )
    heading = forms.CharField(
        required=False,
    )
    about_me = forms.CharField(
        required=False,
    )

    create_user_id = forms.CharField(
        required=False,
    )
    template_id = forms.CharField(
        required=True,
        error_messages={
            'required': "模板ID不能为空"
        }
    )
    def clean_name(self):
        name = self.data.get('name')
        create_user_id = self.data.get('create_user_id')
        objs = models.BusinessCard.objects.filter(name=name, create_user_id=create_user_id)
        if objs:
            self.add_error('name', '该名片名称已存在')
        else:
            return name

    def clean_phone(self):
        phone = self.data.get('phone')
        if phone:
            if verify_phone_number(phone):
                return phone
            else:
                self.add_error('phone', '手机号验证失败')
# 更新
class UpdateForm(forms.Form):
    o_id = forms.CharField(
        required=True,
        error_messages={
            'required': "请选择要修改的名片"
        }
    )
    template_id = forms.CharField(
        required=True,
        error_messages={
            'required': "模板ID不能为空"
        }
    )
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "名称不能为空"
        }
    )
    phone = forms.CharField(
        required=False,
    )
    jobs = forms.CharField(
        required=False,
    )
    email = forms.CharField(
        required=False,
    )
    wechat_num = forms.CharField(
        required=False,
    )
    address = forms.CharField(
        required=False,
    )
    heading = forms.CharField(
        required=False,
    )
    about_me = forms.CharField(
        required=False,
    )

    create_user_id = forms.CharField(
        required=False,
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        create_user_id = self.data.get('create_user_id')
        objs = models.BusinessCard.objects.filter(id=o_id)
        if not objs:
            self.add_error('o_id', '名片不存在')
        else:
            if int(objs[0].create_user_id) == int(create_user_id):
                return o_id
            else:
                self.add_error('o_id', '无权限操作')

    def clean_name(self):
        name = self.data.get('name')
        create_user_id = self.data.get('create_user_id')
        objs = models.BusinessCard.objects.filter(name=name, create_user_id=create_user_id)
        if objs:
            self.add_error('name', '该名片名称已存在')
        else:
            return name

    def clean_phone(self):
        phone = self.data.get('phone')
        if phone:
            if verify_phone_number(phone):
                return phone
            else:
                self.add_error('phone', '手机号验证失败')



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