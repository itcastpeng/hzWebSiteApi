from django import forms

# from api import models
from publicFunc import account
# import time


# 判断是否是数字
class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空",
            'invalid': "参数数据类型错误"
        }
    )

    password = forms.CharField(
        required=True,
        error_messages={
            'required': "密码不能为空",
            'invalid': "参数数据类型错误"
        }
    )

    def clean_password(self):
        password = self.data['password']
        return account.str_encrypt(password)
