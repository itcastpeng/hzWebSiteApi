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

    select_type_choices = (
        (1, "综合"),
        (2, "最热"),
        (3, "最新"),
    )
    select_type = models.SmallIntegerField(verbose_name="搜索类型", default=1, choices=select_type_choices)
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


# 小红书手机记录表
class XiaohongshuPhone(models.Model):
    name = models.CharField(verbose_name="手机名称", max_length=256, default="", null=True)
    ip_addr = models.CharField(verbose_name="ip地址", max_length=256, null=True)
    macaddr = models.CharField(verbose_name="mac地址", max_length=256, null=True)
    phone_num = models.CharField(verbose_name="绑定手机号", max_length=256, null=True)

    iccid = models.CharField(verbose_name="SIM卡ID", max_length=128, null=True)
    imsi = models.CharField(verbose_name="设备IMSI号", max_length=128, null=True)

    phone_type_choices = (
        (1, "查覆盖"),
        (2, "任务发布")
    )
    phone_type = models.SmallIntegerField(verbose_name="手机任务类型", choices=phone_type_choices, default=1)

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 小红书手机日志记录
class XiaohongshuPhoneLog(models.Model):
    parent = models.ForeignKey('XiaohongshuPhone', verbose_name="对应手机")
    log_msg = models.TextField(verbose_name="日志信息")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 小红书发布账号管理
class XiaohongshuUserProfile(models.Model):
    phone_id = models.ForeignKey('XiaohongshuPhone', verbose_name="对应手机")
    name = models.CharField(verbose_name="昵称", max_length=128)
    xiaohongshu_id = models.CharField(verbose_name="小红书号", max_length=128)
    home_url = models.CharField(verbose_name="主页地址", max_length=256)


# 小红书账号注册
class XiaohongshuUserProfileRegister(models.Model):
    uid = models.IntegerField(verbose_name="小红书后台博主id")
    name = models.CharField(verbose_name="昵称", max_length=128)
    head_portrait = models.CharField(verbose_name="头像", max_length=128)

    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.SmallIntegerField(verbose_name="性别", choices=gender_choices)
    birthday = models.DateField(verbose_name="生日")
    is_register = models.BooleanField(verbose_name="是否已经注册", default=False)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class XiaohongshuBiji(models.Model):
    user_id = models.ForeignKey('XiaohongshuUserProfile', verbose_name="用户id")
    # img_list = models.TextField(verbose_name="图片链接数组")
    content = models.TextField(verbose_name="笔记内容")

    """
        {
            "img_list": [
                {
                    "url": "图片地址",
                    "tag": {
                        "name": "标签名称",
                        "location": 1,
                    }
                },
                {
                    "url": "图片地址",
                    "tag": {
                        "name": "标签名称",
                        "location": 1,
                    }
                },
            ],
            "content": "笔记内容",
            "@": "@好友名称",
            "topic_name": "话题名称",
            "location": "位置",
        }

        """

    status_choices = (
        (1, "未发布"),
        (2, "已发布")
    )

    status = models.SmallIntegerField(choices=status_choices, verbose_name="笔记状态", default=1)
    release_time = models.DateTimeField(verbose_name="发布时间")
    biji_url = models.CharField(verbose_name="笔记回链", max_length=256, null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 小红书违禁词管理
class XiaohongshuForbiddenText(models.Model):
    word = models.CharField(verbose_name="违禁词", max_length=256)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class XiaohongshuDirectMessages(models.Model):
    user_id = models.ForeignKey('XiaohongshuUserProfile', verbose_name="用户id")
    img_url = models.CharField(verbose_name="私信截图", max_length=256)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)