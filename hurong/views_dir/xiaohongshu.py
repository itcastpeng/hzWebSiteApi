from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from publicFunc.send_email import SendEmail
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.xiaohongshu import CheckForbiddenTextForm
from django.db.models import Q
import redis
import json
import requests


# 请求三方接口判断是否有禁词
def request_post(context):
    url = "https://avatar-api.wuhan716.com/v1/word-detection/prohibitedWord/executeWord"
    data = {
        "context": context
    }
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://servicewechat.com/wx8a85fe9a89ef75c3/15/page-frame.html",
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; MI 8 Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.91 Mobile Safari/537.36 MicroMessenger/7.0.4.1420(0x27000437) Process/appbrand0 NetType/WIFI Language/zh_CN",
        "charset": "utf-8",
        "Accept-Encoding": "gzip",
        "Accept": "application/json",
    }
    result = requests.post(url, data=json.dumps(data), headers=headers)
    return result.json()


@account.is_token(models.UserProfile)
def check_forbidden_text(request):
    response = Response.ResponseObj()
    if request.method == "POST":
        forms_obj = CheckForbiddenTextForm(request.POST)
        if forms_obj.is_valid():
            result = request_post(forms_obj.cleaned_data.get("context"))
            if result['code'] == 0:
                response.data = result['data']
                response.code = 200
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# if __name__ == '__main__':
#     context = """
#     孕吐严重试试这款蜂蜜糖!没想到!怀个孕能这么难受!天天吐,不吃吐,吃也吐!机缘巧合,我在朋友圈发现了一样好东西!麦卢卡蜂蜜糖!这个蜂蜜糖对孕妇hin友好,它含有天然寡糖,不是蔗糖,也不会囤积脂肪,作为孕期健康小零食不错!那个蜂蜜糖的牌子是AUSTRALIAN BY NATURE,澳洲本土品牌,代·购说它家的蜂场在奥克兰周边的原始森林,是世界上优·质的麦卢卡蜂源地。
#     """
#     request_post(context)