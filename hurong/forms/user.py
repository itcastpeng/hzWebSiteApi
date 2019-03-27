from django import forms

from hurong import models
from publicFunc import account


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


# 添加用户
class AddForm(forms.Form):
    username = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空",
            'invalid': "数据类型错误"
        }
    )

    password = forms.CharField(
        required=True,
        error_messages={
            'required': "密码不能为空",
            'invalid': "数据类型错误"
        }
    )
    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "创建人不能为空",
            'invalid': "数据类型错误"
        }
    )

    def clean_username(self):
        username = self.data['username']
        objs = models.UserProfile.objects.filter(username=username)
        if objs.count() > 0:
            self.add_error('username', '用户名已存在')
        else:
            return username

    def clean_password(self):
        password = self.data['password']
        return account.get_token(password)


# 修改用户
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改id不能为空",
            'invalid': "数据类型错误"
        }
    )
    password = forms.CharField(
        required=False,
        error_messages={
            'required': "密码不能为空",
            'invalid': "数据类型错误"
        }
    )

    status = forms.IntegerField(
        required=True,
        error_messages={
            'required': "状态不能为空",
            'invalid': "数据类型错误"
        }
    )

    def clean_password(self):
        password = self.data['password']

        # 如果密码为空，则表示不修改密码
        if not password:
            return False

        return account.str_encrypt(password)
