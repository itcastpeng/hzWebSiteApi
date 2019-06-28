from django import forms
from hurong import models

# 添加安装包
class AddForm(forms.Form):
    package_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "安装包类型不能为空"
        }
    )

    package_path = forms.CharField(
        required=True,
        error_messages={
            'required': "安装包下载地址不能为空"
        }
    )
    package_name = forms.CharField(
        required=True,
        error_messages={
            'required': "安装包名称不能为空"
        }
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
        }
    )
    def clean_package_type(self):
        package_type = self.data.get('package_type')
        data_list = [i[0] for i in models.InstallationPackage.package_type_choices]
        if int(package_type) in data_list:
            return package_type
        else:
            self.add_error('package_type', '请选择正确类型')

    def clean_package_name(self):
        package_name = self.data.get('package_name')
        objs = models.InstallationPackage.objects.filter(package_name=package_name).exclude(is_delete=1)
        if objs:
            self.add_error('package_name', '该安装包名称重复')
        else:
            return package_name

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


# 修改安装包
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "请选择要修改的安装包"
        }
    )

    package_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "安装包类型不能为空"
        }
    )

    package_path = forms.CharField(
        required=True,
        error_messages={
            'required': "安装包下载地址不能为空"
        }
    )
    package_name = forms.CharField(
        required=True,
        error_messages={
            'required': "安装包名称不能为空"
        }
    )
    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.InstallationPackage.objects.filter(id=o_id).exclude(is_delete=1)
        if objs:
            return o_id
        else:
            self.add_error('o_id', '您要修改的安装包不存在')


    def clean_package_type(self):
        package_type = self.data.get('package_type')
        data_list = [i[0] for i in models.InstallationPackage.package_type_choices]
        if int(package_type) in data_list:
            return package_type
        else:
            self.add_error('package_type', '请选择正确类型')

    def clean_package_name(self):
        package_name = self.data.get('package_name')
        objs = models.InstallationPackage.objects.filter(package_name=package_name)
        if objs:
            self.add_error('package_name', '该安装包名称重复')
        else:
            return package_name


# 删除安装包
class DeleteForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "请选择要修改的安装包"
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.InstallationPackage.objects.filter(id=o_id)
        if objs:
            objs.update(is_delete=1)
        else:
            self.add_error('o_id', '您要删除的安装包不存在')












