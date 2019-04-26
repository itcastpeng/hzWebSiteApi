#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from __future__ import absolute_import, unicode_literals
from .celery import app
import requests
import datetime
import os
import sys

# HOST = 'http://127.0.0.1:8001'
# HOST = 'http://xmgl.zhugeyingxiao.com'
project_dir = os.path.dirname(os.getcwd())
sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'hzWebSiteApi.settings'
import django
django.setup()


from hurong import models
from publicFunc.send_email import SendEmail
import redis

# 更新小红书下拉数据
@app.task
def xiaohongshu_xiala_update_data():
    # 将redis中存储的下拉数据存储到数据库中
    redis_obj = redis.StrictRedis(
        host='spider_redis',
        port=1111,
        db=13,
        password="Fmsuh1J50R%T*Lq15TL#IkWb#oMp^@0OYzx5Q2CSEEs$v9dd*mnqRFByoeGZ"
    )
    redis_key = "xiaohongshu_xiala_data"
    for _ in range(redis_obj.llen(redis_key)):
        item = redis_obj.rpop(redis_key).decode('utf8')
        keywords = item['keywords']
        objs = models.XiaohongshuXiaLaKeywords.objects.filter(keywords=keywords)
        if objs:
            xialaci_num = 0
            for index, i in enumerate(item['data']):
                xialaci_num += 1
                xialaci = i['text'] + " " + i['desc']
                if not models.XiaohongshuXiaLaKeywordsChildren.objects.filter(keywords=xialaci):
                    models.XiaohongshuXiaLaKeywordsChildren.objects.create(keywords=keywords, parent=objs[0])
            objs.update(
                status=2,
                biji_num=item['data'][0]['desc'],
                xialaci_num=xialaci_num,
                update_datetime=datetime.datetime.now()
            )

# 发送邮件，每间隔5分钟一次
@app.task
def hurong_send_email():
    # 将已经完成的任务状态改成已完成
    models.TaskList.objects.filter(percentage_progress=100, status=2).update(status=3)

    # # 开始任务
    # task_list_objs = models.TaskList.objects.exclude(percentage_progress=100).filter(is_delete=False)[0: 1]
    # if task_list_objs:
    #     # 发送标题和内容
    #     task_list_obj = task_list_objs[0]
    #     task_list_obj.status = 2
    #     task_list_obj.save()
    #
    #     send_email_title = task_list_obj.send_email_title
    #     send_email_content = task_list_obj.send_email_content
    #
    #     # 收件人列表
    #     task_info_objs = task_list_obj.taskinfo_set.filter(status=1)[0: 5]
    #     task_info_id_list = []
    #     send_email_list = []
    #     for task_info in task_info_objs:
    #         task_info_id_list.append(task_info.id)
    #         send_email_list.append(task_info.to_email)
    #
    #     while True:
    #         email_user_obj = models.EmailUserInfo.objects.all().order_by('use_number')[0]
    #         email_user_obj.use_number += 1
    #         email_user_obj.save()
    #         email_user = email_user_obj.email_user
    #         email_pwd = email_user_obj.email_pwd
    #         print(email_user, email_pwd, send_email_list)
    #         send_email_obj = SendEmail(
    #             email_user,
    #             email_pwd,
    #             send_email_list,
    #             send_email_title,
    #             send_email_content
    #         )
    #         send_email_obj.send_email()
    #         if send_email_obj.send_status:
    #             # 计算完成百分比
    #             models.TaskInfo.objects.filter(id__in=task_info_id_list).update(status=2)
    #             task_objs = models.TaskInfo.objects.filter(task_list=task_list_obj)
    #             is_send_count = task_objs.filter(status=2).count()  # 已经发送成功的总数
    #             count = task_objs.count()   # 该任务的总任务数
    #             # print(is_send_count, count, is_send_count / count)
    #             task_list_obj.percentage_progress = int(is_send_count / count * 100)
    #             task_list_obj.save()
    #             break
    #         else:
    #             email_user_obj.is_available = False
    #             email_user_obj.save()


