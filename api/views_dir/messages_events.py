

from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.tripartite_platform_oper import encoding_appid, encodingAESKey, encoding_token
from wechatpy.crypto import WeChatCrypto
from api.views_dir import message_inform

import xml.etree.cElementTree as ET, xml.dom.minidom as xmldom, requests


def messages_events_oper(request, oper_type, appid):
    response = Response.ResponseObj()

    # 消息与事件接收
    if oper_type == 'callback':
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        msg_signature = request.GET.get('msg_signature')
        postdata = request.body.decode(encoding='UTF-8')
        # xml_tree = ET.fromstring(postdata)
        # encrypt = xml_tree.find("Encrypt").text
        print('==--------121111111111postdata-> ', postdata)
        crypto = WeChatCrypto(encoding_token, encodingAESKey, encoding_appid)
        decrypted_xml = crypto.decrypt_message(
            postdata,
            msg_signature,
            timestamp,
            nonce
        )
        DOMTree = xmldom.parseString(decrypted_xml)
        collection = DOMTree.documentElement
        MsgType = collection.getElementsByTagName("MsgType")[0].childNodes[0].data

        print('Event------------Event-------> ', MsgType)
        Event = collection.getElementsByTagName("Event")[0].childNodes[0].data
        print('Event-1-> ', DOMTree)
        print('Event-->2 ', collection)
        print('Event--3> ', Event)
        if MsgType == 'event': # api消息
            ToUserName = collection.getElementsByTagName("ToUserName")[0].childNodes[0].data
            FromUserName = collection.getElementsByTagName("FromUserName")[0].childNodes[0].data
            CreateTime = collection.getElementsByTagName("CreateTime")[0].childNodes[0].data

            # FailTime = collection.getElementsByTagName("FailTime")[0].childNodes[0].data
            # ScreenShot = collection.getElementsByTagName("ScreenShot")[0].childNodes[0].data

            if Event == 'weapp_audit_success': # 小程序审核通通过知
                # 更新审核状态
                applet_code_version_obj = models.AppletCodeVersion.objects.filter(applet__appid=ToUserName).order_by('-create_datetime')[0]
                applet_code_version_obj.status = 0
                applet_code_version_obj.save()

                client_applet_objs = models.ClientApplet.objects.filter(appid=ToUserName)
                user_id = client_applet_objs[0].user_id
                nick_name = client_applet_objs[0].nick_name
                msg = "微信小程序: %s 发布代码审核通过" % nick_name
                message_inform.save_msg_inform(user_id, msg, is_send_admin=True)
            elif Event == 'weapp_audit_fail':   # 小程序审核不通过
                Reason = collection.getElementsByTagName("Reason")[0].childNodes[0].data
                applet_code_version_obj = models.AppletCodeVersion.objects.filter(applet__appid=ToUserName).order_by('-create_datetime')[0]
                applet_code_version_obj.status = 1
                applet_code_version_obj.status = Reason
                applet_code_version_obj.save()

                client_applet_objs = models.ClientApplet.objects.filter(appid=ToUserName)
                user_id = client_applet_objs[0].user_id
                nick_name = client_applet_objs[0].nick_name
                msg = "微信小程序: %s 发布代码审核不通过\n不通过原因: %s " % (nick_name, Reason)
                message_inform.save_msg_inform(user_id, msg, is_send_admin=True)
            elif Event == "SCAN":
                pass
            else:
                content = collection.getElementsByTagName("Content")[0].childNodes[0].data
                print('content--------> ', content)

        else: # 文本消息
            pass


    return JsonResponse(response.__dict__)












