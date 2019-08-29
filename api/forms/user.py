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


# 创建子账户
class OpenSubAccount(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "登录异常"
        }
    )
    user_list = forms.CharField(
        required=True,
        error_messages={
            'required': "请选择子账户"
        }
    )

    def clean_user_id(self):
        user_id = self.data.get('user_id')
        user_list = self.data.get('user_list')
        user_list = json.loads(user_list)
        len_user_list = len(user_list)
        inviter_user_objs = models.UserProfile.objects.filter(inviter_id=user_id)
        total_owned = int(inviter_user_objs.count()) + int(len_user_list)

        user_obj = models.UserProfile.objects.get(id=user_id)

        if int(user_obj.number_child_users) >= int(total_owned): # 后台总子账户数量 大于等于 已经在子账户 + 要添加的子账户 数量
            pass


        else:
            self.add_error('user_id', '您的子账户已达到上限')


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

    def clean_o_id(self):
        o_id = self.data.get('o_id')
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
            return user_id
        else:
            self.add_error('user_id', '管理员不可转接')





