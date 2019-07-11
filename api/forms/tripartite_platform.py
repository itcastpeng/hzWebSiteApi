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
    authorization_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': '授权类型不能为空',
        }
    )


    def clean_authorization_type(self):
        authorization_type = self.data.get('authorization_type')
        appid = self.data.get('appid')

        if authorization_type in [1, '1', 2, '2']:
            if authorization_type in [1, '1']: # 公众号授权
                objs = models.CustomerOfficialNumber.objects.filter(appid=appid)

            else: # 小程序
                objs = models.ClientApplet.objects.filter(appid=appid)

            if not objs:
                if authorization_type in [1, '1']: # 公众号授权
                    models.CustomerOfficialNumber.objects.create(appid=appid)

                else:
                    models.ClientApplet.objects.create(appid=appid)

            return authorization_type
        else:
            self.add_error('authorization_type', '请输入正确的收取按类型')










