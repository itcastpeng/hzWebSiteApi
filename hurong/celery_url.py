

from django.conf.urls import url, include
from hurong.views_dir import celery_management
urlpatterns = [
    # 定期删除 手机日志 (保留最近三天数据)
    url(r'^delete_phone_log$', celery_management.delete_phone_log),

    # 更新手机号短信
    url(r'^celery_get_phone_content$', celery_management.celery_get_phone_content),

    # 查询 设备 流量信息 和 设备充值记录
    url(r'^get_traffic_information$', celery_management.get_traffic_information),



]
