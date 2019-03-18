from django.db import models

# Create your models here.


class UserProfile(models.Model):
    name = models.CharField(verbose_name="姓名", max_length=128)

    sex_choices = (
        (1, "男"),
        (2, "女"),
    )
    sex = models.SmallIntegerField(verbose_name="性别", choices=sex_choices)
    country = models.CharField(verbose_name="国家", max_length=128, null=True, blank=True)
    province = models.CharField(verbose_name="省份", max_length=128, null=True, blank=True)
    city = models.CharField(verbose_name="城市", max_length=128, null=True, blank=True)

    phone_number = models.CharField(verbose_name="手机号", max_length=11, null=True, blank=True)
    signature = models.TextField(verbose_name="个性签名", null=True, blank=True)
    show_product = models.BooleanField(verbose_name="文章底部是否显示产品", default=True)

    token = models.CharField(verbose_name="token值", max_length=128)

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    register_date = models.DateField(verbose_name="注册时间", auto_now_add=True)
    overdue_date = models.DateField(verbose_name="过期时间")

    subscribe = models.BooleanField(verbose_name="是否关注公众号", default=False)

    set_avator = models.CharField(
        verbose_name='头像',
        default='http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg',
        max_length=256
    )

    qr_code = models.CharField(verbose_name="微信二维码", max_length=256, null=True, blank=True)

    openid = models.CharField(verbose_name="微信公众号openid", max_length=64)

    inviter = models.ForeignKey(
        'self',
        verbose_name="邀请人",
        related_name="userprofile_inviter",
        null=True,
        blank=True,
        default=None
    )

