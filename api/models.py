from django.db import models
import json


# Create your models here.


# 用户表
class UserProfile(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=128)
    password = models.CharField(verbose_name="密码", max_length=128)
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


# class UserProfile(models.Model):
#     name = models.CharField(verbose_name="姓名", max_length=128)
#
#     sex_choices = (
#         (1, "男"),
#         (2, "女"),
#     )
#     sex = models.SmallIntegerField(verbose_name="性别", choices=sex_choices)
#     country = models.CharField(verbose_name="国家", max_length=128, null=True, blank=True)
#     province = models.CharField(verbose_name="省份", max_length=128, null=True, blank=True)
#     city = models.CharField(verbose_name="城市", max_length=128, null=True, blank=True)
#
#     phone_number = models.CharField(verbose_name="手机号", max_length=11, null=True, blank=True)
#     signature = models.TextField(verbose_name="个性签名", null=True, blank=True)
#     show_product = models.BooleanField(verbose_name="文章底部是否显示产品", default=True)
#
#     token = models.CharField(verbose_name="token值", max_length=128)
#
#     create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
#     register_date = models.DateField(verbose_name="注册时间", auto_now_add=True)
#     overdue_date = models.DateField(verbose_name="过期时间")
#
#     subscribe = models.BooleanField(verbose_name="是否关注公众号", default=False)
#
#     set_avator = models.CharField(
#         verbose_name='头像',
#         default='http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg',
#         max_length=256
#     )
#
#     qr_code = models.CharField(verbose_name="微信二维码", max_length=256, null=True, blank=True)
#
#     openid = models.CharField(verbose_name="微信公众号openid", max_length=64)
#
#     inviter = models.ForeignKey(
#         'self',
#         verbose_name="邀请人",
#         related_name="userprofile_inviter",
#         null=True,
#         blank=True,
#         default=None
#     )


# 模板表


# 角色表
class Role(models.Model):
    name = models.CharField(verbose_name="模板名称", max_length=256)
    create_user = models.ForeignKey('UserProfile', verbose_name="创建用户", related_name="role_create_user")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 模板表
class Template(models.Model):
    name = models.CharField(verbose_name="模板名称", max_length=256)
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
