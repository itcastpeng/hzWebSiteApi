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
        required=False,
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

    def clean_user_id(self):
        user_id = self.data.get('user_id')
        applet_num = models.ClientApplet.objects.filter(user_id=user_id).count() + 1
        obj = models.UserProfile.objects.get(id=user_id)
        if int(obj.small_program_number) >= applet_num:
            return user_id
        self.add_error('user_id', '小程序绑定达到上限')

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
                # if authorization_type in [1, '1']: # 公众号授权
                #     models.CustomerOfficialNumber.objects.create(appid=appid, user_id=user_id)
                #
                # else:   # 小程序授权
                #     models.ClientApplet.objects.create(appid=appid, user_id=user_id)
                return authorization_type
            else:
                self.add_error('authorization_type', '该{}已经授权'.format(app_type))
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

    user_desc = forms.CharField(
        required=False,
        error_messages={
            'required': '代码描述不能为空',
        }
    )


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