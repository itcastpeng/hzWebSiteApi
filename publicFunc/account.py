from django.http import JsonResponse
from publicFunc import Response
from hzWebSiteApi.settings import NoValidationTokenRoute
from hurong import models
import time, random, hashlib

# 生产随机字符串
def randon_str():
    STR = [chr(i) for i in range(65, 91)]       # 65-91对应字符A-Z
    str = [chr(i) for i in range(97, 123)]      # a-z
    number = [chr(i) for i in range(48, 58)]    # 0-9

    str_list = []
    str_list.extend(STR)
    str_list.extend(str)
    str_list.extend(number)

    random_num = random.randrange(10, 15)
    random.shuffle(str_list)
    return ''.join(str_list[:random_num])


# 用户输入的密码加密
def str_encrypt(pwd):
    """
    :param pwd: 密码
    :return:
    """
    pwd = str(pwd)
    hash = hashlib.md5()
    hash.update(pwd.encode())
    return hash.hexdigest()


# 生成token值
def get_token(pwd=None):
    if not pwd:
        pwd = randon_str()
    tmp_str = str(int(time.time()*1000)) + pwd
    return str_encrypt(tmp_str)


# 装饰器 判断token 是否正确
def is_token(table_obj):
    def is_token_decorator(func):
        def inner(request, *args, **kwargs):

            # 本机ip不进行token验证
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']

            # if ip == "127.0.0.1":
            #     return func(request, *args, **kwargs)


            # 手机设备不做token验证
            t = request.GET.get('t')

            if t == "phone" or t == 'ppxhs':
                if t == 'ppxhs':
                    if 'get_coverage_quantity' not in request.path and \
                        'xiaohongshuxiala/detail' not in request.path:
                        request_type = 1
                        if request.method == 'POST': # 请求方式
                            request_type = 2
                        models.AskLittleRedBook.objects.create(
                            request_url=request.path,
                            get_request_parameter=dict(request.GET),
                            post_request_parameter=dict(request.POST),
                            response_data='',
                            request_type=request_type,
                            status=2,
                        )
                return func(request, *args, **kwargs)

            # 不需要验证token的路由直接跳过
            for route in NoValidationTokenRoute:
                if request.get_full_path().startswith(route):
                    return func(request, *args, **kwargs)


            rand_str = request.GET.get('rand_str')
            timestamp = request.GET.get('timestamp', '')
            user_id = request.GET.get('user_id')
            # print('user_id -->', user_id)
            # print('timestamp -->', timestamp)
            # print('rand_str -->', rand_str)
            objs = table_obj.objects.filter(id=user_id)
            if objs:
                obj = objs[0]
                print('str_encrypt(timestamp + obj.token) -->', str_encrypt(timestamp + obj.token))
                # print('rand_str -->', rand_str)
                if str_encrypt(timestamp + obj.token) == rand_str:
                    flag = True
                else:
                    flag = False
            else:
                flag = False

            if not flag:
                response = Response.ResponseObj()
                response.code = 400
                response.msg = "token异常"
                return JsonResponse(response.__dict__)
            return func(request, *args, **kwargs)
        return inner

    return is_token_decorator


if __name__ == '__main__':
    # print(get_token(randon_str()))
    timestamp = str(int(time.time() * 1000))
    token = "892836aad41572b8d8fdd58c04103472"
    user_id = 1
    print(timestamp, str_encrypt(timestamp + token))
