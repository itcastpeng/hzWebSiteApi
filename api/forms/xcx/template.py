# developer: 张聪
# email: 18511123018@163.com

from django import forms

from api import models


# 获取底部导航数据
class GetTabbarDataForm(forms.Form):
    template_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "模板id不能为空",
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


# 获取页面数据
class GetPageDataForm(forms.Form):
    page_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "页面id不能为空",
            'invalid': "页码数据类型错误"
        }
    )

    # 查询名称是否存在
    def clean_page_id(self):
        page_id = self.data['page_id']

        objs = models.Page.objects.filter(
            id=page_id
        )
        if objs:
            return page_id
        else:
            self.add_error('page_id', '页面id异常')
