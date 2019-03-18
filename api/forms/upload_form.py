from django import forms


# 分片上传验证
class imgUploadForm(forms.Form):
    img_name = forms.CharField(
        error_messages={
            'required': "图片名不能为空"
        }
    )
    timestamp = forms.CharField(
        error_messages={
            'required': "时间戳不能为空"
        }
    )
    img_data = forms.CharField(
        error_messages={
            'required': "内容不能为空"
        }
    )
    chunk = forms.IntegerField(
        error_messages={
            'required': "当前是第几份文件不能为空",
            'invalid': '份数必须是整数类型'
        }
    )

    img_source = forms.CharField(
        error_messages={
            'required': "文件类型不能为空",
            'invalid': "必须是字符串"
        }
    )


# 合并图片 Form 验证
class imgMergeForm(forms.Form):
    img_name = forms.CharField(
        error_messages={
            'required': "文件名不能为空"
        }
    )
    timestamp = forms.CharField(
        error_messages={
            'required': "时间戳不能为空"
        }
    )

    chunk_num = forms.IntegerField(
        error_messages={
            'required': "总份数不能为空",
            'invalid': '总份数必须是整数类型'
        }
    )
    img_source = forms.CharField(
        error_messages={
            'required': "文件类型不能为空",
            'invalid': "必须是字符串"
        }
    )
