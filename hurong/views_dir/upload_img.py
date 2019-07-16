# developer: 张聪
# email: 18511123018@163.com


from django.shortcuts import render
from publicFunc import Response
from django.http import JsonResponse
import time
import os


def upload_img(request):
    response = Response.ResponseObj()
    if request.method == "POST":

        img = request.FILES.get('file')  # 所有提交的文件
        # print("request.FILES -->", request.FILES)
        # print("request.POST -->", request.POST)
        # print("request.GET -->", request.GET)

        print('img -->', img)

        timestamp = str(int(time.time() * 1000))  # 时间戳
        extension_name = img.name.split('.')[-1]
        img_abs_name = os.path.join("statics", "imgs", timestamp) + "." + extension_name

        # print("img_abs_name -->", img_abs_name)
        with open(img_abs_name, "wb") as f:
            for chunk in img.chunks():
                f.write(chunk)

        response.code = 200
        response.data = {
            "img_url": '/' + img_abs_name
        }

    return JsonResponse(response.__dict__)
