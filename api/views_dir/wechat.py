#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com


from django.shortcuts import HttpResponse
from django.http import JsonResponse

from api import models
# import base64
# import time
import datetime
import json
import xml.dom.minidom

from publicFunc.account import get_token
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc import Response
from publicFunc import account
from publicFunc import base64_encryption
import time


# 创建或更新用户信息
def update_user_info(openid, ret_obj, timestamp=None, inviter_user_id=None):
    """
    :param openid:  微信openid
    :param inviter_user_id: 邀请人id
    :param ret_obj:  微信数据
    :return:
    """
    print('ret_obj -->', ret_obj)
    """
        {
            'subscribe_scene': 'ADD_SCENE_QR_CODE',
            'city': '丰台',
            'openid': 'oX0xv1pJPEv1nnhswmSxr0VyolLE',
            'qr_scene': 0,
            'tagid_list': [],
            'nickname': '张聪',
            'subscribe_time': 1527689396,
            'country': '中国',
            'groupid': 0,
            'subscribe': 1,
            'qr_scene_str': '{"timestamp": "1527689369548"}',
            'headimgurl': 'http://thirdwx.qlogo.cn/mmopen/oFswpUmYn53kTv5QdmmONicVJqp3okrhHospu6icoLF7Slc5XyZWR
                            96STN9RiakoBQn1uoFJIWEicJgJ1QjR5iaGOgWNQ5BSVqFe5/132',
            'province': '北京',
            'sex': 1,
            'language': 'zh_CN',
            'remark': ''
        }


        {
            "openid":"oX0xv1pJPEv1nnhswmSxr0VyolLE",
            "nickname":"张聪",
            "sex":1,
            "language":"zh_CN",
            "city":"丰台",
            "province":"北京",
            "country":"中国",
            "headimgurl":"http://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJWGnNTvluYlHj8qt8HnxMlwbRiad
                            bv4TNrp4watI2ibPPAp2Hu6Sm1BqYf6IicNWsSrUyaYjIoy2Luw/132",
            "privilege":[]
        }
    """
    # 保证1个微信只能够关联1个账号
    user_objs = models.UserProfile.objects.filter(openid=openid)

    user_data = {
        "sex": ret_obj.get('sex'),
        "country": ret_obj.get('country'),
        "province": ret_obj.get('province'),
        "city": ret_obj.get('city'),
        "login_timestamp": timestamp,
    }

    if user_objs:
        user_id = user_objs[0].id
        user_objs.update(**user_data)
    else:
        encode_username = base64_encryption.b64encode(ret_obj['nickname'])
        # encodestr = base64.b64encode(ret_obj['nickname'].encode('utf8'))
        # encode_username = str(encodestr, encoding='utf8')
        overdue_date = datetime.datetime.now() + datetime.timedelta(days=30)

        subscribe = ret_obj.get('subscribe')

        # 如果没有关注，获取个人信息判断是否关注
        if not subscribe:
            weichat_api_obj = WeChatApi()
            ret_obj = weichat_api_obj.get_user_info(openid=openid)
            subscribe = ret_obj.get('subscribe')

        user_data['inviter_id'] = inviter_user_id
        user_data['head_portrait'] = ret_obj.get('headimgurl')
        user_data['subscribe'] = subscribe
        user_data['name'] = encode_username
        user_data['openid'] = ret_obj.get('openid')
        # user_data['overdue_date'] = overdue_date
        user_data['token'] = get_token()
        print("user_data --->", user_data)
        user_obj = models.UserProfile.objects.create(**user_data)
        user_id = user_obj.id
    return user_id


# 微信服务器调用的接口
def wechat(request):
    weichat_api_obj = WeChatApi()

    signature = request.GET.get("signature")
    timestamp = request.GET.get("timestamp")
    nonce = request.GET.get("nonce")
    echostr = request.GET.get("echostr")

    # 该值做消息解密使用，当前未使用加密模式，参考微信开发文档 https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421135319
    # EncodingAESKey = 'LFYzOBp42g5kwgSUWhGC9uRugSmpyetKfAsJa5FdFHX'

    check_result = weichat_api_obj.checkSignature(timestamp, nonce, signature)
    print('check_result -->', check_result)

    if check_result:

        if request.method == "GET":
            return HttpResponse(echostr)
        else:
            body_text = str(request.body, encoding="utf8")
            print('body_text -->', body_text)

            # 使用minidom解析器打开 XML 文档
            DOMTree = xml.dom.minidom.parseString(body_text)
            collection = DOMTree.documentElement
            print('collection -->', collection)

            # 事件类型
            event = collection.getElementsByTagName("Event")[0].childNodes[0].data
            print("event -->", event)

            # 用户的 openid
            openid = collection.getElementsByTagName("FromUserName")[0].childNodes[0].data

            # 扫描带参数的二维码
            if event in ["subscribe", "SCAN"]:
                # subscribe = 首次关注
                # SCAN = 已关注
                # 事件 Key 值
                ret_obj = weichat_api_obj.get_user_info(openid=openid)

                event_key = collection.getElementsByTagName("EventKey")[0].childNodes[0].data
                if event == "subscribe":
                    event_key = event_key.split("qrscene_")[-1]
                event_key = json.loads(event_key)
                timestamp = event_key.get('timestamp')  # 时间戳，用于判断是否扫码登录
                inviter_user_id = event_key.get('inviter_user_id')      # 邀请人id
                update_user_info(openid, ret_obj, timestamp=timestamp, inviter_user_id=inviter_user_id)

            # 取消关注
            elif event == "unsubscribe":
                models.UserProfile.objects.filter(openid=openid).update(openid=None)

                # we_chat_public_send_msg_obj.sendTempMsg(post_data)

            return HttpResponse("")

    else:
        return HttpResponse(False)


# @csrf_exempt
# def wechat_login(request):
#     response = ResponseObj()
#     timestamp = request.POST.get('timestamp')
#     user_objs = models.zhugedanao_userprofile.objects.select_related('level_name').filter(timestamp=timestamp)
#     if user_objs:
#         user_obj = user_objs[0]
#         response.code = 200
#         decode_username = base64.b64decode(user_obj.username)
#         username = str(decode_username, 'utf-8')
#         role_id = ''
#         if user_obj.role:
#             role_id = user_obj.role.id
#         response.data = {
#             'token': user_obj.token,
#             'user_id': user_obj.id,
#             'set_avator': user_obj.set_avator,
#             'role_id':role_id,
#             'username':username,
#             'level_name': user_obj.level_name.name
#         }
#         response.msg = "登录成功"
#     else:
#         response.code = 405
#         response.msg = '扫码登录异常，请重新扫描'
#
#     return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def wechat_oper(request, oper_type):
    # print('oper_type -->', oper_type)
    response = Response.ResponseObj()
    if request.method == "POST":
        pass

    else:
        # 获取用于登录的微信二维码
        weichat_api_obj = WeChatApi()
        if oper_type == "login_qrcode":
            timestamp = str(int(time.time() * 1000))
            qc_code_url = weichat_api_obj.generate_qrcode({
                'timestamp': timestamp,
            })
            print(qc_code_url)

            expire_date = (datetime.datetime.now().date() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            response.code = 200
            response.data = {
                'qc_code_url': qc_code_url,
                'expire_date': expire_date,
                'timestamp': timestamp,
            }

        # 邀请成员页面展示信息
        elif oper_type == "invite_members":
            user_id = request.GET.get('user_id')
            team_id = request.GET.get('team_id')

            redirect_uri = "http://api.zhugeyingxiao.com/tianyan/team/invite_members/{team_id}".format(team_id=team_id)
            open_weixin_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                              "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                              "&state={user_id}#wechat_redirect"\
                .format(
                    appid=weichat_api_obj.APPID,
                    redirect_uri=redirect_uri,
                    user_id=user_id
                )

            obj = models.UserProfileTeam.objects.select_related('team', 'user').get(team_id=team_id, user_id=user_id)
            response.code = 200
            response.data = {
                "open_weixin_url": open_weixin_url,
                "team_name": obj.team.name,
                "user_name": base64_encryption.b64decode(obj.user.name),
                "set_avator": obj.user.set_avator
            }

            response.note = {
                "open_weixin_url": "点击接受邀请后请求的url",
                "team_name": "团队名称",
                "user_name": "邀请人名称",
                "set_avator": "邀请人头像"
            }

    return JsonResponse(response.__dict__)

# # 获取用于登录的微信二维码
# @account.is_token(models.UserProfile)
# def weichat_generate_qrcode(request):
#     weichat_api_obj = WeChatApi()
#     response = ResponseObj()
#     user_id = request.GET.get('user_id')
#     qc_code_url = weichat_api_obj.generate_qrcode({'inviter_user_id': user_id})
#     print(qc_code_url)
#
#     expire_date = (datetime.datetime.now().date() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
#     response.code = 200
#     response.data = {
#         'qc_code_url': qc_code_url,
#         'expire_date': expire_date
#     }
#
#     return JsonResponse(response.__dict__)
