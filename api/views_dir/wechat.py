#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from django.shortcuts import HttpResponse
from django.http import JsonResponse
from api import models
from publicFunc.account import get_token
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc import Response, account, base64_encryption
from publicFunc.role_choice import admin_list
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
        user_data['role_id'] = 7
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

            user_is_exists = False
            if models.UserProfile.objects.filter(openid=openid):
                user_is_exists = True

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
                new_user_id = update_user_info(openid, ret_obj, timestamp=timestamp, inviter_user_id=inviter_user_id)

                # ========================转接=================================
                transfer_user_id = event_key.get('transfer_user_id')  # 转接人ID
                token = event_key.get('token')  # 转接人token
                if transfer_user_id and token:
                    time_stamp = event_key.get('time_stamp')
                    transfer_objs = models.Transfer.objects.filter(speak_to_people_id=transfer_user_id, timestamp=time_stamp)
                    if transfer_objs and transfer_objs[0].whether_transfer_successful not in [3, '3']:
                        transfer_objs.update(
                            by_connecting_people_id=new_user_id,
                            whether_transfer_successful=2
                        )
                        weichat_api_obj = WeChatApi()
                        url = 'https://xcx.bjhzkq.com/handoverUser?transfer_user_id={}&new_user_id={}&token={}'.format(
                            transfer_user_id,
                            new_user_id,
                            token
                        )
                        post_data = {
                            "touser": openid,
                            "msgtype": "news",  # 图文消息 图文消息条数限制在1条以内，注意，如果图文数超过1，则将会返回错误码45008。
                            "news": {
                                "articles": [
                                    {
                                        "title": '{}请求将建站数据转接给您'.format(base64_encryption.b64decode(transfer_objs[0].speak_to_people.name)),
                                        "description": '如果您接收了数据转接, 发起人的所有数据 将同步到您的账户下',
                                        "url": url,
                                        # "picurl": 'http://tianyan.zhugeyingxiao.com/合众logo.png'
                                        "picurl": transfer_objs[0].speak_to_people.head_portrait
                                    }
                                ]
                            }
                        }
                    else:
                        if transfer_objs:
                            content = '二维码异常, 请刷新'

                        else:
                            content = '二维码已过期, 请刷新'

                        post_data = {
                            "touser": openid,
                            "msgtype": "text",
                            "text": {
                                "content": content
                            }
                        }
                    post_data = bytes(json.dumps(post_data, ensure_ascii=False), encoding='utf-8')
                    weichat_api_obj.news_service(post_data)

                # =========================创建子级=================
                parent_id = event_key.get('parent_id')  # 父级ID
                if parent_id:
                    InviteTheChildObjs = models.InviteTheChild.objects.filter(
                        timestamp=timestamp
                    ).update(
                        whether_transfer_successful=2,
                        child_id=new_user_id
                    )
                    if InviteTheChildObjs:
                        parent_user_obj = models.UserProfile.objects.get(id=parent_id)
                        chil_user_count = models.UserProfile.objects.filter(
                            inviter_id=parent_id
                        ).count()
                        if parent_user_obj.number_child_users > chil_user_count:  # 如果可创建数量 大于 已创建数量
                            user_obj = models.UserProfile.objects.get(id=new_user_id)
                            url = 'https://xcx.bjhzkq.com/joinTeam?parent_id={}&new_user_id={}&user_is_exists={}&timestamp={}&token={}'.format(
                                parent_id,
                                new_user_id,
                                user_is_exists,
                                timestamp,
                                user_obj.token
                            )
                            post_data = {
                                "touser": openid,
                                "msgtype": "news",  # 图文消息 图文消息条数限制在1条以内，注意，如果图文数超过1，则将会返回错误码45008。
                                "news": {
                                    "articles": [
                                        {
                                            "title": '我是{} 加入我的团队吧'.format(
                                                base64_encryption.b64decode(parent_user_obj.name),
                                            ),
                                            "description": '加入团队将看到邀请人所有数据',
                                            "url": url,
                                            "picurl": parent_user_obj.head_portrait
                                        }
                                    ]
                                }
                            }

                        else:
                            post_data = {
                                "touser": openid,
                                "msgtype": "text",
                                "text": {
                                    "content": '邀请人子级用户达到上限'
                                }
                            }
                    else:
                        post_data = {
                            "touser": openid,
                            "msgtype": "text",
                            "text": {
                                "content": '未找到二维码信息'
                            }
                        }
                    post_data = bytes(json.dumps(post_data, ensure_ascii=False), encoding='utf-8')
                    weichat_api_obj.news_service(post_data)
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
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        pass

    else:
        # 获取用于登录的微信二维码
        if oper_type == "login_qrcode":
            weichat_api_obj = WeChatApi()
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

        # 获取转接 二维码(当前用户转接给别的用户)
        elif oper_type == 'transfer_all_user_information':
            weichat_api_obj = WeChatApi()
            obj = models.UserProfile.objects.get(id=user_id)
            timestamp = str(int(time.time() * 1000))
            qc_code_url = weichat_api_obj.generate_qrcode({
                'timestamp': timestamp,
                'time_stamp': timestamp,
                'transfer_user_id': user_id,
                'token': obj.token,
            })
            models.Transfer.objects.create(
                speak_to_people_id=user_id,
                timestamp=timestamp,
            )
            response.code = 200
            response.msg = '生成成功'
            response.data = {
                'qc_code_url': qc_code_url,
                'time_stamp': timestamp  # 判断是否扫码
            }

        # 查询被转接人是否扫码
        elif oper_type == 'check_whether_code_scanned_transferee':
            timestamp = request.GET.get('time_stamp')
            user_obj = models.UserProfile.objects.get(id=user_id)
            if user_obj.role_id not in admin_list and not user_obj.inviter:
                objs = models.Transfer.objects.filter(
                    speak_to_people_id=user_id,
                    timestamp=timestamp
                )
                if objs:
                    obj = objs[0]
                    if obj.whether_transfer_successful in [2, '2']:
                        msg = '已经扫码'
                        code = 200
                    elif obj.whether_transfer_successful in [4, '4']:
                        msg = '已完成交接'
                        code = 401
                    elif obj.whether_transfer_successful in [5, '5']:
                        code = 501
                        msg = '已拒绝交接'
                    else:
                        code = 301
                        msg = '未扫码'
                else:
                    code = 301
                    msg = '未查询到转接记录'
                response.code = code
                response.msg = msg
            else:
                response.code = 301
                if user_obj.inviter:
                    msg = '子级用户不能转接'
                else:
                    msg = '管理员不能转接'
                response.msg = msg

        # 获取 创建子级二维码
        elif oper_type == 'get_create_sub_qr_code':
            weichat_api_obj = WeChatApi()
            timestamp = str(int(time.time() * 1000))
            obj = models.UserProfile.objects.get(id=user_id)
            chil_user_count = models.UserProfile.objects.filter(
                inviter_id=user_id
            ).count()
            if obj.number_child_users > chil_user_count:
                qc_code_url = weichat_api_obj.generate_qrcode({
                    'timestamp': timestamp,
                    'parent_id': user_id,
                })
                models.InviteTheChild.objects.create(
                    parent_id=user_id,
                    # child_id=new_user_id,
                    timestamp=timestamp,
                )
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'qc_code_url': qc_code_url,
                    'timestamp': timestamp
                }
            else:
                response.code = 301
                response.msg = '您的子级用户已达到上限'

        # 查询创建子级是否扫码
        elif oper_type == 'query_sub_esau_code':
            timestamp = request.GET.get('time_stamp')
            objs = models.InviteTheChild.objects.filter(timestamp=timestamp, parent_id=user_id)
            if objs:
                obj = objs[0]
                if obj.whether_transfer_successful in [2, '2']:
                    msg = '已经扫码'
                    code = 200
                elif obj.whether_transfer_successful in [4, '4']:
                    msg = '已完成加入'
                    code = 401
                elif obj.whether_transfer_successful in [5, '5']:
                    code = 501
                    msg = '已拒绝加入'
                else:
                    code = 502
                    msg = '未扫码'
            else:
                code = 301
                msg = '未查询到二维码信息'
            response.code = code
            response.msg = msg

    return JsonResponse(response.__dict__)

# 创建栏目
def set_wechat_column(request):
    WeChatApiObjs = WeChatApi()

    button = {
        'button': [
            {
                "type": "view",
                "name": "阿斗建站",
                "url": "https://xcx.bjhzkq.com/wx/"
            },
        ]
    }
    data = WeChatApiObjs.createMenu(button)

    return HttpResponse(data)

