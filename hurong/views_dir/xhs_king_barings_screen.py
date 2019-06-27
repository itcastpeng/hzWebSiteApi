from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import json, datetime


@csrf_exempt
@account.is_token(models.UserProfile)
def xhs_king_barings_screen(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "GET":
        user_id = request.GET.get('user_id')

        # 小红书 霸屏王 重查覆盖
        if oper_type == 'get_xhs_account':
            id = request.GET.get('id')
            now = datetime.datetime.today()
            code = 200
            if not id:
                models.xhs_bpw_keywords.objects.all().update(
                    update_datetime=None
                )
                models.xhs_bpw_fugai.objects.filter(create_datetime__gte=now).delete()
                msg = '全部关键词重查成功, 请耐心等待'
            else:
                keywords_objs = models.xhs_bpw_keywords.objects.filter(id=id)
                if keywords_objs:
                    keywords_objs.update(
                        update_datetime=None
                    )
                    keywords_obj = keywords_objs[0]
                    models.xhs_bpw_fugai.objects.filter(keywords_id=keywords_obj.id).delete()
                    msg = '关键词《{}》重查成功, 请耐心等待'.format(keywords_obj.keywords)
                else:
                    code = 301
                    msg = '关键词不存在'

            response.code = code
            response.msg = msg

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)












