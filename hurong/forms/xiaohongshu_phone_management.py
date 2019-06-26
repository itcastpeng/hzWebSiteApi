from django import forms
from hurong import models


# 获取手机工作状态
class get_phone_work_status(forms.Form):

    phone_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "手机工作类型不能为空"
        }
    )

    macaddr = forms.CharField(
        required=True,
        error_messages={
            'required': "手机MAC地址不能为空"
        }
    )

    def clean_macaddr(self):
        macaddr = self.data.get('macaddr')
        if models.XiaohongshuPhone.objects.filter(macaddr=macaddr):
            return macaddr
        else:
            self.add_error('macaddr', 'mac地址错误')

