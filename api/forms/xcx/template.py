# developer: 张聪
# email: 18511123018@163.com

from django import forms

from api import models


# 判断是否是数字
class SelectForm(forms.Form):
    template_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "页码数据类型错误"
        }
    )

    # 查询名称是否存在
    def clean_template_id(self):
        template_id = self.data['template_id']

        objs = models.Template.objects.filter(
            id=template_id
        )
        if objs:
            return template_id
        else:
            self.add_error('template_id', '模板id异常')
