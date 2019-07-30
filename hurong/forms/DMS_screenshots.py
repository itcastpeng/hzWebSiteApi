from django import forms
from hurong import models
from publicFunc import account
import re, json, base64

# 上传截图
class Screenshots(forms.Form):
    img_base64_data = forms.CharField(
        required=True,
        error_messages={
            'required': "BASE64 编码数据不能为空",
        }
    )
    iccid = forms.CharField(
        required=True,
        error_messages={
            'required': "ICCID不能为空",
        }
    )
    imsi = forms.CharField(
        required=True,
        error_messages={
            'required': "IMSI不能为空",
        }
    )

    def clean_img_base64_data(self):
        img_base64_data = self.data.get('img_base64_data')

        img_base64_data = img_base64_data.replace(' ', '+')
        imgdata = ''
        try:
            imgdata = base64.b64decode(img_base64_data)
            return imgdata
        except Exception :
            self.add_error('img_base64_data', 'BASE64数据异常')

    def clean_iccid(self):
        imsi = self.data.get('imsi')
        iccid = self.data.get('iccid')

        objs = models.XiaohongshuPhone.objects.filter(
            imsi=imsi,
            iccid=iccid
        )
        if objs:
            return imsi
        else:
            self.add_error('imsi', '设备异常')












