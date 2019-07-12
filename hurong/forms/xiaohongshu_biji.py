from django import forms

from hurong import models
from publicFunc import account
import re
import json


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


# 添加
class AddForm(forms.Form):
    xiaohongshu_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "小红书id不能为空",
            'invalid': "数据类型错误"
        }
    )

    content = forms.CharField(
        required=True,
        error_messages={
            'required': "笔记内容不能为空"
        }
    )

    release_time = forms.DateTimeField(
        required=True,
        error_messages={
            'required': "发布时间不能为空",
            'invalid': "发布时间格式错误"
        }
    )

    def clean_user_id(self):
        user_id = self.data['user_id']

        objs = models.XiaohongshuUserProfile.objects.filter(id=user_id)
        if objs:
            return user_id
        else:
            self.add_error('user_id', "小红书账户不存在")


# 获取发布任务
class GetReleaseTaskForm(forms.Form):
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


# 提交反链
class UploadUrlForm(forms.Form):
    task_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "任务id不能为空",
            'invalid': "数据类型错误"
        }
    )

    url = forms.URLField(
        required=True,
        error_messages={
            'required': "反链不能为空",
            'invalid': "数据类型错误"
        }
    )


# 更改阅读量
class UpdateReding(forms.Form):
    reading_num = forms.IntegerField(
        required=True,
        error_messages={
            'required': "阅读量不能为空",
        }
    )
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "笔记ID不能为空",
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.XiaohongshuBiji.objects.filter(id=o_id)
        if objs:
            return o_id
        else:
            self.add_error('o_id', '笔记不存在')











