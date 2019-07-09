from django.db import models

# Create your models here.

# 角色表
class Role(models.Model):
    name = models.CharField(verbose_name="角色", max_length=128)
    # access_name = models.CharField(verbose_name="角色对应权限名", max_length=128)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('UserProfile', verbose_name='创建人', null=True)
    permissions = models.ManyToManyField('Permissions', verbose_name="拥有权限")

# 权限表
class Permissions(models.Model):
    name = models.CharField(verbose_name="权限名称", max_length=128)
    title = models.CharField(verbose_name="权限标题", max_length=128)
    pid = models.ForeignKey('self', verbose_name="父级权限", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('UserProfile', verbose_name="创建用户", related_name='permissions_user', null=True, blank=True)

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

    is_debug = models.BooleanField(verbose_name="是否调试", default=True)

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
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    xhs_version = models.CharField(max_length=64, verbose_name='小红书版本号', null=True)
    # screenshot_time = models.CharField(verbose_name="私信截图时间(单位:分钟)", max_length=128, default={"first_time":"20", "last_time":"120"}) # 早上8点 - 晚10点
    screenshot_time = models.SmallIntegerField(verbose_name="私信截图时间(单位:分钟)", default=20) # 早上8点 - 晚10点
    late_screenshot_time = models.SmallIntegerField(verbose_name="私信截图时间(单位:分钟)", default=120) # 晚上10点 - 早8点


# 小红书账号注册
class XiaohongshuUserProfileRegister(models.Model):
    uid = models.IntegerField(verbose_name="小红书后台博主id")
    name = models.CharField(verbose_name="昵称", max_length=128)
    head_portrait = models.CharField(verbose_name="头像", max_length=256)

    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.SmallIntegerField(verbose_name="性别", choices=gender_choices)
    birthday = models.DateField(verbose_name="生日")
    is_register = models.BooleanField(verbose_name="是否已经注册", default=False)
    register_datetime = models.DateTimeField(verbose_name="注册时间", null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 小红书笔记
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
        (1, "发布中"),
        (2, "已发布"),
        (3, "待审核"),
    )

    status = models.SmallIntegerField(choices=status_choices, verbose_name="笔记状态", default=3)
    release_time = models.DateTimeField(verbose_name="发布时间")
    completion_time = models.DateTimeField(verbose_name="完成时间", null=True)
    biji_existing_url = models.CharField(verbose_name="笔记真实回链", max_length=256, null=True)
    biji_url = models.CharField(verbose_name="笔记回链", max_length=256, null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 小红书违禁词管理
class XiaohongshuForbiddenText(models.Model):
    word = models.CharField(verbose_name="违禁词", max_length=256)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 小红书 提交违禁词 平台统计
class XiaohongshuBannedWordsPlatform(models.Model):
    platform_name = models.CharField(verbose_name='平台名称', max_length=256)
    submit_num = models.IntegerField(verbose_name='提交次数', default=1)
    create_date = models.DateField(verbose_name='统计时间', auto_now_add=True)

# 小红书私信截图
class XiaohongshuDirectMessages(models.Model):
    user_id = models.ForeignKey('XiaohongshuUserProfile', verbose_name="用户id")
    name = models.CharField(verbose_name="私信用户的名称", max_length=256)
    img_url = models.CharField(verbose_name="私信截图", max_length=256)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 小红书私信回复
class XiaohongshuDirectMessagesReply(models.Model):
    user_id = models.ForeignKey('XiaohongshuUserProfile', verbose_name="用户id")
    name = models.CharField(verbose_name="私信用户的名称", max_length=256)
    msg = models.CharField(verbose_name="回复的内容", max_length=256)
    status_choices = (
        (1, "等待回复"),
        (2, "回复成功"),
    )
    status = models.SmallIntegerField(verbose_name="回复状态", choices=status_choices, default=1)
    update_datetime = models.DateTimeField(verbose_name="回复时间", null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 手机号管理
class PhoneNumber(models.Model):
    phone_num = models.CharField(verbose_name="手机号", max_length=256)
    expire_date = models.DateField(verbose_name="过期时间")
    remark = models.CharField(verbose_name="备注信息", max_length=256)

    status_choices = (
        (1, "未使用"),
        (2, "已使用"),
    )
    status = models.SmallIntegerField(verbose_name="状态", default=1)
    phone = models.ForeignKey('XiaohongshuPhone', verbose_name='哪个手机使用', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 小红书霸屏王关键词管理
class xhs_bpw_keywords(models.Model):
    keywords = models.CharField(verbose_name="搜索词", max_length=256)
    uid = models.IntegerField(verbose_name="小红书后台用户id")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_datetime = models.DateTimeField(verbose_name="更新时间", null=True, blank=True)


# 小红书霸屏王笔记链接管理
class xhs_bpw_biji_url(models.Model):
    biji_url = models.CharField(verbose_name="笔记链接", max_length=256)
    uid = models.IntegerField(verbose_name="小红书后台用户id")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_datetime = models.DateTimeField(verbose_name="更新时间", null=True, blank=True)


# 小红书霸屏王关键词覆盖表
class xhs_bpw_fugai(models.Model):
    keywords = models.ForeignKey("xhs_bpw_keywords", verbose_name="关键词")
    biji_url = models.ForeignKey("xhs_bpw_biji_url", verbose_name="笔记链接")
    rank = models.IntegerField(verbose_name="排名", default=0)
    biji_num = models.IntegerField(verbose_name="笔记数", default=0)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 手机号接收的短信
class text_messages_received_cell_phone_number(models.Model):
    phone = models.ForeignKey('PhoneNumber', verbose_name='哪个手机号')
    message_content = models.CharField(verbose_name='短信内容', max_length=256)
    receiving_time = models.DateTimeField(verbose_name='接收短信时间', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    serial_number = models.CharField(verbose_name="流水号", max_length=128, null=True)

# 安装包表 (聪哥用)
class InstallationPackage(models.Model):
    package_type_choices = (
        (1, '小红书发布'),
        (2, '小红书覆盖')
    )
    package_type = models.SmallIntegerField(verbose_name='安装包类型', choices=package_type_choices, default=1)
    package_name = models.CharField(verbose_name='安装包名称', max_length=32)
    package_path = models.CharField(verbose_name='安装包地址', max_length=1024)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    oper_user = models.ForeignKey('UserProfile', verbose_name="操作人")
    is_delete = models.BooleanField(verbose_name="是否删除", default=0)

# 手机流量信息表
class MobileTrafficInformation(models.Model):
    select_number = models.TextField(verbose_name='查询号码') # 可以是手机号 也可以是 ismi号
    cardnumber = models.CharField(verbose_name='卡号', max_length=64, null=True) # 手机号
    cardbaldata = models.CharField(validators='剩余流量', max_length=16, null=True)
    cardimsi = models.CharField(verbose_name='ISMI号', max_length=64, null=True)
    cardno = models.CharField(verbose_name='卡编号', max_length=64, null=True)
    cardstatus = models.CharField(verbose_name='用户状态', max_length=64, null=True)
    cardtype = models.CharField(verbose_name='套餐类型', max_length=32, null=True)
    cardusedata = models.CharField(verbose_name='已用流量', max_length=16, null=True)
    cardstartdate = models.DateTimeField(verbose_name='卡开户时间', null=True)
    cardenddate = models.DateTimeField(verbose_name='卡到期时间', null=True)
    errmsg = models.CharField(verbose_name='错误日志', max_length=256, null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 移动设备充值记录
class MobilePhoneRechargeInformation(models.Model):
    equipment_package = models.CharField(verbose_name='设备套餐', max_length=128)
    prepaid_phone_time = models.DateTimeField(verbose_name='充值时间')
    equipment = models.ForeignKey('MobileTrafficInformation', verbose_name='设备')
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 对外requests请求 参数 结果 记录
class externalRequestRecord(models.Model):
    request_parameters = models.TextField(verbose_name='请求参数')
    request_url = models.CharField(verbose_name='请求链接', max_length=512)
    response_content = models.TextField(verbose_name='响应数据')
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 评论表
class littleRedBookReviewForm(models.Model):
    xhs_user = models.ForeignKey('XiaohongshuUserProfile', verbose_name='小红书账号')
    head_portrait = models.CharField(verbose_name='头像', max_length=256)
    nick_name = models.CharField(verbose_name='昵称', max_length=128)
    comments_choices = (
        (1, '默认评论'),
        (2, '回复评论')
    )
    comments_status = models.SmallIntegerField(verbose_name='评论类型', choices=comments_choices, default=1)
    comments_content = models.TextField(verbose_name='评论内容')
    article_picture_address = models.CharField(verbose_name='文章图片地址', max_length=512)
    screenshots_address = models.CharField(verbose_name='截图地址', max_length=512, null=True)
    article_notes = models.ForeignKey('XiaohongshuBiji', verbose_name='文章笔记', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 评论回复表
class commentResponseForm(models.Model):
    comment = models.ForeignKey('littleRedBookReviewForm', verbose_name='回复哪个评论')
    comment_response = models.TextField(verbose_name='回复评论内容')
    comment_completion_time = models.DateTimeField(verbose_name='评论完成时间', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 笔记 文章截图 关联表
class noteAssociationScreenshot(models.Model):
    screenshots = models.CharField(verbose_name='截图', max_length=256)
    notes = models.ForeignKey('XiaohongshuBiji', verbose_name='截图')
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)



# 查询是否关联
# 关联  biji_url 文章截图 返回 笔记ID

# 创建评论 传递 笔记ID