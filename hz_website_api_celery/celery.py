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

    # 每分钟执行一次
    'xiaohongshu_xiala_update_data': {
        'task': 'hz_website_api_celery.tasks.xiaohongshu_xiala_update_data',
        'schedule': 60                                   # 单独设置  秒
        # 'schedule': crontab(hour=8, minute=30),
        # 'schedule': crontab('*', '*', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
    },

    # 每2秒执行一次
    'xiaohongshu_fugai_update_data': {
        'task': 'hz_website_api_celery.tasks.xiaohongshu_fugai_update_data',
        'schedule': 30                                   # 单独设置  秒
        # 'schedule': crontab(hour=8, minute=30),
        # 'schedule': crontab('*', '*', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
    },

    # 每10分钟执行一次
    'xiaohongshu_shengcheng_baobiao': {
        'task': 'hz_website_api_celery.tasks.xiaohongshu_shengcheng_baobiao',
        # 'schedule': 2                                   # 单独设置  秒
        # 'schedule': crontab(hour=8, minute=30),
        'schedule': crontab('*/10', '*', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
    },
    'xiaohongshu_phone_monitor':{
        'task':'hz_website_api_celery.tasks.xiaohongshu_phone_monitor',
        'schedule': crontab('*/2', '*', '*', '*', '*'),
    },
    'xiaohongshu_userprofile_register_monitor': {
        'task': 'hz_website_api_celery.tasks.xiaohongshu_userprofile_register_monitor',
        'schedule': crontab('*/5', '*', '*', '*', '*'),
    },
    'xiaohongshu_biji_monitor': {
        'task': 'hz_website_api_celery.tasks.xiaohongshu_biji_monitor',
        'schedule': crontab('*/5', '*', '*', '*', '*'),
    },

    'xhs_bpw_keywords_rsync': {
        'task': 'hz_website_api_celery.tasks.xhs_bpw_keywords_rsync',
        'schedule': crontab('*/30', '*', '*', '*', '*'),
    },

    'xhs_bpw_keywords_fugai_rsync': {
        'task': 'hz_website_api_celery.tasks.xhs_bpw_keywords_fugai_rsync',
        'schedule': crontab('*/10', '*', '*', '*', '*'),
    },
    #
    # # 自动合并gitlab代码，每分钟一次
    # 'merge_project_code':{
    #     'task':'projectmanage_celery.tasks.merge_project_code',
    #     # 'schedule':30                                   # 单独设置  秒
    #     # 'schedule': crontab(hour=8, minute=30),
    #     'schedule': crontab('*/1', '*', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
    # },

    # 定时删除设备日志 保留近三天 (每天12点执行一次)
    'delete_phone_log': {
        'task': 'hz_website_api_celery.tasks.delete_phone_log',
        'schedule': crontab('0', '0', '*', '*', '*'),
    },

    # 获取 手机号短信
    'celery_get_phone_content': {
        'task': 'hz_website_api_celery.tasks.celery_get_phone_content',
        'schedule': crontab('*/30', '*', '*', '*', '*'),
    },

    # 获取 设备流量信息
    'get_traffic_information':{
        'task': 'hz_website_api_celery.tasks.get_traffic_information',
        'schedule': crontab('0', '*/5', '*', '*', '*'),
    },

    # 异步上传手机抓取的评论（一小时执行一次）
    'error_asynchronous_transfer_data':{
        'task': 'hz_website_api_celery.tasks.error_asynchronous_transfer_data',
        'schedule': crontab('0', '*/1', '*', '*', '*'),
    },

    #  异步 同步 日记反链 （一小时一次）
    'asynchronous_synchronous_trans':{
        'task': 'hz_website_api_celery.tasks.asynchronous_synchronous_trans',
        'schedule': crontab('0', '*/1', '*', '*', '*'),
    },

    # 手机号 未使用的低于200 告警(一小时一次)
    'unused_cell_phone_number_below_alarms':{
        'task': 'hz_website_api_celery.tasks.unused_cell_phone_number_below_alarms',
        'schedule': crontab('0', '*/1', '*', '*', '*'),
    },

    # celery任务过多告警
    'celery_task_toomuch_alarm': {
        'task': 'hz_website_api_celery.tasks.celery_task_toomuch_alarm',
        'schedule': crontab('0', '*/1', '*', '*', '*'),
    },
}
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
