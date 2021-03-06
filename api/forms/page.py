from django import forms


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
            'required': "页面名称不能为空"
        }
    )

    page_group_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '分组id不能为空',
            'invalid': "参数数据类型错误"
        }
    )


# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '页面id不能为空',
            'invalid': "参数数据类型错误"
        }
    )

    name = forms.CharField(
        required=False,
        error_messages={
            # 'required': "页面名称不能为空"
        }
    )

    data = forms.CharField(
        required=False,
        error_messages={
            # 'required': "页面数据不能为空"
        }
    )

    page_group_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': '页面id不能为空',
            'invalid': "参数数据类型错误"
        }
    )


# 复制页面
class CopyForm(forms.Form):
    page_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '页面id不能为空',
            'invalid': "参数数据类型错误"
        }
    )

# # 判断是否是数字
# class SelectForm(forms.Form):
#     current_page = forms.IntegerField(
#         required=False,
#         error_messages={
#             'invalid': "参数类型错误"
#         }
#     )
#
#     length = forms.IntegerField(
#         required=False,
#         error_messages={
#             'invalid': "参数类型错误"
#         }
#     )
#
#     page_id = forms.IntegerField(
#         required=True,
#         error_messages={
#             'required': '页面id不能为空',
#             'invalid': "参数类型错误"
#         }
#     )
#
#     def clean_current_page(self):
#         if 'current_page' not in self.data:
#             current_page = 1
#         else:
#             current_page = int(self.data['current_page'])
#         return current_page
#
#     def clean_length(self):
#         if 'length' not in self.data:
#             length = 10
#         else:
#             length = int(self.data['length'])
#         return length
