from django import forms
from api import models
from publicFunc.role_choice import admin_list
import json







# 添加
class AddForm(forms.Form):
    template_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "模板ID不能为空"
        }
    )
    article_content = forms.CharField(
        required=True,
        error_messages={
            'required': "文章内容不能为空"
        }
    )
    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "登录失败"
        }
    )

    def clean_template_id(self):
        template_id = self.data.get('template_id')
        objs = models.Template.objects.filter(id=template_id)
        if objs and objs[0].create_user.role_id not in admin_list:
            return template_id
        else:
            if objs:
                self.add_error('template_id', '该模板不可添加表单')
            else:
                self.add_error('template_id', '模板不存在')

    def clean_create_user_id(self):
        create_user_id = self.data.get('create_user_id')
        objs = models.UserProfile.objects.get(id=create_user_id)
        if objs and objs.role_id not in admin_list:
            return create_user_id
        else:
            self.add_error('create_user_id', '权限不足')



# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '公司id不能为空'
        }
    )
    article_content = forms.CharField(
        required=True,
        error_messages={
            'required': "文章内容不能为空"
        }
    )
    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "登录失败"
        }
    )

    def clean_create_user_id(self):
        create_user_id = self.data.get('create_user_id')
        objs = models.UserProfile.objects.get(id=create_user_id)
        if objs and objs.role_id not in admin_list:
            return create_user_id
        else:
            self.add_error('create_user_id', '权限不足')

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.ReservationForm.objects.filter(id=o_id)
        if objs:
            return o_id
        else:
            self.add_error('o_id', '该表单不存在')



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