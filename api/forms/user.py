from django import forms
from api import models
from publicFunc.role_choice import admin_list
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

# 转接验证
class TransferAllUserInformation(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "登录异常"
        }
    )
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "转接人不能为空"
        }
    )
    transfer_template_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '小程序ID类型错误'
        }
    )
    def clean_o_id(self):
        o_id = self.data.get('o_id')
        user_id = self.data.get('user_id')
        if o_id == user_id:
            self.add_error('o_id', '不可转接给自己')
        objs = models.UserProfile.objects.filter(id=o_id)
        if objs:
            obj = objs[0]
            if obj.role_id not in admin_list:
                return o_id

            else:
                self.add_error('o_id', '不可转接给管理员')
        else:
            self.add_error('o_id', '您要转接的用户不存在')

    def clean_user_id(self):
        user_id = self.data.get('user_id')
        objs = models.UserProfile.objects.filter(id=user_id)
        if objs and objs[0].role_id not in admin_list:
            if objs[0].inviter:
                self.add_error('user_id', '转接失败')
            else:
                return user_id
        else:
            self.add_error('user_id', '管理员不可转接')

    def clean_transfer_template_id(self):
        transfer_template_id = self.data.get('transfer_template_id')
        if transfer_template_id:
            objs = models.Template.objects.filter(id=transfer_template_id)
            if objs:
                return transfer_template_id
            else:
                self.add_error('transfer_template_id', '模板不存在')


# 删除团队成员
class DeleteTeamMembers(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "登录异常"
        }
    )
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "请选择要删除的成员"
        }
    )

    def clean_user_id(self):
        user_id = self.data.get('user_id')
        o_id= self.data.get('o_id')

        objs = models.UserProfile.objects.filter(id=o_id)
        if objs:
            obj = objs[0]
            if obj.inviter and obj.inviter_id == int(user_id):
                return user_id
            else:
                if not obj.inviter:
                    self.add_error('user_id', '该成员未加入团队')
                else:
                    self.add_error('user_id', '权限不足')
        else:
            self.add_error('user_id', '删除成员不存在')



