

from django.conf.urls import url, include
from hurong.views_dir import celery_management
urlpatterns = [

    # 定期删除 手机日志 (保留最近三天数据)
    url(r'^delete_phone_log', celery_management.delete_phone_log),

    # url(r'^delete_phone_log/(?P<oper_type>\w+)', celery_management.delete_phone_log),

]
