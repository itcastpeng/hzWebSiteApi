
from django.conf.urls import url, include
from api.views_dir import upload_img, login, user, template, page_group, page, wechat, photo_library_group,\
    photo_library, qiniu, compoment_library, compoment_library_class, tripartite_platform, messages_events, permissions, \
    role, template_class, article_management, baidu_tripartite_platform_management, business_card_management, service_management, \
    view_log
from api.views_dir.xcx import template as xcx_template, form_management, business_card_management as xcx_business_card_management

urlpatterns = [

    url(r'^celery/', include('api.celery_url')),     # celery
    # --------------------------- 公共 ----------------------------
    url(r'^upload_img$', upload_img.upload_img),   # 上传图片
    url(r'^login$', login.login),                  # 账号密码登录
    url(r'^wechat_login$', login.wechat_login),    # 微信扫码登录
    url(r'^external_login$', login.external_login),    # 外部登录
    url(r'^qiniu/get_upload_token$', qiniu.get_upload_token),    # 获取七牛云上传token
    url(r'^messages_events/(?P<oper_type>\w+)/(?P<appid>\w+)$', messages_events.messages_events_oper),      # 三方平台操作 消息接收


    # ------------------------ 后台管理 ----------------------
    # 用户管理
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user/get_info$', user.get_userinfo),
    url(r'^user', user.user),

    # 角色管理
    url(r'^role/(?P<oper_type>\w+)/(?P<o_id>\d+)', role.role_oper),
    url(r'^role', role.role),

    # 权限管理
    url(r'^permissions/(?P<oper_type>\w+)/(?P<o_id>\d+)$', permissions.permissions_oper),
    url(r'^permissions$', permissions.permissions),
    url(r'^get_permissions$', permissions.get_permissions),

    # 模板分类管理
    url(r'^template_class/(?P<oper_type>\w+)/(?P<o_id>\d+)', template_class.template_class_oper),
    url(r'^template_class$', template_class.template_class),

    # 模板管理
    url(r'^template/(?P<oper_type>\w+)/(?P<o_id>\d+)', template.template_oper),
    url(r'^template$', template.template),

    # 页面分组管理
    url(r'^page_group/(?P<oper_type>\w+)/(?P<o_id>\d+)', page_group.page_group_oper),
    url(r'^page_group$', page_group.page_group),

    # 页面管理
    url(r'^page/(?P<oper_type>\w+)/(?P<o_id>\d+)', page.page_oper),
    # url(r'^page$', page.page),

    # 图片库分组管理
    url(r'^photo_library_group/(?P<oper_type>\w+)/(?P<o_id>\d+)', photo_library_group.photo_library_group_oper),
    url(r'^photo_library_group$', photo_library_group.photo_library_group),

    # 图片库管理
    url(r'^photo_library/(?P<oper_type>\w+)/(?P<o_id>\d+)', photo_library.photo_library_oper),
    url(r'^photo_library$', photo_library.photo_library),

    # 组件库分类
    url(r'^compoment_library_class/(?P<oper_type>\w+)/(?P<o_id>\d+)', compoment_library_class.compoment_library_class_oper),
    url(r'^compoment_library_class', compoment_library_class.compoment_library_class),

    # 组件库
    url(r'^compoment_library/(?P<oper_type>\w+)/(?P<o_id>\d+)', compoment_library.compoment_library_oper),
    url(r'^compoment_library$', compoment_library.compoment_library),


    # # ----------------------------- 公众号操作 ----------------------------------
    url(r'^wechat/(?P<oper_type>\w+)$', wechat.wechat_oper),
    url(r'^wechat$', wechat.wechat),     # 接受微信服务器发送的请求
    url(r'^set_wechat_column$', wechat.set_wechat_column),     # 设置微信栏目



    # ------------------------------------ 小程序管理 -------------------------------
    url(r'^xcx/login$', login.xcx_login),    # 小程序登录
    url(r'^xcx/template/(?P<oper_type>\w+)$', xcx_template.template),  # 获取页面数据
    url(r'^xcx/business_card_management/(?P<oper_type>\w+)/(?P<o_id>\d+)$', xcx_business_card_management.business_card_management_oper),  # 小程序名片管理

    url(r'^xcx/log/(?P<oper_type>\w+)$', view_log.view_log_oper),  # 获取页面数据


    # ------------------------------------ 表单管理 -------------------------------
    url(r'^xcx/form_management/(?P<oper_type>\w+)/(?P<o_id>\d+)$', form_management.form_management_oper),
    url(r'^xcx/form_management$', form_management.form_management),

    # ------------------------------------ 文章管理 -------------------------------
    url(r'^article_management/(?P<oper_type>\w+)/(?P<o_id>\d+)', article_management.article_management_oper),
    url(r'^article_management$', article_management.article_management),

    # ------------------------------------ 名片管理 -------------------------------
    url(r'^business_card_management/(?P<oper_type>\w+)/(?P<o_id>\d+)', business_card_management.business_card_management_oper),
    url(r'^business_card_management$', business_card_management.business_card_management),

    # ------------------------------------ 服务管理 -------------------------------
    url(r'^service_management/(?P<oper_type>\w+)/(?P<o_id>\d+)', service_management.service_management_oper),
    url(r'^service_management$', service_management.service_management),

    # ---------------------------- 微信三方平台管理 -------------------------------
    url(r'^tripartite_platform/(?P<oper_type>\w+)$', tripartite_platform.tripartite_platform_oper),
    url(r'^tripartite_platform$', tripartite_platform.tongzhi),  # 微信通知
    url(r'^authorize_callback$', tripartite_platform.authorize_callback),  # 用户确认 同意授权 回调(用户点击授权 or 扫码授权后 跳转)

    # ---------------------------- 微信小程序管理 --------------------------------
    url(r'^tripartite_platform/(?P<oper_type>\w+)/(?P<o_id>\d+)$', tripartite_platform.tripartite_platform_admin),

    # ---------------------------- 百度三方平台管理 -------------------------------
    url(r'^baidu_platform_management/(?P<oper_type>\w+)$', baidu_tripartite_platform_management.tripartite_platform_oper),
    url(r'^baidu_platform_management$', baidu_tripartite_platform_management.baidu_tongzhi), # 百度通知
    url(r'^baidu_authorize_callback$', baidu_tripartite_platform_management.authorize_callback),  # 用户确认 同意授权 回调(用户点击授权 or 扫码授权后 跳转)

    # ---------------------------- 百度小程序管理 --------------------------------
    url(r'^baidu_platform_management/(?P<oper_type>\w+)/(?P<o_id>\d+)$', baidu_tripartite_platform_management.baidu_platform_management_admin),

    # ----------------------------- 查看日志 -------------------------------------
    url(r'^view_log/(?P<oper_type>\w+)$', view_log.view_log_oper),  # 用户确认 同意授权 回调(用户点击授权 or 扫码授权后 跳转)


]















