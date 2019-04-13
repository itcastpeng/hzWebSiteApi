from django import forms

from api import models
import json


# 添加
class AddForm(forms.Form):
    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '创建人不能为空',
            'invalid': "参数数据类型错误"
        }
    )

    img_url = forms.CharField(
        required=True,
        error_messages={
            'required': "图片地址不能为空"
        }
    )

    group_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '分组id不能为空',
            'invalid': "参数数据类型错误"
        }
    )


# 更新
class UpdateForm(forms.Form):
    update_id_list = forms.CharField(
        required=True,
        error_messages={
            'required': "修改id不能为空"
        }
    )

    group_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '分组id不能为空',
            'invalid': "参数数据类型错误"
        }
    )

    def clean_group_id(self):
        group_id = self.data.get('group_id')
        create_user_id = self.data.get('create_user_id')
        objs = models.PhotoLibraryGroup.objects.filter(create_user_id=create_user_id, id=group_id)
        if objs:
            return group_id
        else:
            self.add_error('update_id_list', "分组id不存在")

    def clean_update_id_list(self):
        update_id_list = self.data.get('update_id_list')
        update_id_list = json.loads(update_id_list)
        if isinstance(update_id_list, list):
            return list(update_id_list)
        else:
            self.add_error('update_id_list', "修改id类型错误")


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

    create_user_id = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "用户id类型错误"
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


class DeleteForm(forms.Form):
    delete_id_list = forms.CharField(
        required=True,
        error_messages={
            'required': "删除id不能为空"
        }
    )

    def clean_delete_id_list(self):
        delete_id_list = self.data.get('delete_id_list')
        delete_id_list = json.loads(delete_id_list)
        if isinstance(delete_id_list, list):
            return list(delete_id_list)
        else:
            self.add_error('delete_id_list', "删除id类型错误")
