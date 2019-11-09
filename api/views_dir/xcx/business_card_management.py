from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.xcx.business_card_management import SelectForm
from PIL import Image, ImageFont, ImageDraw
from PIL import Image
from publicFunc.public import upload_qiniu, requests_img_download
import json, time, os



# @account.is_token(models.Customer)
def business_card_management_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        pass


    else:

        # 查询名片
        if oper_type == 'get_data':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_date')
                field_dict = {
                    'id': '',
                }
                q = conditionCom(request, field_dict)
                print('q -->', q)
                objs = models.BusinessCard.objects.filter(q).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                # 返回的数据
                ret_data = []

                for obj in objs:
                    ret_data.append({
                        'id': obj.id,
                        'create_user_id': obj.create_user_id,
                        'name': obj.name,  # 名称
                        'phone': obj.phone,  # 电话
                        'jobs': obj.jobs,  # 职位
                        'email': obj.email,  # 邮箱
                        'wechat_num': obj.wechat_num,  # 微信号
                        'address': obj.address,  # 地址
                        'heading': obj.heading,  # 头像
                        'about_me': obj.about_me,  # 关于我
                        'card_poster': obj.card_poster,  # 海报
                        'enterprise_name': obj.template.enterprise_name,  # 关于我
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }
                response.note = {
                    'id': '名片ID',
                    'create_user_id': '创建人ID',
                    'name': '名称',
                    'phone': '电话',
                    'jobs': '职位',
                    'email': '邮箱',
                    'wechat_num': '微信号',
                    'address': '地址',
                    'heading': '头像',
                    'card_poster': '海报',
                    'about_me': '关于我',
                    'create_date': '创建时间',
                }

        # # 名片海报
        # elif oper_type == 'get_card_poster':
            # obj = models.BusinessCard.objects.get(id=o_id)
            #
            # enterprise_name = obj.template.enterprise_name  # 企业名称
            # name = obj.name                                 # 名称
            # jobs = obj.jobs                                 # 职位
            # phone = obj.phone                               # 电话
            # email = obj.email                               # 邮箱
            # address = obj.address                           # 地址
            # dibu = '长按识别小程序码, 马上认识我'
            #
            # heading_path = requests_img_download(obj.heading) # 下载头像
            # im1 = Image.open(heading_path)
            # im2 = Image.open('2.jpg')
            #
            # huabu_x = 375  # 画布宽度
            # huabu_y = 550  # 画布高度
            #
            # # 新建画布纯白色           宽度↓   ↓高度    ↓ 颜色
            # p = Image.new('RGBA', (huabu_x, huabu_y), (255, 255, 255))
            #
            # # 二维码摆放位置
            # qr_suofang_x = 200  # 固定小程序二维码 宽度
            # qr_suofang_y = 200  # 固定小程序二维码 高度
            # im2 = im2.resize((qr_suofang_x, qr_suofang_y))  # 缩放图片 小程序二维码
            # qr_x = int((huabu_x - qr_suofang_x) / 2)  # 画布宽度减去二维码宽度 除二  中间位置 x轴
            # qr_y = huabu_y - (qr_suofang_y + 100)  # 画布宽度 减去 (二维码宽度+120) 由下往上反值
            # p.paste(im2, (qr_x, qr_y))  # 把缩放的小程序二维码 放到画布上
            #
            # # 头像摆放位置
            # heading_suofang_x = 65
            # heading_suofang_y = 65
            # im1 = im1.resize((heading_suofang_x, heading_suofang_y))
            # heading_x = huabu_x - (heading_suofang_x + 20)
            # heading_y = 20
            # p.paste(im1, (heading_x, heading_y))  # 把缩放的 封面 放到画布
            #
            # image_draw = ImageDraw.Draw(p)  # 画布对象
            #
            # # font = ImageFont.truetype('/usr/share/fonts/chinese/simkai.ttf', 18)  # 字体
            # # heading_font = ImageFont.truetype('/usr/share/fonts/chinese/simsun.ttc', 30)  # 名称 字体
            # font = ImageFont.truetype('/usr/share/fonts/chinese/SIMKAI.TTF', 18)  # 字体
            # heading_font = ImageFont.truetype('/usr/share/fonts/chinese/SIMSUN.TTC', 30)  # 名称 字体
            #
            # dibux, dibuy = image_draw.textsize(dibu, font=font)  # 底部字体 长宽
            # headingx, headingy = image_draw.textsize(name, font=heading_font)  # 底部字体 长宽
            # image_draw.text((int((huabu_x - dibux) / 2), qr_y + qr_suofang_y + 10), dibu, font=font, fill=(0, 0, 0))
            #
            # image_draw.text((15, 20), enterprise_name, font=font, fill=(0, 0, 0))
            # heading_y = heading_suofang_y + heading_y
            # image_draw.text((15, heading_y), name, font=heading_font, fill=(0, 0, 0))
            # image_draw.text((15, heading_y + headingy + 15), jobs, font=font, fill=(0, 0, 0))
            # image_draw.text((15, heading_y + headingy + 40), phone, font=font, fill=(0, 0, 0))
            # image_draw.text((15, heading_y + headingy + 60), email, font=font, fill=(0, 0, 0))
            # image_draw.text((15, heading_y + headingy + 80), address, font=font, fill=(0, 0, 0))
            #
            # key = str(int(time.time())) + '.png'
            # p.save(key)
            # path = upload_qiniu(key, 500)
            # obj.card_poster = path
            # obj.save()
            # if os.path.exists(heading_path):
            #     os.remove(heading_path)  # 删除本地图片
            # response.code = 200
            # response.msg = '完成'


        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
