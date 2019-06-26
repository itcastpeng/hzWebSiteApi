from django import forms

from hurong import models
import json


# 添加
class AddForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "角色名称不能为空"
        }
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        }
    )

    permissionsList = forms.CharField(
        required=True,
        error_messages={
            'required': "选择权限不能为空"
        }
    )

    # 查询名称是否存在
    def clean_name(self):
        name = self.data['name']
        objs = models.Role.objects.filter(
            name=name,
        )
        if objs:
            self.add_error('name', '角色名称已存在')
        else:
            return name

    def clean_permissionsList(self):
        permissionsList = self.data.get('permissionsList')
        return json.loads(permissionsList)

# 更新
class UpdateForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': '角色名称不能为空'
        }
    )
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '角色id不能为空'
        }
    )

    permissionsList = forms.CharField(
        required=True,
        error_messages={
            'required': "选择权限不能为空"
        }
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "选择权限不能为空"
        }
    )

    # 判断名称是否存在
    def clean_name(self):
        o_id = self.data['o_id']
        name = self.data['name']
        objs = models.Role.objects.filter(
            name=name,
        ).exclude(id=o_id)
        if objs:
            self.add_error('name', '角色名称已存在')
        else:
            return name

    def clean_permissionsList(self):
        permissionsList = self.data.get('permissionsList')
        return json.loads(permissionsList)

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