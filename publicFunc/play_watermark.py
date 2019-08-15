
from PIL import Image,ImageFont,ImageDraw
from publicFunc.account import randon_str
import os


# 图片打水印
class watermark():
    def __init__(self, data):
        self.data = data
        self.img_path = data.get('img_path')
        self.name = data.get('name')
        self.phone = data.get('phone')


    # 海报水印
    def posters_play_watermark(self):
        image = Image.open(self.img_path).convert('RGBA')

        # 绘图句柄
        image_draw = ImageDraw.Draw(image)

        posters_status = int(self.data.get('posters_status'))  # 水印类型

        text = str(self.name) + ' ' + str(self.phone)

        # 正能量海报水印
        if posters_status == 1:
            font = ImageFont.truetype('/usr/share/fonts/chinese/SIMSUN.TTC', 15)  # 使用自定义的字体，第二个参数表示字符大小
            # 文字rgb颜色
            rgb_color = (0, 0, 0)
            set_avator = self.data.get('set_avator')
            # 获取文本大小
            text_size_x, text_size_y = image_draw.textsize(text, font=font)

            # 获取文字位置
            x = int((image.size[0] - text_size_x) / 2)  # 文字左右放在居中位置
            y = int(image.size[1] - text_size_y - 20)  # 文字距底20像素

            # 设置文本位置及颜色和透明度
            image_draw.text((x, y), text, font=font, fill=rgb_color)

            # -------------------头像--------------------------
            set_avator = Image.open(set_avator)

            left = int(set_avator.size[0] / 2 - 15)
            right = int(set_avator.size[0] / 2 + 15)
            top = int(set_avator.size[1] / 2 - 15)
            end = int(set_avator.size[1] / 2 + 15)
            cropped = set_avator.crop((left, top, right, end))  # 截取该图片

            # 头像右侧减去左侧 剩下的值为头像宽 x轴减去图片宽 减五距右侧五像素
            image.paste(cropped, (x - (right - left) - 2, y - (int((end - top - text_size_y) / 2))))

        # 邀请函海报水印
        else:
            zhu_title = self.data.get('zhu_title')
            fu_title = self.data.get('fu_title')
            time = self.data.get('time')
            place = self.data.get('place')

            gbk_color = (0, 0, 0)

            text = '详询:' + text

            zhu_title_font = ImageFont.truetype('/usr/share/fonts/chinese/SIMHEI.TTF', 20)  # 使用自定义的字体，第二个参数表示字符大小
            font = ImageFont.truetype('/usr/share/fonts/chinese/SIMHEI.TTF', 15)

            zhu_title_x, zhu_title_y = image_draw.textsize(zhu_title, font=zhu_title_font)
            fu_title_x, fu_title_y = image_draw.textsize(fu_title, font=font)
            time_x, time_y = image_draw.textsize(time, font=font)
            place_x, place_y = image_draw.textsize(place, font=font)
            text_x, text_y = image_draw.textsize(text, font=font)

            zhu_title_width = int(image.size[0] / 2 - (zhu_title_x / 2))
            fu_title_width = int(image.size[0] / 2 - (fu_title_x / 2))
            time_width = int(image.size[0] / 2 - (time_x / 2))
            place_width = int(image.size[0] / 2 - (place_x / 2))
            text_width = int(image.size[0] / 2 - (text_x / 2))

            img_hight = image.size[1]
            image_draw.text((zhu_title_width, img_hight-180), zhu_title, font=zhu_title_font, fill=gbk_color)
            image_draw.text((fu_title_width, img_hight-140), fu_title, font=font, fill=gbk_color)
            image_draw.text((time_width, img_hight-110), time, font=font, fill=gbk_color)
            image_draw.text((place_width, img_hight-80), place, font=font, fill=gbk_color)
            image_draw.text((text_width, img_hight-40), text, font=font, fill=gbk_color)

        path = os.path.join('statics', 'img', randon_str() + '.png')
        image.save(path)
        return path

if __name__ == '__main__':
    img_path = '1.jpg'
    set_avator = '2.png'

    zhu_title = '峰会主席邀请会'
    fu_title = '期待诸位亲临现场'
    time = '2019年8月11日 上午11点'
    place = '北京one大厦23层'


    data = {
        'posters_status': 2,
        'img_path': img_path,
        'name': '微商天眼',
        'phone': 188888888,
        'set_avator': set_avator,

        'zhu_title': zhu_title,
        'fu_title': fu_title,
        'time': time,
        'place': place,
    }
    obj = watermark(data)
    poster_path = '1.jpg'
    logo_path = 'tianyan_logo.png'
    # obj.test(poster_path)
    obj.posters_play_watermark()






