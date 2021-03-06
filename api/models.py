from django.db import models
import json


# 权限表
class Permissions(models.Model):
    name = models.CharField(verbose_name="权限名称", max_length=128)
    title = models.CharField(verbose_name="权限标题", max_length=128)
    pid = models.ForeignKey('self', verbose_name="父级权限", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('UserProfile', verbose_name="创建用户", related_name='permissions_user', null=True, blank=True)


# 角色表
class Role(models.Model):
    name = models.CharField(verbose_name="模板名称", max_length=256)
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", related_name="role_create_user")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    permissions = models.ManyToManyField('Permissions', verbose_name="拥有权限")


# 用户表
class UserProfile(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=128, null=True, blank=True)
    name = models.CharField(verbose_name="微信昵称", max_length=128, null=True, blank=True)
    company_name = models.CharField(verbose_name="公司名称", max_length=256, null=True, blank=True)
    password = models.CharField(verbose_name="密码", max_length=128, null=True, blank=True)
    role = models.ForeignKey('Role', verbose_name="角色", null=True)
    token = models.CharField(verbose_name="token值", max_length=128)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_login_datetime = models.DateTimeField(verbose_name="最后登录时间", null=True, blank=True)
    head_portrait = models.CharField(
        verbose_name='头像',
        default='/statics/admin_imgs/head_portrait.jpg',
        max_length=256
    )

    # name = models.CharField(verbose_name="姓名", max_length=128)
    is_update_pwd = models.BooleanField(verbose_name="是否修改密码", default=False)

    sex_choices = (
        (1, "男"),
        (2, "女"),
    )
    sex = models.SmallIntegerField(verbose_name="性别", choices=sex_choices, null=True, blank=True)
    country = models.CharField(verbose_name="国家", max_length=128, null=True, blank=True)
    province = models.CharField(verbose_name="省份", max_length=128, null=True, blank=True)
    city = models.CharField(verbose_name="城市", max_length=128, null=True, blank=True)
    subscribe = models.BooleanField(verbose_name="是否关注公众号", default=False)
    openid = models.CharField(verbose_name="微信公众号openid", max_length=64, null=True, blank=True)
    login_timestamp = models.CharField(verbose_name="登录时间戳", max_length=64, null=True, blank=True)

    inviter = models.ForeignKey(
        'self',
        verbose_name="父账户",
        related_name="userprofile_inviter",
        null=True,
        blank=True,
        default=None
    )
    number_child_users = models.IntegerField(verbose_name='可以创建几个子用户', default=1)
    small_program_number = models.IntegerField(verbose_name='可以创建几个小程序', default=1)
    login_type_choices = (
        (1, '微信扫码登录'),
        (2, '叮咚营销宝'),
    )
    login_type = models.SmallIntegerField(verbose_name='登录类型', choices=login_type_choices, default=1)
    ding_dong_marketing_treasure_user_id = models.IntegerField(verbose_name='叮咚营销宝', null=True)
    select_template_list = models.TextField(verbose_name='可查看模板ID列表', default=[])
    remark = models.TextField(verbose_name="备注信息", null=True, blank=True)





# 公众号或小程序用户表
class ClientUserProfile(models.Model):
    openid = models.CharField(verbose_name="微信公众号openid", max_length=64)
    session_key = models.CharField(verbose_name="微信公众号openid", max_length=64)
    token = models.CharField(verbose_name="token值", max_length=128)
    name = models.CharField(verbose_name="微信昵称", max_length=128, null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    head_portrait = models.CharField(
        verbose_name='头像',
        default='/statics/admin_imgs/head_portrait.jpg',
        max_length=256
    )

    sex_choices = (
        (1, "男"),
        (2, "女"),
    )
    sex = models.SmallIntegerField(verbose_name="性别", choices=sex_choices, null=True, blank=True)
    country = models.CharField(verbose_name="国家", max_length=128, null=True, blank=True)
    province = models.CharField(verbose_name="省份", max_length=128, null=True, blank=True)
    city = models.CharField(verbose_name="城市", max_length=128, null=True, blank=True)
    login_timestamp = models.CharField(verbose_name="登录时间戳", max_length=64, null=True, blank=True)

    user_type_choices = (
        (1, "公众号用户"),
        (2, "小程序用户"),
    )
    user_type = models.SmallIntegerField(verbose_name="用户类型", choices=user_type_choices)


# 模板分类表
class TemplateClass(models.Model):
    name = models.CharField(verbose_name="模板分类名称", max_length=256)

    class_type_choices = (
        (1, "单页模板"),
        (2, "多页模板"),
    )
    class_type = models.SmallIntegerField(verbose_name="分类类型", choices=class_type_choices, default=2)
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 模板表
class Template(models.Model):
    name = models.CharField(verbose_name="模板名称", max_length=256)
    template_class = models.ForeignKey('TemplateClass', verbose_name="模板分类", null=True)
    share_qr_code = models.CharField(verbose_name="微信分享二维码", max_length=256, null=True, blank=True)
    logo_img = models.CharField(
        verbose_name="logo图片",
        max_length=256,
        default="/statics/admin_imgs/logo_img.png"
    )

    tab_bar_data = models.TextField(verbose_name="底部导航数据(正式)", null=True)
    tab_bar_data_dev = models.TextField(verbose_name="底部导航数据(设计)", null=True)
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户")
    thumbnail = models.CharField(verbose_name='缩略图', max_length=256, null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    expire_datetime = models.DateTimeField(verbose_name="到期时间", null=True)
    qrcode = models.CharField(verbose_name='体验二维码H5页面', max_length=512, null=True)
    xcx_qrcode = models.CharField(verbose_name='体验二维码小程序', max_length=512, null=True)
    baidu_xcx_qrcode = models.CharField(verbose_name='体验二维码百度小程序', max_length=512, null=True)
    common_components = models.TextField(verbose_name='公用组件', default='')
    # ----------------------------------名片数据---------------------------------------
    enterprise_name = models.CharField(verbose_name='企业名称', max_length=64, null=True)

    # ----------------------------------模板记录日志 触发场景---------------------------# 是否触发日志
    card_details_choices = (
        (1, '不触发'),
        (2, '引导授权'),
        (3, '强制授权'),
    )
    name_card_details = models.SmallIntegerField(verbose_name='进入名片详情', choices=card_details_choices, default=1)
    name_save_address_book = models.SmallIntegerField(verbose_name='保存通讯录', choices=card_details_choices, default=1)
    name_make_phone_call = models.SmallIntegerField(verbose_name='拨打电话', choices=card_details_choices, default=1)
    name_my = models.SmallIntegerField(verbose_name='我的', choices=card_details_choices, default=1)
    name_article_details = models.SmallIntegerField(verbose_name='文章详情', choices=card_details_choices, default=1)
    name_service_details = models.SmallIntegerField(verbose_name='服务详情', choices=card_details_choices, default=1)
    name_share_page = models.SmallIntegerField(verbose_name='分享页面', choices=card_details_choices, default=1)

    phone_card_details = models.SmallIntegerField(verbose_name='进入名片详情', choices=card_details_choices, default=1)
    phone_save_address_book = models.SmallIntegerField(verbose_name='保存通讯录', choices=card_details_choices, default=1)
    phone_make_phone_call = models.SmallIntegerField(verbose_name='拨打电话', choices=card_details_choices, default=1)
    phone_my = models.SmallIntegerField(verbose_name='我的', choices=card_details_choices, default=1)
    phone_article_details = models.SmallIntegerField(verbose_name='文章详情', choices=card_details_choices, default=1)
    phone_service_details = models.SmallIntegerField(verbose_name='服务详情', choices=card_details_choices, default=1)
    phone_submit_form = models.SmallIntegerField(verbose_name='提交表单', choices=card_details_choices, default=1)
    phone_submit_article = models.SmallIntegerField(verbose_name='提交文章', choices=card_details_choices, default=1)
    phone_submit_service_order = models.SmallIntegerField(verbose_name='提交服务订单', choices=card_details_choices, default=1)
    phone_vote = models.SmallIntegerField(verbose_name='投票', choices=card_details_choices, default=1)
    phone_share_page = models.SmallIntegerField(verbose_name='分享页面', choices=card_details_choices, default=1)


# 表单管理
class Form(models.Model):
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户")
    template = models.ForeignKey('Template', verbose_name="模板", null=True)
    data = models.TextField(verbose_name="表单数据,数据结构前端自己定义")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 页面分组表
class PageGroup(models.Model):
    name = models.CharField(verbose_name="分组名称", max_length=256)
    template = models.ForeignKey('Template', verbose_name="所属模板")
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 页面表
class Page(models.Model):
    name = models.CharField(verbose_name="页面名称", max_length=256)
    page_group = models.ForeignKey('PageGroup', verbose_name="所属模板")
    data = models.TextField(verbose_name="页面数据(正式)", null=True, blank=True)
    data_dev = models.TextField(verbose_name="页面数据(设计)", null=True, blank=True)
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 图片库分组
class PhotoLibraryGroup(models.Model):
    template = models.ForeignKey('Template', verbose_name='对应模板', null=True)
    name = models.CharField(verbose_name="分组名称", max_length=256)
    parent = models.ForeignKey('self', verbose_name="父级id", null=True)  # 为空表示顶级分组
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", null=True)  # 创建用户为空，表示为系统分组
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 图片库
class PhotoLibrary(models.Model):
    template = models.ForeignKey('Template', verbose_name='对应模板', null=True)
    img_url = models.CharField(verbose_name="图片地址", max_length=256)
    group = models.ForeignKey('PhotoLibraryGroup', verbose_name="所属分组", null=True)
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", null=True)  # 创建用户为空，表示为系统分组
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 组件库分类
class CompomentLibraryClass(models.Model):
    name = models.CharField(verbose_name="组件分类名称", max_length=256, null=True)
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 组件库
class CompomentLibrary(models.Model):
    name = models.CharField(verbose_name="组件名称", max_length=256, null=True)
    compoment_library_class = models.ForeignKey('CompomentLibraryClass', verbose_name="组件分类")
    data = models.TextField(verbose_name="组件对应渲染到页面的数据")
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    is_delete = models.BooleanField(verbose_name="是否删除", default=False)


# 消息通知
class MessageInform(models.Model):
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", null=True)
    msg = models.TextField(verbose_name="通知消息")
    status = models.BooleanField(verbose_name="查阅状态", default=False)
    is_send = models.BooleanField(verbose_name="是否发送微信公众号模板消息通知", default=False)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


""" 建站表单 数据表 """

# 预约表单 表
class ReservationForm(models.Model):
    template = models.ForeignKey('Template', verbose_name='对应模板')
    form = models.ForeignKey('Form', verbose_name='表单', null=True)
    form_content = models.TextField(verbose_name='表单数据', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 文章分类表
class ArticleClass(models.Model):
    template = models.ForeignKey('Template', verbose_name='对应模板')
    name = models.CharField(verbose_name="分类名称", max_length=256, null=True)
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 文章表
class Article(models.Model):
    template = models.ForeignKey('Template', verbose_name='对应模板')
    article_class = models.ForeignKey('ArticleClass', verbose_name="文章分类", null=True, blank=True)
    article_title = models.CharField(verbose_name='文章标题', max_length=512, null=True)
    article_introduction = models.CharField(verbose_name='文章简介', max_length=512, null=True)
    thumbnail = models.CharField(verbose_name='缩略图', max_length=512, null=True)
    article_content = models.TextField(verbose_name='文章内容')
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 名片 表
class BusinessCard(models.Model):
    name = models.CharField(verbose_name='姓名', max_length=64, null=True)
    phone = models.CharField(verbose_name='电话', max_length=64, null=True)
    jobs = models.CharField(verbose_name='岗位', max_length=128, null=True)
    email = models.CharField(verbose_name='邮箱', max_length=128, null=True)
    wechat_num = models.CharField(verbose_name='微信号', max_length=128, null=True)
    address = models.CharField(verbose_name='地址', max_length=128, null=True)
    heading = models.CharField(verbose_name='头像', max_length=256, null=True)
    about_me = models.TextField(verbose_name='关于我', null=True)
    create_user = models.ForeignKey('UserProfile', verbose_name='创建人', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    template = models.ForeignKey('Template', verbose_name='模板', null=True)
    card_poster = models.CharField(verbose_name='海报图片', max_length=256, null=True)


# 服务 表
class ServiceTable(models.Model):
    name = models.CharField(verbose_name='名称', max_length=64, null=True)
    abstract = models.CharField(verbose_name='摘要', max_length=128, null=True)
    main_figure = models.CharField(verbose_name='主图', max_length=256, null=True)
    service_classification = models.CharField(verbose_name='服务分类', max_length=128, null=True)
    price_type_choices = (
        (1, '默认'),
        (2, '免费'),
        (3, '面议'),
    )
    price_type = models.SmallIntegerField(verbose_name='价格类型', choices=price_type_choices, default=1)
    price = models.CharField(verbose_name='价格', max_length=128, null=True)
    promotion_price = models.CharField(verbose_name='促销价格', max_length=128, null=True)
    limit_amount = models.IntegerField(verbose_name='限制总量', default=0)
    virtual_order_volume = models.IntegerField(verbose_name='虚拟订单量', default=0)
    create_user = models.ForeignKey('UserProfile', verbose_name='创建人', null=True)
    service_detail = models.TextField(verbose_name='服务详情', null=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


""" 转接 数据表 """

# 转接表(用户--转接--用户)
class Transfer(models.Model): # 可定时删除
    speak_to_people = models.ForeignKey('UserProfile', verbose_name='转接人', related_name='speak_to_people_name')
    by_connecting_people = models.ForeignKey('UserProfile', verbose_name='被转接人', related_name='by_connecting_people_name', null=True)
    timestamp = models.CharField(verbose_name='时间戳', max_length=128)
    whether_transfer_successful_choices = (
        (1, '未扫码'),
        (2, '已扫码'),
        (3, '已过期'),
        (4, '已完成'),
        (5, '已拒绝'),
    )
    whether_transfer_successful = models.SmallIntegerField(verbose_name='是否转接成功', choices=whether_transfer_successful_choices, default=1)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 邀请子级记录表
class InviteTheChild(models.Model):
    parent = models.ForeignKey('UserProfile', verbose_name='父级', related_name='parent_name')
    child = models.ForeignKey('UserProfile', verbose_name='子级', related_name='child_name', null=True)
    timestamp = models.CharField(verbose_name='时间戳', max_length=128)
    whether_transfer_successful_choices = (
        (1, '未扫码'),
        (2, '已扫码'),
        (3, '已过期'),
        (4, '已完成'),
        (5, '已拒绝'),
    )
    whether_transfer_successful = models.SmallIntegerField(verbose_name='是否邀请完成',
        choices=whether_transfer_successful_choices, default=1)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


""" 三方平台 数据表 """

# 微信三方平台管理
class TripartitePlatform(models.Model):
    appid = models.CharField(verbose_name='三方平台APPID', max_length=64)
    appsecret = models.CharField(verbose_name='三方平台appsecret', max_length=128)
    component_verify_ticket = models.TextField(verbose_name='component_verify_ticket协议')
    component_access_token = models.TextField(verbose_name='component_access_token')
    access_token_time = models.IntegerField(verbose_name='access_token 过期时间')
    linshi = models.TextField(verbose_name='临时', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)

# 百度三方平台管理
class BaiduTripartitePlatformManagement(models.Model):
    appid = models.CharField(verbose_name='三方平台APPID', max_length=64)
    ticket = models.TextField(verbose_name='ticket协议')
    access_token = models.TextField(verbose_name='access_token')
    access_token_time = models.IntegerField(verbose_name='access_token 过期时间', default=0) # 默认一个月
    pre_auth_code = models.CharField(verbose_name='预授权码', max_length=128)
    pre_auth_code_time = models.IntegerField(verbose_name='access_token 过期时间', default=0) # 默认20分钟
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)


""" 客户平台 授权表 """

# 客户公众号授权 信息
class CustomerOfficialNumber(models.Model):
    is_authorization = models.IntegerField(verbose_name='授权是否完成', default=0)
    appid = models.CharField(verbose_name='公众号APPID', max_length=64)

    auth_code = models.CharField(verbose_name='授权码', max_length=512, null=True)
    auth_code_expires_in = models.IntegerField(verbose_name='授权码 过期时间', null=True)


    authorizer_access_token = models.CharField(verbose_name='接口凭证 (令牌)', max_length=512, null=True)
    authorizer_access_token_expires_in = models.IntegerField(verbose_name='令牌过期时间', null=True)
    authorizer_refresh_token = models.CharField(verbose_name='接口调用刷新凭证', max_length=512, null=True)

    nick_name = models.CharField(verbose_name='授权方昵称', max_length=32, null=True)
    head_img = models.CharField(verbose_name='授权方头像', max_length=256, null=True)
    original_id = models.CharField(verbose_name="原始ID", max_length=64, null=True)
    qrcode_url = models.CharField(verbose_name='二维码', max_length=256, null=True)
    user = models.ForeignKey('UserProfile', verbose_name='用户', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 客户小程序授权 信息(微信小程序)
class ClientApplet(models.Model):
    is_authorization = models.IntegerField(verbose_name='授权是否完成', default=0)
    appid = models.CharField(verbose_name='小程序APPID', max_length=64)

    auth_code = models.CharField(verbose_name='授权码', max_length=512, null=True)
    auth_code_expires_in = models.IntegerField(verbose_name='授权码 过期时间', null=True)

    authorizer_access_token = models.CharField(verbose_name='接口凭证 (令牌)', max_length=512, null=True)
    authorizer_access_token_expires_in = models.IntegerField(verbose_name='令牌过期时间', null=True)
    authorizer_refresh_token = models.CharField(verbose_name='接口调用刷新凭证', max_length=512, null=True)

    nick_name = models.CharField(verbose_name='授权方昵称', max_length=32, null=True)
    head_img = models.CharField(verbose_name='授权方头像', max_length=256, null=True)
    original_id = models.CharField(verbose_name="原始ID", max_length=64, null=True)
    qrcode_url = models.CharField(verbose_name='二维码', max_length=256, null=True)
    user = models.ForeignKey('UserProfile', verbose_name='用户', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    template = models.ForeignKey('Template', verbose_name='对应模板', null=True)

# 百度小程序管理
class BaiduSmallProgramManagement(models.Model):
    appid = models.CharField(verbose_name='小程序APPID', max_length=64)
    program_name = models.CharField(verbose_name='小程序名称', max_length=64, null=True)
    app_key = models.CharField(verbose_name='小程序的key', max_length=128, null=True)
    app_desc = models.CharField(verbose_name='小程序的介绍内容', max_length=128, null=True)
    photo_addr = models.CharField(verbose_name='小程序图标', max_length=256, null=True)
    access_token = models.TextField(verbose_name='access_token', null=True)
    refresh_token = models.TextField(verbose_name='refresh_token', null=True) # 接口调用凭据刷新令牌，有效期10年，使用后失效
    access_token_time = models.IntegerField(verbose_name='access_token 过期时间', default=0)  # 默认一个月
    user = models.ForeignKey('UserProfile', verbose_name='用户', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    template = models.ForeignKey('Template', verbose_name='对应模板', null=True)

# 小程序保存代码版本页面数据 （预览用）
class AppletCodeVersion(models.Model):
    applet = models.ForeignKey('ClientApplet', verbose_name='关联小程序')
    navigation_data = models.TextField(verbose_name='导航数据', null=True)
    page_data = models.TextField(verbose_name='页面数据', null=True)
    user_desc = models.TextField(verbose_name='备注', null=True)
    user_version = models.CharField(verbose_name='代码版本号', max_length=128, null=True)
    auditid = models.CharField(verbose_name='审核提交代码编号', max_length=128, null=True)
    choices_status = (
        (2, '审核中'),
        (0, '审核成功'),
        (1, '审核失败'),
        (3, '发布成功')
    )
    status = models.SmallIntegerField(verbose_name='审核状态', default=2, choices=choices_status)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 小程序体验者列表
class AppletExperiencerList(models.Model):
    applet = models.ForeignKey('ClientApplet', verbose_name='关联小程序')
    userstr = models.CharField(verbose_name='体验者微信userstr', max_length=256)
    wechat_id = models.CharField(verbose_name='体验者微信ID', max_length=256)
    is_delete = models.BooleanField(verbose_name='是否删除', default=0)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 客户登录信息
class Customer(models.Model):
    head_portrait = models.CharField(verbose_name='头像', max_length=256, null=True)
    sex_choices = (
        (1, "男"),
        (2, "女"),
    )
    sex = models.SmallIntegerField(verbose_name="性别", choices=sex_choices, null=True, blank=True)
    name = models.CharField(verbose_name="名称", max_length=128, blank=True)
    country = models.CharField(verbose_name="国家", max_length=128, null=True, blank=True)
    province = models.CharField(verbose_name="省份", max_length=128, null=True, blank=True)
    city = models.CharField(verbose_name="城市", max_length=128, null=True, blank=True)
    subscribe = models.BooleanField(verbose_name="是否关注公众号", default=False)
    openid = models.CharField(verbose_name="微信公众号openid", max_length=64, null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    token = models.CharField(verbose_name="token值", max_length=128, null=True)
    phone = models.CharField(verbose_name='手机号', max_length=20, blank=True, null=True)
    session_key = models.TextField(verbose_name='session_key', null=True)
    ip_address = models.CharField(verbose_name='IP地址', max_length=64, null=True)
    user_type_choices = (
        (1, '微信小程序'),
        (2, '微信公众号'),
        (3, '百度小程序'),
    )
    user_type = models.SmallIntegerField(verbose_name='用户类型', choices=user_type_choices, default=1)

# 查看小程序信息
class ViewCustomerSmallApplet(models.Model):
    customer = models.ForeignKey('Customer', verbose_name='客户', null=True)
    client_applet = models.ForeignKey('ClientApplet', verbose_name='查看的微信小程序', null=True)
    baidu_client_applet = models.ForeignKey('BaiduSmallProgramManagement', verbose_name='查看的百度小程序', null=True)
    template = models.ForeignKey('Template', verbose_name='模板', null=True)
    source_choices = (
        (1, '微信小程序'),
        (2, '百度小程序')
    )
    source = models.SmallIntegerField(verbose_name='客户来源', choices=source_choices, default=1)
    log_type_choices = (
        (1, '查看小程序'),
        (2, '进入名片详情'),
        (3, '保存通讯录'),
        (4, '拨打电话'),
        (5, '我的'),
        (6, '文章详情'),
        (7, '服务详情'),
        (9, '提交表单'),
        (10, '提交文章'),
        (11, '提交服务订单'),
        (12, '投票'),
        (13, '分享页面'),
    )
    log_type = models.SmallIntegerField(verbose_name='日志类型', choices=log_type_choices, default=1)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)






