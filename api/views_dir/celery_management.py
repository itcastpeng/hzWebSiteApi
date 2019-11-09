from django.http import HttpResponse
from api import models
from publicFunc.public import send_error_msg
from django.db.models import Q
import datetime, time, random, requests, json
from PIL import Image, ImageFont, ImageDraw
from PIL import Image


# 定时刷新转接 时间是否过期
def time_refresh_whether_connect_time_expired(request):
    objs = models.Transfer.objects.filter(whether_transfer_successful__in=[1, 2])
    for obj in objs:
        if int(obj.timestamp) + 600 < int(time.time()):
            obj.whether_transfer_successful = 3
            obj.save()

    return HttpResponse('1')




def generate_business_card_poster(request):
    qiyemingcheng = '广告公司'
    mingcheng = 'Miss Huang'
    zhiwei = '销售经理'
    dianhua = '13000000000'
    youxiang = 'xxx@.co.m'
    dizhi = 'xxx省xxx市xxx县xxx路xxx号'
    dibu = '长按识别小程序码, 马上认识我'

    im1 = Image.open('1.jpg')
    im2 = Image.open('2.jpg')

    huabu_x = 375  # 画布宽度
    huabu_y = 550  # 画布高度

    # 新建画布纯白色           宽度↓   ↓高度    ↓ 颜色
    p = Image.new('RGBA', (huabu_x, huabu_y), (255, 255, 255))

    # 二维码摆放位置
    qr_suofang_x = 200  # 固定小程序二维码 宽度
    qr_suofang_y = 200  # 固定小程序二维码 高度
    im2 = im2.resize((qr_suofang_x, qr_suofang_y))  # 缩放图片 小程序二维码
    qr_x = int((huabu_x - qr_suofang_x) / 2)  # 画布宽度减去二维码宽度 除二  中间位置 x轴
    qr_y = huabu_y - (qr_suofang_y + 100)  # 画布宽度 减去 (二维码宽度+120) 由下往上反值
    p.paste(im2, (qr_x, qr_y))  # 把缩放的小程序二维码 放到画布上

    # 头像摆放位置
    heading_suofang_x = 65
    heading_suofang_y = 65
    im1 = im1.resize((heading_suofang_x, heading_suofang_y))
    heading_x = huabu_x - (heading_suofang_x + 20)
    heading_y = 20
    p.paste(im1, (heading_x, heading_y))  # 把缩放的 封面 放到画布

    image_draw = ImageDraw.Draw(p)  # 画布对象

    font = ImageFont.truetype('/usr/share/fonts/chinese/simkai.ttf', 18)  # 字体
    heading_font = ImageFont.truetype('/usr/share/fonts/chinese/simsun.ttc', 30)  # 名称 字体

    dibux, dibuy = image_draw.textsize(dibu, font=font)  # 底部字体 长宽
    headingx, headingy = image_draw.textsize(mingcheng, font=heading_font)  # 底部字体 长宽
    image_draw.text((int((huabu_x - dibux) / 2), qr_y + qr_suofang_y + 10), dibu, font=font, fill=(0, 0, 0))

    image_draw.text((15, 20), qiyemingcheng, font=font, fill=(0, 0, 0))
    heading_y = heading_suofang_y + heading_y
    image_draw.text((15, heading_y), mingcheng, font=heading_font, fill=(0, 0, 0))
    image_draw.text((15, heading_y + headingy + 15), zhiwei, font=font, fill=(0, 0, 0))
    image_draw.text((15, heading_y + headingy + 40), dianhua, font=font, fill=(0, 0, 0))
    image_draw.text((15, heading_y + headingy + 60), youxiang, font=font, fill=(0, 0, 0))
    image_draw.text((15, heading_y + headingy + 80), dizhi, font=font, fill=(0, 0, 0))

    p.save('5.png')
    return HttpResponse('1')