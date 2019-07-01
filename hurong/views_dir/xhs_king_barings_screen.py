from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import json, datetime, redis


@csrf_exempt
@account.is_token(models.UserProfile)
def xhs_king_barings_screen(request, oper_type):
    response = Response.ResponseObj()
    if request.method == "POST":
        user_id = request.GET.get('user_id')

        # 小红书 霸屏王 重查覆盖
        if oper_type == 'get_xhs_account':
            user_id_list = request.POST.get('user_id_list')
            now = datetime.datetime.today()
            code = 200
            redis_obj = redis.StrictRedis(host='redis', port=6381, db=0, decode_responses=True)

            user_id_list = json.loads(user_id_list)
            if len(user_id_list) >= 1:
                for user_id in user_id_list:
                    now_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    key = "XHS_FUGAI_{now_date}_{uid}".format(now_date=now_date, uid=user_id)
                    redis_obj.delete(key)

                    keywords_objs = models.xhs_bpw_keywords.objects.filter(uid=user_id)
                    keywords_objs.update(
                        update_datetime=None
                    )
                    for keywords_obj in keywords_objs:
                        models.xhs_bpw_fugai.objects.filter(
                            create_datetime__gte=now,
                            keywords_id=keywords_obj.id
                        ).delete()
                msg = '重查成功, 请耐心等待'
            else:
                code = 301
                msg = '重查失败,原因:用户ID不存在'

            response.code = code
            response.msg = msg


    else:

        # 查询 该人覆盖量 和 已完成覆盖
        if oper_type == 'get_coverage_quantity':
            user_id_list = request.GET.get('user_id_list')
            user_id_list = json.loads(user_id_list)

            now_date_time = datetime.datetime.today().strftime('%Y-%m-%d 00:00:00')
            if len(user_id_list) >= 1:
                data_list = []
                for user_id in user_id_list:
                    count = models.xhs_bpw_keywords.objects.filter(uid=user_id).count()
                    success = models.xhs_bpw_keywords.objects.filter(uid=user_id, update_datetime__gte=now_date_time).count()

                    data_list.append({
                        'user_id': user_id,
                        'count': count,
                        'success': success,
                    })
                response.code = 200
                response.msg = '查询成功'
                response.data = data_list

            else:
                response.code = 301
                response.msg = '重查失败,原因:用户ID不存在'

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)












