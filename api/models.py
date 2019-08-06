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
    password = models.CharField(verbose_name="密码", max_length=128, null=True, blank=True)
    role = models.ForeignKey('Role', verbose_name="角色", null=True)
    token = models.CharField(verbose_name="token值", max_length=128)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
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
    inviter = models.ForeignKey(
        'self',
        verbose_name="邀请人",
        related_name="userprofile_inviter",
        null=True,
        blank=True,
        default=None
    )
    subscribe = models.BooleanField(verbose_name="是否关注公众号", default=False)
    openid = models.CharField(verbose_name="微信公众号openid", max_length=64, null=True, blank=True)
    login_timestamp = models.CharField(verbose_name="登录时间戳", max_length=64, null=True, blank=True)


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
        default="/statics/admin_imgs/logo_70_70.png"
    )
    tab_bar_base_data = {
        "type": "tab_bar",
        "txt": "底部导航",
        "style": {
            'borderStyle': 'solid',         # 顶部边框 solid->实线  dotted->点线  dashed->虚线
            'borderColor': '#d8d8d8',       # 顶部边框颜色
            'borderWidth': 1,               # 顶部边框粗细
            'backgroundColor': '#ffffff',   # 背景颜色
            'color': '#515a6e',             # 文字颜色-未选中
            'selectedColor': '#1296db'       # 文字颜色-选中
        },
        "data": [
            {
                "page_id": None,
                "text": '导航1',
                "icon_path": '/statics/admin_imgs/tabbar/homepage.png',
                "selected_icon_path": '/statics/admin_imgs/tabbar/homepage_selected.png'
            },
            {
                "page_id": None,
                "text": '导航2',
                "icon_path": '/statics/admin_imgs/tabbar/people.png',
                "selected_icon_path": '/statics/admin_imgs/tabbar/people_selected.png'
            }
        ]
    }
    tab_bar_data = models.TextField(verbose_name="底部导航数据", default=json.dumps(tab_bar_base_data))
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户")
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
    data = models.TextField(verbose_name="模板数据", null=True, blank=True)
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 图片库分组
class PhotoLibraryGroup(models.Model):
    name = models.CharField(verbose_name="分组名称", max_length=256)
    parent = models.ForeignKey('self', verbose_name="父级id", null=True)  # 为空表示顶级分组
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", null=True)  # 创建用户为空，表示为系统分组
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 图片库
class PhotoLibrary(models.Model):
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


# 微信三方平台管理
class TripartitePlatform(models.Model):
    appid = models.CharField(verbose_name='三方平台APPID', max_length=64)
    appsecret = models.CharField(verbose_name='三方平台appsecret', max_length=128)
    component_verify_ticket = models.TextField(verbose_name='component_verify_ticket协议')
    component_access_token = models.TextField(verbose_name='component_access_token')
    access_token_time = models.IntegerField(verbose_name='access_token 过期时间')
    linshi = models.TextField(verbose_name='临时', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)


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


# 客户小程序授权 信息
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


# 小程序代码审核上线(代小程序上线)
class GenerationAppletOnline(models.Model):
    small_program = models.ForeignKey('ClientApplet', verbose_name='对应小程序')
    auditid = models.CharField(verbose_name='审核编号', max_length=64)

    status_choices = (
        (1, '已提交审核'),
        (2, '审核成功'),
        (3, '审核失败'),
    )
    status = models.SmallIntegerField(verbose_name='审核状态', choices=status_choices, default=1)
    reason = models.CharField(verbose_name='失败原因', max_length=512, null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 小程序体验者列表
class AppletExperiencerList(models.Model):
    applet = models.ForeignKey('ClientApplet', verbose_name='关联小程序')
    userstr = models.CharField(verbose_name='体验者微信userstr', max_length=256)
    wechat_id = models.CharField(verbose_name='体验者微信ID', max_length=256)
    is_delete = models.BooleanField(verbose_name='是否删除', default=0)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)










