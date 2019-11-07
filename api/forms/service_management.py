from django import forms
from api import models
import json






# 添加
class AddForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "名称不能为空"
        }
    )
    create_user_id = forms.CharField(
        required=False,
    )
    abstract = forms.CharField(
        required=False,
    )
    main_figure = forms.CharField(
        required=False,
    )
    service_classification = forms.CharField(
        required=False,
    )
    price_type = forms.CharField(
        required=False,
    )
    price = forms.CharField(
        required=False,
    )
    promotion_price = forms.CharField(
        required=False,
    )
    limit_amount = forms.CharField(
        required=False,
    )
    virtual_order_volume = forms.CharField(
        required=False,
    )
    service_detail = forms.CharField(
        required=False,
    )
    def clean_name(self):
        name = self.data.get('name')
        create_user_id = self.data.get('create_user_id')
        objs = models.ServiceTable.objects.filter(name=name, create_user_id=create_user_id)
        if objs:
            self.add_error('name', '该名片名称已存在')
        else:
            return name

    def clean_main_figure(self):
        main_figure = self.data.get('main_figure')
        return json.dumps(main_figure)

# 更新
class UpdateForm(forms.Form):
    o_id = forms.CharField(
        required=True,
        error_messages={
            'required': "请选择要修改的名片"
        }
    )
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "名称不能为空"
        }
    )
    create_user_id = forms.CharField(
        required=False,
    )
    abstract = forms.CharField(
        required=False,
    )
    main_figure = forms.CharField(
        required=False,
    )
    service_classification = forms.CharField(
        required=False,
    )
    price_type = forms.CharField(
        required=False,
    )
    price = forms.CharField(
        required=False,
    )
    promotion_price = forms.CharField(
        required=False,
    )
    limit_amount = forms.CharField(
        required=False,
    )
    virtual_order_volume = forms.CharField(
        required=False,
    )
    service_detail = forms.CharField(
        required=False,
    )
    def clean_o_id(self):
        o_id = self.data.get('o_id')
        create_user_id = self.data.get('create_user_id')
        objs = models.ServiceTable.objects.filter(id=o_id)
        if not objs:
            self.add_error('o_id', '服务不存在')
        else:
            if int(objs[0].create_user_id) == int(create_user_id):
                return o_id
            else:
                self.add_error('o_id', '无权限操作')

    def clean_name(self):
        name = self.data.get('name')
        create_user_id = self.data.get('create_user_id')
        objs = models.BusinessCard.objects.filter(name=name, create_user_id=create_user_id)
        if objs:
            self.add_error('name', '该名片名称已存在')
        else:
            return name


    def clean_main_figure(self):
        main_figure = self.data.get('main_figure')
        return json.dumps(main_figure)



# 判断是否是数字
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页显示数量类型错误"
        }
    )

    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
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