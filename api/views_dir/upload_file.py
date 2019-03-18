# from api import models
from publicFunc import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from api.forms import upload_form
import os
import re
import hashlib
import platform
import time
import random
import json
import base64
from PIL import Image, ImageFont, ImageDraw

sysstr = platform.system()


# 加密名字
def encryption():
    string = str(random.randint(10, 99)) + str(int(time.time())) + str(random.randint(10, 99))
    pwd = str(string)
    hash = hashlib.md5()
    hash.update(pwd.encode())
    return hash.hexdigest()


# 上传海报水印
def upload_poster_watermark(poster_path, video_name):
    logo_path = os.path.join('statics', 'img', 'tianyan_logo.png')
    image = Image.open(poster_path).convert('RGBA')

    # 绘图句柄
    image_draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('/usr/share/fonts/chinese/simsun.ttc', 15)  # 使用自定义的字体，第二个参数表示字符大小

    text_size_x, text_size_y = image_draw.textsize('微商天眼', font=font)
    image_draw.text((40, 20), '微商天眼', font=font, fill=(0, 0, 0))

    logo_img = Image.open(logo_path)  # logo
    logo_img = logo_img.resize((20, 20), Image.ANTIALIAS)
    image.paste(logo_img, (18, 18))
    path = os.path.join('statics', 'img', video_name)
    image.save(path)
    return path


# 获取名字后缀
def get_name_suffix(fileName):
    houzhui = re.search(r'[^.]+$', fileName).group(0)  # 获取点后面的后缀
    return houzhui


# 分片
@csrf_exempt
def upload_shard(request):
    response = Response.ResponseObj()
    if request.method == 'POST':
        print('request.POST------> ', request.FILES)

        forms_obj = upload_form.imgUploadForm(request.POST)
        if forms_obj.is_valid():
            img_data = request.FILES.get('img_data')  # 文件内容
            img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
            img_source = forms_obj.cleaned_data.get('img_source')  # 文件类型
            timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
            chunk = forms_obj.cleaned_data.get('chunk')  # 第几片文件
            expanded_name = get_name_suffix(img_name)  # 获取扩展名称
            if img_source == 'file':
                if expanded_name.lower().strip() not in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf']:
                    response.code = 301
                    response.msg = '请上传正确(文件)格式'
                    return JsonResponse(response.__dict__)

            elif img_source == 'img':
                if expanded_name.lower().strip() not in [
                    'bmp', 'dib', 'rle', 'emf', 'gif', 'jpg', 'jpeg', 'jpe', 'jif', 'pcx', 'dcx', 'pic', 'png',
                    'tga', 'tif', 'tiffxif', 'wmf', 'jfif', 'pdf'
                ]:
                    response.code = 301
                    response.msg = '请上传正确(图片)格式'
                    return JsonResponse(response.__dict__)

            # elif img_source == 'video':
            #     if expanded_name.lower().strip() not in ['rm', 'rmvb', '3gp','avi','mpeg','mpg','mkv','dat','asf',
            #             'wmv', 'flv', 'mov','mp4','ogg','ogm']:
            #         response.code = 301
            #         response.msg = '请上传正确视频格式'
            #         return JsonResponse(response.__dict__)

            else:
                response.code = 301
                response.msg = '请上传正确格式'
                return JsonResponse(response.__dict__)

            img_name = timestamp + "_" + str(chunk) + '.' + expanded_name
            img_save_path = os.path.join('statics', 'tmp', img_name)
            with open(img_save_path, "wb") as f:
                data = ''
                for chunk in img_data.chunks():
                    data += str(chunk)
                f.write(eval(data))
            if os.path.exists(img_save_path):
                response.code = 200
                response.msg = '上传成功'
            else:
                response.code = 301
                response.msg = '上传失败'
        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = '请求异常'
    return JsonResponse(response.__dict__)


# 合并
@csrf_exempt
def merge(request):
    response = Response.ResponseObj()
    if request.method == 'POST':
        forms_obj = upload_form.imgMergeForm(request.POST)
        if forms_obj.is_valid():

            img_source = forms_obj.cleaned_data.get('img_source')  # 文件类型
            img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
            timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
            chunk_num = forms_obj.cleaned_data.get('chunk_num')  # 一共多少份
            expanded_name = get_name_suffix(img_name)  # 获取扩展名称

            file_dir = ''
            file_type = '图片'

            if img_source == 'img':
                file_dir = os.path.join('statics', 'img')

            elif img_source == 'file':
                file_dir = os.path.join('statics', 'file')
                file_type = '文件'

            # elif img_source == 'video':
            #     file_dir = os.path.join('statics', 'video')
            #     file_type = '视频'

            else:
                response.code = 402
                response.msg = '合并异常'

            fileData = ''
            for chunk in range(chunk_num):
                file_name = timestamp + "_" + str(chunk) + '.' + expanded_name
                file_save_path = os.path.join('statics', 'tmp', file_name)
                if os.path.exists(file_save_path):
                    print('---file_save_path---file_save_path-----', file_save_path)
                    with open(file_save_path, 'rb') as f:
                        fileData += str(f.read())
                    # os.remove(file_save_path)  # 删除分片 文件

            video_name = encryption() + img_name
            path = os.path.join(file_dir, video_name)
            try:
                with open(path, 'ab')as f:
                    f.write(eval(fileData))  # 写入
            except Exception as e:
                print('e--> ', e)
            response.data = {'url': path}

            response.code = 200
            response.msg = "上传{}成功".format(file_type)

        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = '请求异常'
    return JsonResponse(response.__dict__)


# base分片
@csrf_exempt
def upload_base_shard(request):
    response = Response.ResponseObj()
    if request.method == 'POST':
        print('request.POST------> ', request.FILES)

        forms_obj = upload_form.imgUploadForm(request.POST)
        if forms_obj.is_valid():
            img_data = forms_obj.cleaned_data.get('img_data')  # 文件内容
            img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
            img_source = forms_obj.cleaned_data.get('img_source')  # 文件类型
            timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
            chunk = forms_obj.cleaned_data.get('chunk')  # 第几片文件
            expanded_name = get_name_suffix(img_name)  # 获取扩展名称
            if img_source == 'file':
                if expanded_name.lower().strip() not in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf']:
                    response.code = 301
                    response.msg = '请上传正确(文件)格式'
                    return JsonResponse(response.__dict__)

            elif img_source == 'img':
                extension_list = [
                    'bmp', 'dib', 'rle', 'emf', 'gif', 'jpg', 'jpeg', 'jpe', 'jif', 'pcx', 'dcx', 'pic', 'png',
                    'tga', 'tif', 'tiffxif', 'wmf', 'jfif', 'pdf'
                ]
                if expanded_name.lower().strip() not in extension_list:
                    response.code = 301
                    response.msg = '请上传正确(图片)格式'
                    return JsonResponse(response.__dict__)

            else:
                response.code = 301
                response.msg = '请上传正确格式'
                return JsonResponse(response.__dict__)
            print('img_data--------> ', img_data)
            img_name = timestamp + "_" + str(chunk) + '.' + expanded_name
            img_save_path = os.path.join('statics', 'tmp', img_name)
            with open(img_save_path, "w", encoding='utf8') as f:
                f.write(img_data)

            if os.path.exists(img_save_path):
                response.code = 200
                response.msg = '上传成功'
            else:
                response.code = 301
                response.msg = '上传失败'
        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = '请求异常'
    return JsonResponse(response.__dict__)


# base合并
@csrf_exempt
def base_merge(request):
    response = Response.ResponseObj()
    if request.method == 'POST':
        is_posters = request.GET.get('is_posters')  # 判断是否为海报  如果该参数有值 则打水印
        forms_obj = upload_form.imgMergeForm(request.POST)
        if forms_obj.is_valid():
            img_source = forms_obj.cleaned_data.get('img_source')  # 文件类型
            img_name = forms_obj.cleaned_data.get('img_name')  # 图片名称
            timestamp = forms_obj.cleaned_data.get('timestamp')  # 时间戳
            chunk_num = forms_obj.cleaned_data.get('chunk_num')  # 一共多少份
            expanded_name = get_name_suffix(img_name)  # 获取扩展名称

            file_type = '图片'
            if img_source == 'img':
                file_dir = os.path.join('statics', 'img')

            elif img_source == 'file':
                file_dir = os.path.join('statics', 'file')
                file_type = '文件'

            else:
                response.code = 402
                response.msg = '合并异常'
                return JsonResponse(response.__dict__)

            fileData = ''
            for chunk in range(chunk_num):
                file_name = timestamp + "_" + str(chunk) + '.' + expanded_name
                file_save_path = os.path.join('statics', 'tmp', file_name)
                if os.path.exists(file_save_path):
                    with open(file_save_path, 'r') as f:
                        fileData += f.read()
                    os.remove(file_save_path)  # 删除分片 文件

            video_name = encryption() + img_name
            path = os.path.join(file_dir, video_name)
            try:
                with open(path, 'ab')as f:
                    f.write(base64.b64decode(fileData))  # 写入
            except Exception as e:
                print('e--> ', e)
            print('is_posters------> ', is_posters)
            if is_posters:  # 海报打水印
                path_name = encryption() + '.png'
                print('video_name------> ', video_name)
                path = upload_poster_watermark(path, path_name)

                os.remove(os.path.join(file_dir, video_name))  # 删除原始上传图片

            response.data = {'url': path}
            print('path-> ', path)
            response.code = 200
            response.msg = "上传{}成功".format(file_type)

        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = '请求异常'
    return JsonResponse(response.__dict__)
