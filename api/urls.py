
from django.conf.urls import url
from api.views_dir import upload_img, login, user, template, page_group, page, wechat
from api.views_dir.xcx import template as xcx_template


urlpatterns = [


    url(r'^upload_img$', upload_img.upload_img),   # 上传图片
    url(r'^login$', login.login),                  # 账号密码登录
    url(r'^wechat_login$', login.wechat_login),    # 微信扫码登录

    # ------------------ 后台管理 ------------------
    # 用户管理
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user/get_info$', user.get_userinfo),
    url(r'^user', user.user),

    # 模板管理
    url(r'^template/(?P<oper_type>\w+)/(?P<o_id>\d+)', template.template_oper),
    url(r'^template$', template.template),

    # 页面分组管理
    url(r'^page_group/(?P<oper_type>\w+)/(?P<o_id>\d+)', page_group.page_group_oper),
    url(r'^page_group$', page_group.page_group),

    # 页面管理
    url(r'^page/(?P<oper_type>\w+)/(?P<o_id>\d+)', page.page_oper),
    # url(r'^page$', page.page),

    # # ---------------- 公众号操作 ----------------
    url(r'^wechat/(?P<oper_type>\w+)$', wechat.wechat_oper),
    url(r'^wechat$', wechat.wechat),     # 接受微信服务器发送的请求
    # # url(r'^weichat_generate_qrcode$', wechat.weichat_generate_qrcode),    # 微信获取带参数的二维码

    # ------------------ 小程序管理 ------------------
    url(r'^xcx/login$', login.xcx_login),    # 小程序登录
    url(r'^xcx/template/(?P<oper_type>\w+)$', xcx_template.template),  # 获取页面数据

    # ------------------ 微信三方平台管理 ------------------

]
