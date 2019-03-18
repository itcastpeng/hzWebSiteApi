from publicFunc import Response
from django.http import JsonResponse
from publicFunc.weixin import weixin_gongzhonghao_api


# 权限签名算法(转发朋友圈等)
def letter_operation(request, oper_type):
    response = Response.ResponseObj()
    if oper_type == 'js_sdk_permissions':
        weixin_obj = weixin_gongzhonghao_api.WeChatApi()
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'data': weixin_obj.get_signature()
        }
        response.note = {
            'signature': 'signature',
            'timestamp': '时间戳',
            'noncestr': '随机值(32位)',
            'appid': 'appid',
        }
    return JsonResponse(response.__dict__)
