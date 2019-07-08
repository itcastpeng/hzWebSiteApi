from django import forms
from hurong import models
from publicFunc.public import verify_phone_number

# 获取手机工作状态
class GetPhoneWorkStatus(forms.Form):
    iccid = forms.CharField(
        required=False,
        error_messages={
            'required': "SIM卡ID类型错误"
        }
    )
    imsi = forms.CharField(
        required=False,
        error_messages={
            'required': "设备IMSI号类型错误"
        }
    )
    phone_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "手机工作类型不能为空"
        }
    )

    macaddr = forms.CharField(
        required=False,
        error_messages={
            'required': "手机MAC地址类型错误"
        }
    )

    def clean_phone_type(self):
        phone_type = int(self.data.get('phone_type'))
        macaddr = self.data.get('macaddr')
        imsi = self.data.get('imsi')
        iccid = self.data.get('iccid')

        if phone_type == 1: # 查覆盖
            if not macaddr:
                self.add_error('macaddr', 'MAC地址不能为空')
            else:
                return phone_type
        else:
            if iccid and imsi:
                return phone_type
            else:
                if not iccid:
                    self.add_error('iccid', 'SIM卡ID不能为空')
                else:
                    self.add_error('imsi', '设备IMSI号不能为空')



# 获取未使用的手机号
class GetPhoneNumber(forms.Form):
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
    # macaddr = forms.CharField(
    #     required=False,
    #     error_messages={
    #         'required': "SIM卡ID 不能为空"
    #     }
    # )
    #
    # def clean_macaddr(self):
    #     macaddr = self.data.get('macaddr')
    #     imsi = self.data.get('imsi')
    #     iccid = self.data.get('iccid')
    #
    #     if macaddr:
    #         return macaddr
    #     else:
    #         if not iccid or not imsi:
    #             self.add_error('imsi', '设备IMSI号或SIM卡ID不能为空')
    #         else:
    #             return macaddr


# 获取验证码
class GetVerificationCode(forms.Form):
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
class GetXhsUnregisteredInformation(forms.Form):
    get_info_number = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
        }
    )


# 修改 移动设备
class UpdateMobileDevices(forms.Form):

    phone_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "请选择修改的设备"
        }
    )
    device_name = forms.CharField(
        required=False,
        error_messages={
            'required': "设备名称类型错误"
        }
    )
    is_debug = forms.BooleanField(
        required=True,
        error_messages={
            'required': "是否调试请选择"
        }
    )
    def clean_phone_id(self):
        phone_id = self.data.get('phone_id')
        objs = models.XiaohongshuPhone.objects.filter(id=phone_id)
        if objs:
            return phone_id
        else:
            self.add_error('phone_id', '修改设备不存在')

