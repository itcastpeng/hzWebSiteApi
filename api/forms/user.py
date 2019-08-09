from django import forms
from api import models


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


# 修改角色
class UpdateRoleForm(forms.Form):
    role_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "角色ID不能为空"
        }
    )
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "登录人用户ID不能为空"
        }
    )
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "要修改的用户ID不能为空"
        }
    )

    def clean_role_id(self):
        role_id = self.data.get('role_id')
        if models.Role.objects.filter(id=role_id):
            return role_id
        else:
            self.add_error('role_id', '角色ID不存在')





