#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com
import hashlib
import uuid


class WeixinApiPublic(object):

    def sha1(self, string):
        return hashlib.sha1(string.encode('utf8')).hexdigest()

    def md5(self, string):
        m = hashlib.md5()
        m.update(string.encode('utf8'))
        return m.hexdigest()

    # 返回 xml
    def toXml(self, params):
        xml = []
        for k in sorted(params.keys()):
            v = params.get(k)
            if k == 'detail' and not v.startswith('<![CDATA['):
                v = '<![CDATA[{}]]>'.format(v)
            xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
        return '<xml>{}</xml>'.format(''.join(xml))

    # 返回32为 时间戳
    def generateRandomStamping(self):
        return str(uuid.uuid4()).replace('-', '')

    # 生成 签名
    def shengchengsign(self, result_data, key=None):
        ret = []
        for k in sorted(result_data.keys()):
            if (k != 'sign') and (k != '') and (result_data[k] is not None):
                ret.append('%s=%s' % (k, result_data[k]))
        string = '&'.join(ret)
        string_sign_temp = string
        if key:
            string_sign_temp = '{string}&key={key}'.format(
                string=string,
                key=key
            )
        return string_sign_temp
