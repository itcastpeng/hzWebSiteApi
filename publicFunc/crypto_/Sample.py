#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# Author: jonyqin
# Created Time: Thu 11 Sep 2014 03:55:41 PM CST
# File Name: demo.py
# Description: WXBizMsgCrypt 使用demo文件
#########################################################################
from zhugeleida.public.crypto_.WXBizMsgCrypt import WXBizMsgCrypt

'''
signature = request.GET.get('signature')
timestamp = request.GET.get('timestamp')
nonce = request.GET.get('nonce')
msg_signature = request.GET.get('msg_signature')
'''


if __name__ == "__main__":   
   """ 
   1.第三方回复加密消息给公众平台；
   2.第三方收到公众平台发送的消息，验证消息的安全性，并对消息进行解密。
   """
   encodingAESKey = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG" 
   to_xml = """ <xml><ToUserName><![CDATA[oia2TjjewbmiOUlr6X-1crbLOvLw]]></ToUserName><FromUserName><![CDATA[gh_7f083739789a]]></FromUserName><CreateTime>1407743423</CreateTime><MsgType>  <![CDATA[video]]></MsgType><Video><MediaId><![CDATA[eYJ1MbwPRJtOvIEabaxHs7TX2D-HV71s79GUxqdUkjm6Gs2Ed1KF3ulAOA9H1xG0]]></MediaId><Title><![CDATA[testCallBackReplyVideo]]></Title><Descript  ion><![CDATA[testCallBackReplyVideo]]></Description></Video></xml>"""
   token = "spamtest"
   nonce = "1320562132"
   appid = "wx2c2769f8efd9abc2"
   #测试加密接口
   encryp_test = WXBizMsgCrypt(token,encodingAESKey,appid)
   ret,encrypt_xml = encryp_test.EncryptMsg(to_xml,nonce)
   print (ret,encrypt_xml)
   

   #测试解密接口
   timestamp = "1409735669"
   msg_sign  = "5d197aaffba7e9b25a30732f161a50dee96bd5fa"   
   
   from_xml = """<xml><AppId><![CDATA[wx67e2fde0f694111c]]></AppId><Encrypt><![CDATA[o834havwdyEGc504ax8gQPiZBihUfctoJR/cWqOF3lEURCE3ze1F60aT/PhPff0QVtZOEI/gfnWwnW2tHs1fGf9oKf31/mW/OolgWJ49e8TC1gX1zBL2G0PjGhsVWQT4QeKNjYCDw/mnOsNJKncVtQmmlOSzNDzQVi49uBYFZ20hwKTcY+ePx5X2Q3UnoMVsQLrH9cuhw4/JySgW8aLhjK1Kp28U4ohhg11az432JDZ18V+W4591U+aqCXia4idLIzAyT0pk4Q5mnU6GeswNAWWJKYTKmLEM5p6UdUA4zjecXw4UgFnAkQwKyp2c6Qg4ZTHlD0oXPueNXM0JUhbw8i+np+vBkOR8VE0wwZ2C/aQbffHi4VElsi78QN7/ZXW3gvBz769Dj0dbmcAmH21vB6DbH2+XuCeEF3Qep76y+hccH/fJ/aRBg54CdZRB2ReyUoiYuM8xKvy5RkQpenrA==]]></Encrypt></xml>"""
   decrypt_test = WXBizMsgCrypt(token,encodingAESKey,appid)
   ret ,decryp_xml = decrypt_test.DecryptMsg(from_xml, msg_sign, timestamp, nonce)
   print (ret ,decryp_xml)
   
   
   
