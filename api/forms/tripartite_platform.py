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
    authorization_way = forms.IntegerField(
        required=True,
        error_messages={
            'required': '授权方式不能为空',
        }
    )

    def clean_authorization_type(self):
        authorization_type = self.data.get('authorization_type')
        user_id = self.data.get('user_id')
        appid = self.data.get('appid')

        if authorization_type in [1, '1', 2, '2']:
            if authorization_type in [1, '1']: # 公众号授权
                objs = models.CustomerOfficialNumber.objects.filter(appid=appid)
                app_type = '公众号'

            else: # 小程序
                app_type = '小程序'
                objs = models.ClientApplet.objects.filter(appid=appid)

            if not objs:
                if authorization_type in [1, '1']: # 公众号授权
                    models.CustomerOfficialNumber.objects.create(appid=appid, user_id=user_id)

                else:   # 小程序授权
                    models.ClientApplet.objects.create(appid=appid, user_id=user_id)
            else:
                self.add_error('authorization_type', '该{}已经授权'.format(app_type))
            return authorization_type
        else:
            self.add_error('authorization_type', '请输入正确的授权类型')

    def clean_authorization_way(self):
        authorization_way = self.data.get('authorization_way')
        if authorization_way in [1, '1', 2, '2']:
            return authorization_way
        else:
            self.add_error('authorization_way', '授权方式异常')


# 发布代码
class UploadAppletCode(forms.Form):
    code_template_id = forms.CharField(
        required=True,
        error_messages={
            'required': '代码模板ID不能为空',
        }
    )

    user_version = forms.CharField(
        required=True,
        error_messages={
            'required': '代码版本号不能为空',
        }
    )

    user_desc = forms.CharField(
        required=True,
        error_messages={
            'required': '代码描述不能为空',
        }
    )


