from django import forms

from hurong import models
from publicFunc import account
import re
import json


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


# 禁词检测
class CheckForbiddenTextForm(forms.Form):
    context = forms.CharField(
        required=True,
        error_messages={
            'required': "检测文本不能为空",
        }
    )


# 添加
class AddForm(forms.Form):
    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "创建人不能为空",
            'invalid': "数据类型错误"
        }
    )

    keywords_list = forms.CharField(
        required=False,
        error_messages={
            'required': "下拉词列表不能为空"
        }
    )

    def clean_keywords_list(self):
        keywords_list = self.data['keywords_list']
        keywords_list = keywords_list.split()
        print('keywords_list -->', keywords_list)
        if isinstance(keywords_list, list):
            return list(keywords_list)
        else:
            self.add_error('keywords_list', "下拉词类型错误")


# 修改用户
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "修改id不能为空",
            'invalid': "数据类型错误"
        }
    )
    password = forms.CharField(
        required=False,
        error_messages={
            'required': "密码不能为空",
            'invalid': "数据类型错误"
        }
    )

    status = forms.IntegerField(
        required=True,
        error_messages={
            'required': "状态不能为空",
            'invalid': "数据类型错误"
        }
    )

    def clean_password(self):
        password = self.data['password']

        # 如果密码为空，则表示不修改密码
        if not password:
            return False

        return account.str_encrypt(password)


# 测试
class TestForm(forms.Form):
    send_email_title = forms.CharField(
        required=True,
        error_messages={
            'required': "邮件标题不能为空",
            'invalid': "数据类型错误"
        }
    )
    send_email_content = forms.CharField(
        required=True,
        error_messages={
            'required': "邮件内容不能为空",
            'invalid': "数据类型错误"
        }
    )
    send_email_list = forms.CharField(
        required=True,
        error_messages={
            'required': "收件人列表不能为空",
            'invalid': "数据类型错误"
        }
    )

    def clean_send_email_list(self):
        send_email_list = self.data['send_email_list'].split()
        for send_email in send_email_list:
            send_email = send_email.strip()
            if not re.match(r'\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}', send_email):
                self.add_error('send_email_list', '存在异常邮箱：{}'.format(send_email))
        return list(set(send_email_list))


# 删除
class DeleteForm(forms.Form):
    delete_id_list = forms.CharField(
        required=True,
        error_messages={
            'required': "删除列表不能为空"
        }
    )

    def clean_delete_id_list(self):
        delete_id_list = self.data['delete_id_list']
        delete_id_list = delete_id_list.strip().split(",")
        print('delete_id_list -->', delete_id_list)
        if isinstance(delete_id_list, list):
            return list(delete_id_list)
        else:
            self.add_error('delete_id_list', "删除列表类型错误")




# 本地禁词检测
class ForbiddenWordsQuery(forms.Form):
    forbidden_words = forms.CharField(
        required=True,
        error_messages={
            'required': "禁词不能为空"
        }
    )

    def clean_forbidden_words(self):
        forbidden_words = self.data.get('forbidden_words')
        forbidden_word = forbidden_words
        objs = models.XiaohongshuForbiddenText.objects.filter(create_datetime__isnull=False)
        data = []
        for obj in objs:
            if obj.word in forbidden_words:
                word = '{%s}' % obj.word
                forbidden_words = forbidden_words.replace(obj.word, word)
                data.append(obj.word)

        print('forbidden_words------->', forbidden_words)

        return data, forbidden_word













