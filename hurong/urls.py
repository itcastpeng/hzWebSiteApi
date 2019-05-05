
from django.conf.urls import url
from hurong.views_dir import upload_img, login, user, task_list, task_info, role, xiaohongshu, xiaohongshuxila, xiaohongshufugai


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

]
