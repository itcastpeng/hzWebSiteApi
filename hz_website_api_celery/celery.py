#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

from __future__ import absolute_import, unicode_literals
# from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

app = Celery(
    broker='redis://redis:6379/15',
    backend='redis://redis:6379/15',
    include=['hz_website_api_celery.tasks'],

)
# app.conf.enable_utc = False
# app.conf.timezone = "Asia/Shanghai"
# CELERYD_FORCE_EXECV = True           # 非常重要,有些情况下可以防止死锁
# CELERYD_MAX_TASKS_PER_CHILD = 100    # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
app.conf.beat_schedule = {

    # 每分钟执行一次
    'hurong_send_email': {
        'task': 'hz_website_api_celery.tasks.hurong_send_email',
        # 'schedule':30                                   # 单独设置  秒
        # 'schedule': crontab(hour=8, minute=30),
        'schedule': crontab('*', '*', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
    },

    # 'automatic_test':{
    #     'task':'projectmanage_celery.tasks.automatic_test',
    #     'schedule': crontab(minute=1),
    # },
    #
    # # 自动合并gitlab代码，每分钟一次
    # 'merge_project_code':{
    #     'task':'projectmanage_celery.tasks.merge_project_code',
    #     # 'schedule':30                                   # 单独设置  秒
    #     # 'schedule': crontab(hour=8, minute=30),
    #     'schedule': crontab('*/1', '*', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
    # },

}
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
