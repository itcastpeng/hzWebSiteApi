from django import forms
from hurong import models

def permissions_init_data(pid, data_list, o_id):
    objs = models.Permissions.objects.filter(id=pid)
    for obj in objs:
        data_list.append(obj.id)
        print('data_list--> ', data_list)
        if o_id and int(o_id) == int(obj.id):
            return data_list

        permissions_init_data(obj.pid_id, data_list, o_id)
    return data_list

# 添加
class AddForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': "权限名称不能为空"
        }
    )
    title = forms.CharField(
        required=True,
        error_messages={
            'required': "权限标题不能为空"
        }
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        }
    )
    pid_id = forms.CharField(
        required=False
    )

    def clean_name(self):
        name = self.data.get('name')
        objs = models.Permissions.objects.filter(name=name)
        if objs:
            self.add_error('name', '权限名称存在')
        else:
            return name
    def clean_title(self):
        title = self.data.get('title')
        objs = models.Permissions.objects.filter(title=title)
        if objs:
            self.add_error('title', '该路径存在')
        else:
            return title

    def clean_pid_id(self):
        pid_id = self.data.get('pid_id')
        if pid_id:
            objs = models.Permissions.objects.filter(id=pid_id)
            if objs:
                return pid_id
            else:
                self.add_error('pid_id', '该父级ID不存在')


# 更新
class UpdateForm(forms.Form):
    name = forms.CharField(
        required=True,
        error_messages={
            'required': '权限名称不能为空'
        }
    )
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '公司id不能为空'
        }
    )
    title = forms.CharField(
        required=True,
        error_messages={
            'required': "权限标题不能为空"
        }
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "权限标题不能为空"
        }
    )
    pid_id = forms.CharField(
        required=False
    )

    def clean_pid_id(self):
        pid_id = self.data.get('pid_id')
        if pid_id:
            objs = models.Permissions.objects.filter(id=pid_id)
            if objs:
                return pid_id
            else:
                self.add_error('pid_id', '该父级ID不存在')

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        obj = models.Permissions.objects.filter(
            id=o_id
        )
        if not obj:
            self.add_error('o_id', '该权限不存在')
        else:
            pid_id = self.data.get('pid_id')
            if pid_id:
                print('o_id, pid_id---------------> ', o_id, pid_id)
                if int(o_id) == int(pid_id):
                    self.add_error('pid_id', '父级权限不能为自己')

                # 判断添加该父级是否能死循环
                print('pid_id---> ',pid_id)
                data_list = []
                result_data = permissions_init_data(pid_id, data_list, o_id)
                print('result_data--> ', result_data)
                print('o_id--> ', o_id)
                if int(o_id) in result_data:
                    self.add_error('pid_id', '不能循环权限')
            return o_id


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