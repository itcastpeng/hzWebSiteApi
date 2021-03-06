from django import forms
from hurong import models
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
    phone_num = forms.IntegerField(
        required=True,
        error_messages={
            'required': "手机号不能为空"
        }
    )
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
    macaddr = forms.CharField(
        required=False,
        error_messages={
            'required': "mac地址类型错误"
        }
    )
    platform = forms.IntegerField(
        required=False,
        error_messages={
            'required': "平台类型错误"
        }
    )

    def clean_name(self):
        name = self.data.get('name')
        name = name.strip()
        return name

    def clean_xiaohongshu_id(self):
        xiaohongshu_id = self.data.get('xiaohongshu_id')
        count = models.XiaohongshuUserProfile.objects.filter(xiaohongshu_id=xiaohongshu_id).count()
        if count > 0:
            self.add_error('xiaohongshu_id', '小红书id已经存在')
        else:
            return xiaohongshu_id

class RegistreForm(forms.Form):
    uid = forms.IntegerField(
        required=True,
        error_messages={
            'required': "小红书博主表id不能为空",
            'invalid': "类型错误"
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "小红书博主昵称不能为空",
        }
    )

    # head_portrait = forms.URLField( #
    head_portrait = forms.CharField(
        required=True,
        error_messages={
            'required': "小红书博主头像不能为空",
            'invalid': "类型错误"
        }
    )

    gender = forms.IntegerField(
        required=True,
        error_messages={
            'required': "小红书博主性别不能为空",
            'invalid': "类型错误"
        }
    )

    birthday = forms.DateField(
        required=True,
        error_messages={
            'required': "小红书博主生日不能为空",
            'invalid': "类型错误"
        }
    )
    remark = forms.CharField(
        required=False,
        error_messages={
            'invalid': "类型错误"
        }
    )
    platform = forms.IntegerField(
        required=False,
        error_messages={
            'required': "平台类型错误"
        }
    )

# 判断今天是否更新阅读量
class IsTodayUpdateReading(forms.Form):
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

    def clean_imsi(self):
        imsi = self.data.get('imsi')
        iccid = self.data.get('iccid')

        objs = models.XiaohongshuPhone.objects.filter(imsi=imsi, iccid=iccid)
        if objs:
            obj = objs[0]
            user_objs = obj.xiaohongshuuserprofile_set.all()
            if user_objs:
                return user_objs[0].id

            else:
                self.add_error('imsi', '未绑定用户')
        else:
            self.add_error('imsi', '设备不存在')













