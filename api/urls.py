
from django.conf.urls import url
from api.views_dir import upload_img, login, user, template, page_group, page, wechat, photo_library_group,\
    photo_library, qiniu, compoment_library, compoment_library_class
from api.views_dir.xcx import template as xcx_template


urlpatterns = [


    url(r'^upload_img$', upload_img.upload_img),   # 上传图片
    url(r'^login$', login.login),                  # 账号密码登录
    url(r'^wechat_login$', login.wechat_login),    # 微信扫码登录
    url(r'^qiniu/get_upload_token$', qiniu.get_upload_token),    # 获取七牛云上传token


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

    # # ---------------- 公众号操作 ----------------
    url(r'^wechat/(?P<oper_type>\w+)$', wechat.wechat_oper),
    url(r'^wechat$', wechat.wechat),     # 接受微信服务器发送的请求
    # # url(r'^weichat_generate_qrcode$', wechat.weichat_generate_qrcode),    # 微信获取带参数的二维码

    # ------------------ 小程序管理 ------------------
    url(r'^xcx/login$', login.xcx_login),    # 小程序登录
    url(r'^xcx/template/(?P<oper_type>\w+)$', xcx_template.template),  # 获取页面数据

    # ------------------ 微信三方平台管理 ------------------

]
