#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from __future__ import absolute_import, unicode_literals
from .celery import app
import requests
import datetime

# HOST = 'http://127.0.0.1:8001'
# HOST = 'http://xmgl.zhugeyingxiao.com'
from hurong import models
from publicFunc import send_email as SendEmail


# 发送邮件，每间隔5分钟一次
@app.task
def hurong_send_email():
    task_list_objs = models.TaskList.objects.exclude(percentage_progress=100).filter(is_delete=False)[0: 1]
    if task_list_objs:
        task_list_objs.update(status=3)
        # 发送标题和内容
        task_list_obj = task_list_objs[0]
        send_email_title = task_list_obj.send_email_title
        send_email_content = task_list_obj.send_email_content

        # 收件人列表
        task_info_objs = task_list_obj.taskinfo_set.filter(status=1)[0: 5]
        task_info_id_list = []
        send_email_list = []
        for task_info in task_info_objs:
            task_info_id_list.append(task_info.id)
            send_email_list.append(task_info.to_email)

        # 获取发送账号
        email_user_obj = models.EmailUserInfo.objects.all().order_by('use_number')[0]
        email_user_obj.use_number += 1
        email_user_obj.save()
        email_user = email_user_obj.email_user
        email_pwd = email_user_obj.email_pwd

        # 开始发送
        SendEmail.send_email(email_user, email_pwd, send_email_list, send_email_title, send_email_content)
        print("发送成功")

        # 计算完成百分比
        models.TaskInfo.objects.filter(id__in=task_info_id_list).update(status=2)
        task_objs = models.TaskInfo.objects.filter(task_list=task_list_obj)
        task_list_obj.percentage_progress = int(task_objs.filter(status=2).count() / task_objs.count())
        task_list_obj.save()




