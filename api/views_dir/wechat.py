#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from django.shortcuts import HttpResponse
from django.http import JsonResponse
from api import models
from publicFunc.account import get_token
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc import Response
from publicFunc import account
from publicFunc import base64_encryption
import json, datetime, xml.dom.minidom, time


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
                print('event_key -->', event_key)
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


@account.is_token(models.UserProfile)
def wechat_oper(request, oper_type):
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


    return JsonResponse(response.__dict__)

# 创建栏目
def set_wechat_column(request):
    WeChatApiObjs = WeChatApi()
    button = [
        {
            "type": "view",
            "name": "阿斗建站",
            "url": "https://xcx.bjhzkq.com/wx/"
        },
    ]
    data = WeChatApiObjs.createMenu(button)

    return HttpResponse(data)