from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.xcx.business_card_management import SelectForm
from PIL import Image, ImageFont, ImageDraw
from PIL import Image
from publicFunc.public import upload_qiniu
import json, time



# @account.is_token(models.Customer)
def business_card_management_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        pass


    else:
        # 名片海报
        if oper_type == 'get_card_poster':
            card_id = request.GET.get('card_id')
            obj = models.BusinessCard.objects.get(id=card_id)

            enterprise_name = obj.template.enterprise_name  # 企业名称
            name = obj.name                                 # 名称
            jobs = obj.jobs                                 # 职位
            phone = obj.phone                               # 电话
            email = obj.email                               # 邮箱
            address = obj.address                           # 地址
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
            response.code = 200
            response.msg = '完成'
        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
