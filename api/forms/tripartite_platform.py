from django import forms

from api import models


# 添加
class AuthorizationForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '非法用户',
        }
    )
    appid = forms.CharField(
        required=True,
        error_messages={
            'required': 'APPID不能为空',
        }
    )
