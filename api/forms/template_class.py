from django import forms

from api import models


# 添加
class AddForm(forms.Form):
    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '创建人不能为空',
            'invalid': "参数数据类型错误"
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "模板名称不能为空"
        }
    )

    class_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "模板名称不能为空"
        }
    )

    # 查询名称是否存在
    def clean_name(self):
        name = self.data['name']
        # create_user_id = self.data['create_user_id']

        objs = models.TemplateClass.objects.filter(
            name=name,
            # create_user_id=create_user_id
        )
        if objs:
            self.add_error('name', '模板分类名称已存在')
        else:
            return name


# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '模板id不能为空',
            'invalid': "参数数据类型错误"
        }
    )

    name = forms.CharField(
        required=False,
        error_messages={
            # 'required': "模板不能为空"
        }
    )

    # 判断名称是否存在
    def clean_name(self):
        o_id = self.data['o_id']
        name = self.data['name']
        # create_user_id = self.data['create_user_id']
        objs = models.TemplateClass.objects.filter(
            name=name,
            # create_user_id=create_user_id
        ).exclude(
            id=o_id
        )
        if objs:
            self.add_error('username', '模板分类名称已存在')
        else:
            return name


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


# 更新
class GetTabBarDataForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '模板id不能为空',
            'invalid': "参数数据类型错误"
        }
    )
