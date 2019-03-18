from django import forms

from api import models
# from publicFunc import account
import datetime


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
            'required': "页显示数量类型错误"
        }
    )

    def clean_user_id(self):
        user_id = self.data.get('user_id')
        objs = models.Userprofile.objects.filter(id=user_id)
        if objs and objs[0].overdue_date:
            now_date = datetime.date.today()
            if objs[0].overdue_date >= now_date:
                return user_id
            else:
                self.add_error('user_id', '您的会员已经到期, 为了避免您的正常使用, 请续费继续使用')
        else:
            if not objs:
                self.add_error('user_id', '非法用户')
            else:
                self.add_error('user_id', '您的会员已经到期, 为了避免您的正常使用, 请续费继续使用')

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


# 添加客户备注
class AddForm(forms.Form):
    remote_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "备注类型不能为空"
        }
    )

    remote = forms.CharField(
        required=True,
        error_messages={
            'required': "备注不能为空"
        }
    )

    title = forms.CharField(
        required=False,
        error_messages={
            'required': "标题类型错误"
        }
    )

    create_date = forms.CharField(
        required=False,
        error_messages={
            'required': "创建时间类型错误"
        }
    )
    customer_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户不能为空"
        }
    )
    def clean_remote_type(self):
        remote_type = int(self.data.get('remote_type'))
        title = self.data.get('title')
        create_date = self.data.get('create_date')

        if remote_type in [2, 3]:
            if not title:
                self.add_error('remote_type', '请备注产品名称')
        if remote_type == 2:
            if not create_date:
                self.add_error('remote_type', '请填写产品购买时间')

        return remote_type


# 修改客户备注
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户不能为空"
        }
    )

    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
        }
    )

    remote = forms.CharField(
        required=True,
        error_messages={
            'required': "备注不能为空"
        }
    )

    title = forms.CharField(
        required=False,
        error_messages={
            'required': "标题类型错误"
        }
    )

    create_date = forms.CharField(
        required=False,
        error_messages={
            'required': "创建时间类型错误"
        }
    )
    customer_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户不能为空"
        }
    )
    def clean_o_id(self):
        o_id = self.data.get('o_id')
        user_id = int(self.data.get('user_id'))

        objs = models.customer_information_the_user.objects.filter(id=o_id)
        if objs:
            if objs[0].user_id == user_id:
                remote_type = int(objs[0].remote_type)
                title = self.data.get('title')
                create_date = self.data.get('create_date')

                if remote_type in [2, 3]:
                    if not title:
                        self.add_error('o_id', '请备注产品名称')
                if remote_type == 2:
                    if not create_date:
                        self.add_error('o_id', '请填写产品购买时间')

                return o_id, remote_type
            else:
                self.add_error('o_id', '暂无权限')
        else:
            self.add_error('o_id', '数据异常')


class Form(forms.Form):
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
