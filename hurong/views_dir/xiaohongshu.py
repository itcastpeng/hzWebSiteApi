from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from publicFunc.send_email import SendEmail
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.xiaohongshu import CheckForbiddenTextForm, SelectForm, AddForm
from django.db.models import Q, F, Sum, Count
from publicFunc.redisOper import get_redis_obj
import json, redis, requests, datetime


@account.is_token(models.UserProfile)
def xiaohongshu(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'keywords': '__contains',
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            # print('q -->', q)
            objs = models.XiaohongshuXiaLaKeywords.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'keywords': obj.keywords,
                    'status': obj.get_status_display(),
                    'status_id': obj.status,
                    'biji_num': obj.biji_num,
                    'xialaci_num': obj.xialaci_num,
                    'create_user__username': obj.create_user.username,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            response.note = {
                'id': "下拉词id",
                'keywords': "搜索词",
                'status': "状态名称",
                'status_id': "状态值",
                'biji_num': "笔记数",
                'xialaci_num': "下拉词数",
                'send_email_content': "发送邮件内容",
                'create_user__username': "创建人",
                'create_datetime': "创建时间",

            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.UserProfile)
def xiaohongshu_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    # print('request.POST -->', request.POST)
    if request.method == "POST":
        # 添加用户
        if oper_type == "add":
            form_data = {
                'create_user_id': request.GET.get('user_id'),
                'keywords_list': request.POST.get('keywords_list')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                keywords_list = forms_obj.cleaned_data.get('keywords_list')
                create_user_id = forms_obj.cleaned_data.get('create_user_id')

                query = []
                for keywords in keywords_list:
                    query.append(
                        models.XiaohongshuXiaLaKeywords(create_user_id=create_user_id, keywords=keywords)
                    )
                    if len(query) > 500:
                        models.XiaohongshuXiaLaKeywords.objects.bulk_create(query)
                        query = []
                if len(query) > 0:
                    models.XiaohongshuXiaLaKeywords.objects.bulk_create(query)

                response.code = 200
                response.msg = "添加成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            task_list_objs = models.XiaohongshuXiaLaKeywords.objects.filter(id=o_id)
            if task_list_objs:
                if task_list_objs[0].status == 1:
                    task_list_objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 300
                    response.msg = "该任务在操作中或者已完成，不能删除"

    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)


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
        platform = request.POST.get('platform')
        now = datetime.date.today()
        # 如果有平台,则自增1
        if platform:
            platform_objs = models.XiaohongshuBannedWordsPlatform.objects.filter(
                platform_name=platform,
                create_date=now
            )
            if platform_objs:
                platform_obj = platform_objs[0]
                platform_obj.submit_num = F('submit_num') + 1
                platform_obj.save()
            else:
                models.XiaohongshuBannedWordsPlatform.objects.create(
                    platform_name=platform
                )

            # key = "platform_" + platform
            # redis_obj = get_redis_obj()
            # num = redis_obj.get(key)
            # if num:
            #     num = int(num) + 1
            # else:
            #     num = 1
            # redis_obj.set(key, num)

        if forms_obj.is_valid():
            result = request_post(forms_obj.cleaned_data.get("context"))
            for item in result["data"]:
                if item["enable"] == False:
                    word = item["word"]
                    objs = models.XiaohongshuForbiddenText.objects.filter(word=word)
                    if not objs:
                        models.XiaohongshuForbiddenText.objects.create(word=word)
            if result['code'] == 0:
                response.data = result['data']
                response.code = 200
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())

    else:# 提交的词数 和 禁词数量
        submit_count_num = models.XiaohongshuBannedWordsPlatform.objects.all().aggregate(submit_num=Sum('submit_num')).get('submit_num')
        forbidden_objs_count = models.XiaohongshuForbiddenText.objects.all().count()

        data_list = []
        now_date = datetime.date.today()
        now_weekday = now_date.weekday() # 当前周几

        nowTime = (now_date - datetime.timedelta(days=now_weekday))
        for i in range(7):
            deletion_date = (nowTime + datetime.timedelta(days=i))

            submit_now_num = models.XiaohongshuBannedWordsPlatform.objects.filter(
                create_date=deletion_date).aggregate(submit_num=Sum('submit_num')).get('submit_num')

            forbidden_objs_now = models.XiaohongshuForbiddenText.objects.filter(
                create_datetime__gte=deletion_date.strftime('%Y-%m-%d 00:00:00'),
                create_datetime__lte=deletion_date.strftime('%Y-%m-%d 23:59:59')
            ).count()

            date_now = deletion_date
            if now_date == deletion_date:
                date_now = '今天'
            data_list.append({
                '时间': date_now,
                '提交禁词': submit_now_num,
                '入库禁词': forbidden_objs_now
            })

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            '提交的词数_总数':submit_count_num,
            '禁词数量_总数': forbidden_objs_count,
            '本周禁词统计': data_list
        }

    return JsonResponse(response.__dict__)


# if __name__ == '__main__':
#     context = """
#     孕吐严重试试这款蜂蜜糖!没想到!怀个孕能这么难受!天天吐,不吃吐,吃也吐!机缘巧合,我在朋友圈发现了一样好东西!麦卢卡蜂蜜糖!这个蜂蜜糖对孕妇hin友好,它含有天然寡糖,不是蔗糖,也不会囤积脂肪,作为孕期健康小零食不错!那个蜂蜜糖的牌子是AUSTRALIAN BY NATURE,澳洲本土品牌,代·购说它家的蜂场在奥克兰周边的原始森林,是世界上优·质的麦卢卡蜂源地。
#     """
#     request_post(context)