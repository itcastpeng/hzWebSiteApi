
from django.conf.urls import url, include
from hurong.views_dir import upload_img, login, user, task_list, task_info, role, xiaohongshu, xiaohongshuxila, \
    xiaohongshufugai, xhs_phone_log, xiaohongshu_userprofile, xiaohongshu_biji, xiaohongshu_direct_essages, \
    permissions, xiaohongshu_phone_management, xhs_account_management, xhs_king_barings_screen, \
    xhs_mobile_phone_number_management, package_management, qiniu, equipment_management, registered_account, \
    DMS_screenshots, comment_management, ask_little_red_book, little_red_book_crawler


urlpatterns = [

    url(r'^celery/', include('hurong.celery_url')),     # celery
    url(r'^get_qiniu_token', qiniu.get_upload_token),   # 获取七牛云token
    url(r'^upload_img$', upload_img.upload_img),        # base64 上传分片
    url(r'^login$', login.login),                       # 登录

    # 角色管理
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role', role.role),

    # 权限管理
    url(r'^permissions/(?P<oper_type>\w+)/(?P<o_id>\d+)$', permissions.permissions_oper),
    url(r'^permissions$', permissions.permissions),
    url(r'^get_permissions$', permissions.get_permissions),

    # 用户管理
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user/get_info$', user.get_userinfo),
    url(r'^user', user.user),

    # 任务列表
    url(r'^task_list/(?P<oper_type>\w+)/(?P<o_id>\d+)', task_list.task_list_oper),
    url(r'^task_list', task_list.task_list),

    # 任务详情
    url(r'^task_info', task_info.task_info),

    # 小红书禁词检测
    url(r'^xiaohongshu/check_forbidden_text$', xiaohongshu.check_forbidden_text),
    url(r'^xiaohongshu/(?P<oper_type>\w+)', xiaohongshu.forbidden_words_oper), # 禁词检测


    # 小红书下拉
    url(r'^xiaohongshuxiala/(?P<oper_type>\w+)/(?P<o_id>\d+)', xiaohongshuxila.xiaohongshuxila_oper),
    url(r'^xiaohongshuxiala', xiaohongshuxila.xiaohongshuxila),

    # 小红书覆盖查询
    url(r'^xiaohongshufugai/(?P<oper_type>\w+)/(?P<o_id>\d+)', xiaohongshufugai.xiaohongshufugai_oper),
    url(r'^xiaohongshufugai', xiaohongshufugai.xiaohongshufugai),

    # 小红书手机日志记录
    url(r'^xhs_phone_log/(?P<oper_type>\w+)/(?P<o_id>\d+)', xhs_phone_log.xhs_phone_log_oper),


    # 小红书账号管理
    url(r'^xiaohongshu_userprofile/(?P<oper_type>\w+)/(?P<o_id>\d+)', xiaohongshu_userprofile.xiaohongshu_userprofile_oper),
    # url(r'^xiaohongshu_userprofile', xiaohongshu_userprofile.xiaohongshu_userprofile),

    # 小红书笔记管理
    url(r'^xiaohongshu_biji/(?P<oper_type>\w+)/(?P<o_id>\d+)', xiaohongshu_biji.xiaohongshu_biji_oper),
    url(r'^xiaohongshu_biji', xiaohongshu_biji.xiaohongshu_biji),


    # 小红书私信管理
    url(r'^xiaohongshu_direct_essages/(?P<oper_type>\w+)/(?P<o_id>\d+)', xiaohongshu_direct_essages.xiaohongshu_direct_essages_oper),
    url(r'^xiaohongshu_direct_essages', xiaohongshu_direct_essages.xiaohongshu_direct_essages),

    # 小红书手机 管理
    url(r'^xhs_phone_management/(?P<oper_type>\w+)', xiaohongshu_phone_management.xiaohongshu_phone_management),

    # 小红书发布的账号管理
    url(r'^xhs_account_management/(?P<oper_type>\w+)', xhs_account_management.xhs_account_management),

    # 小红书注册账号管理
    url(r'^registered_account/(?P<oper_type>\w+)', registered_account.registered_account),

    # 小红书 霸屏王 覆盖管理
    url(r'^xhs_king_barings_screen/(?P<oper_type>\w+)', xhs_king_barings_screen.xhs_king_barings_screen),

    # 手机号管理 手机号相关信息(手机短信等)
    url(r'^xhs_mobile_phone_number_management/(?P<oper_type>\w+)', xhs_mobile_phone_number_management.xhs_mobile_phone_number_management),

    # 安装包管理
    url(r'^package_management/(?P<oper_type>\w+)/(?P<o_id>\d+)', package_management.package_management_oper),
    url(r'^package_management$', package_management.package_management),

    # 设备管理 (手机充值信息 和 流量查询)
    url(r'^equipment_management/(?P<oper_type>\w+)/(?P<o_id>\d+)', equipment_management.equipment_management_oper),
    url(r'^equipment_management$', equipment_management.equipment_management),

    # 小红书截图
    url(r'^DMS_screenshots/(?P<oper_type>\w+)', DMS_screenshots.DMS_screenshots),

    # 评论管理
    url(r'^comment_management/(?P<oper_type>\w+)', comment_management.comment_management),

    # 小红书后台请求接口 and 接口请求小红书 日志
    url(r'^ask_little_red_book$', ask_little_red_book.ask_little_red_book),
    url(r'^abnormal_number_columns$', ask_little_red_book.abnormal_number_columns),  # 栏目查询异常数量
    url(r'^query_mobile_equipment$', ask_little_red_book.query_mobile_equipment_alarm_information),  # 移动页面查询 移动设备告警信息

    # 小红书爬虫 操作
    url(r'^little_red_book_crawler/(?P<oper_type>\w+)$', little_red_book_crawler.little_red_book_crawler),

]
