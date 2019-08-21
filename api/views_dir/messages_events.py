

from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.tripartite_platform_oper import encoding_appid, encodingAESKey, encoding_token
from wechatpy.crypto import WeChatCrypto
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
            Reason = collection.getElementsByTagName("Reason")[0].childNodes[0].data
            FailTime = collection.getElementsByTagName("FailTime")[0].childNodes[0].data
            ScreenShot = collection.getElementsByTagName("ScreenShot")[0].childNodes[0].data

            if Event == 'weapp_audit_success': # 小程序审核通知
                pass

            else:
                content = collection.getElementsByTagName("Content")[0].childNodes[0].data
                print('content--------> ', content)

        else: # 文本消息
            pass


    return JsonResponse(response.__dict__)












