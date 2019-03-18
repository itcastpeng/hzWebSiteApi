#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

import base64


# 加密
def b64encode(string):
    return str(base64.b64encode(string.encode('utf8')), encoding='utf8')


# 解密
def b64decode(string):
    return base64.b64decode(string.encode('utf8')).decode('utf8')
