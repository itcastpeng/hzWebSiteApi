from django.http import HttpResponse
from api import models
from publicFunc.public import send_error_msg
from django.db.models import Q
import datetime, time, random, requests, json
from PIL import Image, ImageFont, ImageDraw
from PIL import Image
from publicFunc.public import upload_qiniu, requests_img_download
import os
from publicFunc.weixin import weixin_gongzhonghao_api


# 定时刷新转接 时间是否过期
def time_refresh_whether_connect_time_expired(request):
    objs = models.Transfer.objects.filter(whether_transfer_successful__in=[1, 2])
    for obj in objs:
        if int(obj.timestamp) + 600 < int(time.time()):
            obj.whether_transfer_successful = 3
            obj.save()

    return HttpResponse('1')




def generate_business_card_poster(request):
    card_id = request.GET.get('card_id')
    obj = models.BusinessCard.objects.get(id=card_id)

    enterprise_name = obj.template.enterprise_name  # 企业名称
    name = obj.name  # 名称
    jobs = obj.jobs  # 职位
    phone = obj.phone  # 电话
    email = obj.email  # 邮箱
    address = obj.address  # 地址
    dibu = '长按识别小程序码, 马上认识我'

    heading_path = requests_img_download(obj.heading)  # 下载头像
    im1 = Image.open(heading_path)
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

    font = ImageFont.truetype('/usr/share/fonts/chinese/SIMKAI.TTF', 18)  # 字体
    heading_font = ImageFont.truetype('/usr/share/fonts/chinese/SIMSUN.TTC', 30)  # 名称 字体

    dibux, dibuy = image_draw.textsize(dibu, font=font)  # 底部字体 长宽
    headingx, headingy = image_draw.textsize(name, font=heading_font)  # 底部字体 长宽
    image_draw.text((int((huabu_x - dibux) / 2), qr_y + qr_suofang_y + 10), dibu, font=font, fill=(0, 0, 0))

    image_draw.text((15, 20), enterprise_name, font=font, fill=(0, 0, 0))
    heading_y = heading_suofang_y + heading_y
    image_draw.text((15, heading_y), name, font=heading_font, fill=(0, 0, 0))
    image_draw.text((15, heading_y + headingy + 15), jobs, font=font, fill=(0, 0, 0))
    image_draw.text((15, heading_y + headingy + 40), phone, font=font, fill=(0, 0, 0))
    image_draw.text((15, heading_y + headingy + 60), email, font=font, fill=(0, 0, 0))
    image_draw.text((15, heading_y + headingy + 80), address, font=font, fill=(0, 0, 0))

    key = str(int(time.time())) + '.png'
    p.save(key)
    path = upload_qiniu(key, 500)
    obj.card_poster = path
    obj.save()
    if os.path.exists(heading_path):
        os.remove(heading_path)  # 删除本地图片


    return HttpResponse('1')


# 发送微信公众号模板消息
def send_wechat_msg(request):
    wechat_api_obj = weixin_gongzhonghao_api.WeChatApi()
    objs = models.MessageInform.objects.select_related('create_user').filter(is_send=False)

    for obj in objs:
        post_data = {
            "touser": obj.create_user.openid,
            "template_id": "Tn107ZLaOMdfc3TIV3R2WFG846IH4ztf1DezkgnLwI0",
            # "url": "http://wenda.zhugeyingxiao.com/",
            "data": {
                # "first": {
                #     "value": obj.msg,
                #     # "color": "#173177"
                # },
                "keyword1": {
                    "value": obj.msg,
                    # "color": "#173177"
                },
                "keyword2": {
                    "value": obj.create_datetime.strftime("%y-%m-%d %H:%M:%S"),
                    # "color": "#173177"
                },
                # "keyword3": {
                #     "value": "发布失败",
                #     "color": "#173177"
                # },
                # "keyword4": {
                #     "value": "请修改",
                #     "color": "#173177"
                # },
                # "remark": {
                #     "value": "问题:嘻嘻嘻\n答案:嘻嘻嘻",
                #     "color": "#173177"
                # }
            }
        }
        wechat_api_obj.sendTempMsg(post_data)

        obj.is_send = True
        obj.save()
