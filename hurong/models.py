from django.db import models

# Create your models here.


class Role(models.Model):
    name = models.CharField(verbose_name="角色", max_length=128)
    access_name = models.CharField(verbose_name="角色对应权限名", max_length=128)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 用户表
class UserProfile(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=128)
    password = models.CharField(verbose_name="密码", max_length=128)
    role_id = models.ForeignKey("Role", verbose_name="对应角色", null=True, blank=True)
    token = models.CharField(verbose_name="token值", max_length=128, null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    head_portrait = models.CharField(
        verbose_name='头像',
        default='/statics/admin_imgs/head_portrait.jpg',
        max_length=256
    )
    status_choices = (
        (1, "启用"),
        (2, "不启用"),
        (3, "禁用"),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    # name = models.CharField(verbose_name="姓名", max_length=128)
    is_update_pwd = models.BooleanField(verbose_name="是否修改密码", default=False)
    create_user = models.ForeignKey("UserProfile", verbose_name="添加任务的人", null=True, blank=True)


# 邮箱账户表
class EmailUserInfo(models.Model):
    email_user = models.CharField(verbose_name="邮箱账户", max_length=256)
    email_pwd = models.CharField(verbose_name="邮箱密码", max_length=256)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    use_number = models.SmallIntegerField(verbose_name="使用次数", default=0)
    is_available = models.BooleanField(verbose_name="是否可用", default=True)


# 任务列表
class TaskList(models.Model):
    name = models.CharField(verbose_name="任务名称", max_length=256)
    percentage_progress = models.SmallIntegerField(verbose_name="完成百分比", default=0)
    send_email_title = models.TextField(verbose_name="发送邮件标题")
    send_email_content = models.TextField(verbose_name="发送邮件内容")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    create_user = models.ForeignKey("UserProfile", verbose_name="添加任务的人")
    is_delete = models.BooleanField(verbose_name="是否删除", default=False)
    delete_user = models.ForeignKey(
        "UserProfile",
        verbose_name="添加任务的人",
        related_name='task_list_dekete_user',
        null=True,
        blank=True
    )
    status_choices = (
        (1, "等待操作"),
        (2, "操作中"),
        (3, "操作完成"),
        (4, "手动完成"),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)


# 任务详情
class TaskInfo(models.Model):
    to_email = models.CharField(verbose_name="发送给谁", max_length=256)
    status_choices = (
        (1, "等待发送"),
        (2, "发送成功"),
        (3, "发送失败"),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    send_num = models.SmallIntegerField(verbose_name="发送次数", default=1)
    task_list = models.ForeignKey('TaskList', verbose_name="属于哪个任务列表")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 小红书下拉词管理
class XiaohongshuXiaLaKeywords(models.Model):
    keywords = models.CharField(verbose_name="搜索词", max_length=128)
    status_choices = (
        (1, "查询中"),
        (2, "已查询"),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    biji_num = models.CharField(verbose_name="笔记数", max_length=128, null=True, blank=True)
    xialaci_num = models.CharField(verbose_name="下拉词数", max_length=128, null=True, blank=True)
    create_user = models.ForeignKey("UserProfile", verbose_name="添加任务的人")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_datetime = models.DateTimeField(verbose_name="更新时间", null=True, blank=True)


# 小红书下拉词数据管理
class XiaohongshuXiaLaKeywordsChildren(models.Model):
    parent = models.ForeignKey("XiaohongshuXiaLaKeywords", verbose_name="搜索词")
    keywords = models.CharField(verbose_name="搜索词", max_length=128)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 小红书查覆盖
class XiaohongshuFugai(models.Model):
    keywords = models.CharField(verbose_name="搜索词", max_length=256)
    url = models.CharField(verbose_name="匹配链接", max_length=256)
    status_choices = (
        (1, "查询中"),
        (2, "已查询"),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    rank = models.IntegerField(verbose_name="排名", default=0)
    biji_num = models.IntegerField(verbose_name="笔记数", default=0)
    is_shoulu = models.BooleanField(verbose_name="是否收录", default=False)
    create_user = models.ForeignKey("UserProfile", verbose_name="添加任务的人")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_datetime = models.DateTimeField(verbose_name="更新时间", null=True, blank=True)


# 小红书查覆盖详细
class XiaohongshuFugaiDetail(models.Model):
    keywords = models.ForeignKey('XiaohongshuFugai', verbose_name="任务词")
    rank = models.IntegerField(verbose_name="排名", default=0)
    biji_num = models.IntegerField(verbose_name="笔记数", default=0)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_datetime = models.DateTimeField(verbose_name="更新时间", null=True, blank=True)
