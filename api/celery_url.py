

from django.conf.urls import url
from api.views_dir import celery_management
urlpatterns = [
    # 定时刷新转接 时间是否过期
    url(r'^time_refresh_switch$', celery_management.time_refresh_whether_connect_time_expired),

    # 异步生成海报名片
    url(r'^generate_business_card_poster$', celery_management.generate_business_card_poster),
]
