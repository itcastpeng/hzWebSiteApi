
from django.conf.urls import url
from hurong.views_dir import upload_img, login, user, task_list, task_info, role, xiaohongshu, xiaohongshuxila, \
    xiaohongshufugai, xhs_phone_log, xiaohongshu_userprofile, xiaohongshu_biji, xiaohongshu_direct_essages


urlpatterns = [

    url(r'^upload_img$', upload_img.upload_img),                  # base64 上传分片
    url(r'^login$', login.login),                  # base64 上传分片

    # 角色管理
    # url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role', role.role),

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
    url(r'^xiaohongshu/check_forbidden_text', xiaohongshu.check_forbidden_text),

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
]
