from django import forms

# from hurong import models
# from publicFunc import account
# import re
# import json


# 判断是否需要更新个人信息
class IsUpdateUserinfoForm(forms.Form):
    imsi = forms.IntegerField(
        required=True,
        error_messages={
            'required': "SIM卡ID不能为空"
        }
    )

    iccid = forms.IntegerField(
        required=True,
        error_messages={
            'required': "设备IMSI号不能为空"
        }
    )


# 判断是否需要更新个人信息
class UpdateUserinfoForm(forms.Form):
    imsi = forms.IntegerField(
        required=True,
        error_messages={
            'required': "SIM卡ID不能为空"
        }
    )

    iccid = forms.IntegerField(
        required=True,
        error_messages={
            'required': "设备IMSI号不能为空"
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "昵称不能为空"
        }
    )

    xiaohongshu_id = forms.CharField(
        required=True,
        error_messages={
            'required': "id不能为空"
        }
    )

    home_url = forms.CharField(
        required=True,
        error_messages={
            'required': "主页地址不能为空"
        }
    )
