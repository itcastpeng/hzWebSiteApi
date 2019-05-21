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
from django.db.models.aggregates import Count
from publicFunc.send_email import SendEmail
import redis
import json
from openpyxl import Workbook


# 更新小红书下拉数据
@app.task
def xiaohongshu_xiala_update_data():
    # 1、将redis中存储的下拉数据存储到数据库中
    redis_obj = redis.StrictRedis(
        host='spider_redis',
        port=1111,
        db=13,
        password="Fmsuh1J50R%T*Lq15TL#IkWb#oMp^@0OYzx5Q2CSEEs$v9dd*mnqRFByoeGZ"
    )
    redis_key = "xiaohongshu_xiala_data"
    for _ in range(redis_obj.llen(redis_key)):
        item = json.loads(redis_obj.rpop(redis_key).decode('utf8'))
        keywords = item['keywords']
        objs = models.XiaohongshuXiaLaKeywords.objects.filter(keywords=keywords)
        if objs:
            xialaci_num = 0
            for index, i in enumerate(item['data']):
                xialaci_num += 1
                xialaci = i['text'] + " " + i['desc']
                if not models.XiaohongshuXiaLaKeywordsChildren.objects.filter(keywords=xialaci):
                    models.XiaohongshuXiaLaKeywordsChildren.objects.create(keywords=xialaci, parent=objs[0])
            objs.update(
                status=2,
                biji_num=item['data'][0]['desc'],
                xialaci_num=xialaci_num,
                update_datetime=datetime.datetime.now()
            )

    # 2、假如redis队列中没有下拉关键词，则将数据库中等待查询的下拉词存入redis队列中
    redis_key = "xiaohongshu_task_list"
    if redis_obj.llen(redis_key) == 0:
        objs = models.XiaohongshuXiaLaKeywords.objects.filter(status=1)
        for obj in objs:
            item = {
                "keywords": obj.keywords,
                "task_type": "xiaohongshu_xiala"
            }
            redis_obj.lpush(redis_key, json.dumps(item))


# 更新小红书查覆盖数据
@app.task
def xiaohongshu_fugai_update_data():
    # 1、将redis中存储的覆盖数据存储到数据库中
    redis_obj = redis.StrictRedis(
        host='spider_redis',
        port=1111,
        db=13,
        password="Fmsuh1J50R%T*Lq15TL#IkWb#oMp^@0OYzx5Q2CSEEs$v9dd*mnqRFByoeGZ"
    )
    redis_key = "xiaohongshu_fugai_data"

    for _ in range(redis_obj.llen(redis_key)):
        item = json.loads(redis_obj.rpop(redis_key).decode('utf8'))
        keywords = item['keywords']
        page_id_list = item['page_id_list']
        total_count = item['total_count']
        # {'keywords': '隆鼻', 'total_count': 0, 'page_id_list': []}
        objs = models.XiaohongshuFugai.objects.filter(keywords=keywords)
        for obj in objs:
            flag = False
            item_data = {
                'rank': 0,
                'biji_num': total_count,
                'update_datetime': datetime.datetime.now(),
            }
            for item in page_id_list:
                obj.biji_num = total_count
                obj.update_datetime = datetime.datetime.now()
                obj.status = 2
                if item['id'] in obj.url:
                    flag = True
                    obj.rank = item['rank']
                    obj.is_shoulu = True
                    item_data['rank'] = item['rank']

                obj.save()

            now_date = datetime.datetime.now().strftime("%Y-%m-%d")
            objs = models.XiaohongshuFugaiDetail.objects.filter(keywords=obj, create_datetime__gt=now_date)
            if objs:  # 已经创建当日详情
                if flag:    # 查找到覆盖
                    objs.update(**item_data)
            else:  # 不存在
                item_data['keywords'] = obj
                models.XiaohongshuFugaiDetail.objects.create(**item_data)

    # 2、假如redis队列中没有任务，则将数据库中等待查询的下拉词存入redis队列中
    redis_key = "xiaohongshu_task_list"
    if redis_obj.llen(redis_key) == 0:
        objs = models.XiaohongshuFugai.objects.all().values('keywords').annotate(Count('id'))
        for obj in objs:
            now_date = datetime.datetime.now().strftime("%Y-%m-%d")
            print('obj -->', obj)
            detail_objs = models.XiaohongshuFugaiDetail.objects.filter(keywords=obj['keywords'], create_datetime__gt=now_date)
            # 将今天未查询的任务放入redis队列中
            if not detail_objs:
                item = {
                    "keywords": obj.keywords,
                    # "url": obj.url,
                    "count": obj['id__count'],      # 当前关键词存在几个任务
                    # "select_type": obj.select_type,
                    "task_type": "xiaohongshu_fugai"
                }
                redis_obj.lpush(redis_key, json.dumps(item))


# 保存下拉和覆盖的数据到报表中
@app.task
def xiaohongshu_shengcheng_baobiao():
    # 保存下拉报表
    objs = models.XiaohongshuXiaLaKeywords.objects.filter(status=2)
    wb = Workbook()
    ws = wb.active

    ws.cell(row=1, column=1, value="编号")
    ws.cell(row=1, column=2, value="关键词名称")
    ws.cell(row=1, column=3, value="笔记数量")
    ws.cell(row=1, column=4, value="下拉词数量")
    ws.cell(row=1, column=5, value="下拉词")
    row = 2

    for obj in objs:
        ws.cell(row=row, column=1, value=row - 1)
        ws.cell(row=row, column=2, value=obj.keywords)
        ws.cell(row=row, column=3, value=obj.biji_num)
        ws.cell(row=row, column=4, value=obj.xialaci_num)

        xialaci_list = [i[0] for i in obj.xiaohongshuxialakeywordschildren_set.values_list('keywords')]
        ws.cell(row=row, column=5, value="\n".join(xialaci_list))
        row += 1
    excel_path = "statics/api_hurong/xiaohongshu_xiala.xlsx"
    wb.save(os.path.abspath(excel_path))

    # 保存覆盖数据
    objs = models.XiaohongshuFugai.objects.filter(status=2)
    wb = Workbook()
    ws = wb.active

    ws.cell(row=1, column=1, value="编号")
    ws.cell(row=1, column=2, value="关键词名称")
    ws.cell(row=1, column=3, value="笔记数量")
    ws.cell(row=1, column=4, value="排名")
    ws.cell(row=1, column=5, value="搜索类型")
    row = 2

    for obj in objs:
        ws.cell(row=row, column=1, value=row - 1)
        ws.cell(row=row, column=2, value=obj.keywords)
        ws.cell(row=row, column=3, value=obj.biji_num)
        ws.cell(row=row, column=4, value=obj.rank)
        ws.cell(row=row, column=5, value=obj.get_select_type_display())

        row += 1
    excel_path = "statics/api_hurong/xiaohongshu_fugai.xlsx"
    wb.save(os.path.abspath(excel_path))



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



@app.task
def debug_test():
    objs = models.XiaohongshuFugai.objects.all()
    for obj in objs:
        now_date = datetime.datetime.now().strftime("%Y-%m-%d")
        objs = models.XiaohongshuFugaiDetail.objects.filter(keywords=obj, create_datetime__gt=now_date)
        if not objs:
            print('obj -->', obj.id, obj.keywords, obj.url, obj.select_type)
