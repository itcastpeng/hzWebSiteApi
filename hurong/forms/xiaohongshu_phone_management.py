from django import forms
from hurong import models
from publicFunc.public import verify_phone_number

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

# 获取未使用的手机号
class get_phone_number(forms.Form):
    iccid= forms.CharField(
        required=True,
        error_messages={
            'required': "SIM卡ID 不能为空"
        }
    )
    imsi= forms.CharField(
        required=True,
        error_messages={
            'required': "设备IMSI号 不能为空"
        }
    )

# 获取验证码
class get_verification_code(forms.Form):
    phone_number = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
        }
    )
    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        if verify_phone_number(phone_number):
            return phone_number
        else:
            self.add_error('phone_number', '手机号错误')


# 获取小红书未注册的账号信息
class get_xhs_unregistered_information(forms.Form):
    get_info_number = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
        }
    )
