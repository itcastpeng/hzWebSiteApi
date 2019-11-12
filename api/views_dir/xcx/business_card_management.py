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
                    enterprise_name = ''
                    if obj.template:
                        enterprise_name = obj.template.enterprise_name
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
                        'enterprise_name': enterprise_name,  # 关于我
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

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
