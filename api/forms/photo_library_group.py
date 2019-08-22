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
            'required': "分组名称不能为空"
        }
    )

    parent_id = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "参数数据类型错误"
        }
    )
    template_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "模板ID不能为空"
        }
    )


# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '分组id不能为空',
            'invalid': "参数数据类型错误"
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "分组名称不能为空"
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

    get_type = forms.CharField(
        required=True,
        error_messages={
            'required': "数据类型不能为空",
            'invalid': "分组类型错误"
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

    def clean_get_type(self):
        get_type = self.data.get('get_type')
        if get_type not in ["system", "is_me"]:
            self.add_error('name', '分组类型异常')
        else:
            return get_type
