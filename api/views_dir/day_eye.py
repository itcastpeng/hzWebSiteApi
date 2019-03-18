# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.day_eye import SelectForm, AddForm, UpdateForm
from django.db.models import Count
from publicFunc.base64_encryption import b64decode, b64encode
import json
import datetime


# 放入开始和结束时间 返回 天 时 分 秒
def get_min_s(start_time=None, stop_time=None, ms=None):
    date_time = stop_time - start_time
    day = date_time.days
    hour, date_time = divmod(date_time.seconds, 3600)
    min, date_time = divmod(date_time, 60)
    second = date_time

    days = ''
    hours = ''
    mins = ''
    seconds = ''
    if day:
        days = str(day) + '天'
    if hour:
        hours = str(hour) + '小时'
    if min:
        mins = str(min) + '分钟'
        if second:
            mins = str(min) + '分'
    if second:
        seconds = str(second) + '秒'
    if ms:
        return days + hours
    else:
        return days + hours + mins + seconds


# cerf  token验证 谁看了我(列表)
@account.is_token(models.Userprofile)
def day_eye(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            user_id = forms_obj.cleaned_data['user_id']

            objs = models.SelectArticleLog.objects.filter(
                inviter_id=user_id
            ).select_related(
                'customer'
            ).values(
                'customer_id', 'customer__name', 'customer__set_avator'
            ).distinct().annotate(Count('customer_id'))

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
            count = objs.count()

            # 返回的数据
            ret_data = []
            for obj in objs:
                customer_id = obj.get('customer_id')
                article_count = models.SelectArticleLog.objects.filter(
                    customer_id=customer_id,
                    inviter_id=user_id,
                ).values('article_id').distinct().count()

                ret_data.append({
                    'customer_id': customer_id,
                    'customer__name': b64decode(obj.get('customer__name')),
                    'customer__set_avator': obj.get('customer__set_avator'),
                    'customer_id__count': obj.get('customer_id__count'),    # 总共查看几次
                    'article_count': article_count,                         # 总共查看几篇文章
                })

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'count': count,
            }
            response.note = {
                'customer_id': "查看人ID",
                'customer__name': "查看人姓名",
                'customer_id__count': '总共查看几次',
                'article_count': '总共查看几篇文章',
                'customer__set_avator': '客户头像',
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.Userprofile)
def day_eye_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_datetime')
        if request.method == "POST":
            form_data = {
                'o_id': o_id,
                'user_id': user_id,
                'customer_id': request.POST.get('customer_id'),
                'remote_type': request.POST.get('remote_type'),
                'title': request.POST.get('title'),
                'create_date': request.POST.get('create_date'),
                'remote': request.POST.get('remote')
            }

            # 添加客户信息备注
            if oper_type == "add":
                form_obj = AddForm(form_data)
                if form_obj.is_valid():
                    remote_type = form_obj.cleaned_data.get('remote_type')
                    title = form_obj.cleaned_data.get('title')
                    remote = form_obj.cleaned_data.get('remote')
                    customer_id = form_obj.cleaned_data.get('customer_id')
                    create_date = form_obj.cleaned_data.get('create_date')

                    remote_text = {
                        'create_date': create_date,
                        'title': title,
                        'remote': remote
                    }

                    data = {
                        'user_id': user_id,
                        'customer_id': customer_id,
                        'remote_type': remote_type,
                        'remote': remote_text
                    }
                    models.customer_information_the_user.objects.create(**data)
                    response.code = 200
                    response.msg = '保存成功'

                else:
                    response.code = 301
                    response.msg = json.loads(form_obj.errors.as_json())

            # 修改客户信息备注
            elif oper_type == 'update':
                form_obj = UpdateForm(form_data)
                if form_obj.is_valid():
                    o_id, remote_type = form_obj.cleaned_data.get('o_id')
                    title = form_obj.cleaned_data.get('title')
                    remote = form_obj.cleaned_data.get('remote')
                    create_date = form_obj.cleaned_data.get('create_date')
                    remote_text = {
                        'create_date': create_date,
                        'title': title,
                        'remote': remote
                    }

                    models.customer_information_the_user.objects.filter(id=o_id).update(
                        remote=remote_text
                    )
                    response.code = 200
                    response.msg = '保存成功'

                else:
                    response.code = 301
                    response.msg = json.loads(form_obj.errors.as_json())

            # 删除客户信息备注
            elif oper_type == 'delete':
                customer_id = request.POST.get('customer_id')
                print(user_id,customer_id)
                if customer_id:
                    objs = models.customer_information_the_user.objects.filter(
                        user_id=user_id,
                        customer_id=customer_id
                    )
                else:
                    objs = models.customer_information_the_user.objects.filter(id=o_id)
                print('user-----> ', objs)
                if not objs:
                    response.code = 301
                    response.msg = '刪除数据不存在'
                else:
                    objs.delete()
                    response.code = 200
                    response.msg = '删除成功'


            # 添加客户资料
            elif oper_type == 'add_customer_info':
                pass

            # 修改客户资料
            elif oper_type == 'update_customer_info':
                customer_info = request.POST.get('customer_info')
                objs = models.user_comments_customer_information.objects.filter(
                    user_id=user_id,
                    customer_id=o_id
                )

                if objs:
                    objs.update(customer_info=customer_info)
                else:
                    objs.create(
                        customer_info=customer_info,
                        user_id=user_id,
                        customer_id=o_id
                    )
                response.code = 200
                response.msg = '保存成功'
                response.note = {
                    'customer_info':'用户所有信息',
                    'customer_sex': '用户性别 默认微信性别',
                    'customer_set_avator': '用户头像 默认微信头像',
                    'customer_name': '用户姓名 备注 默认微信名称',
                    'customer_wechat': '用户微信名称',
                    'customer_phone': '用户电话',
                    'customer_professional': '用户职业',
                    'customer_birthday': '用户生日',
                    'customer_remake': '用户备注',
                    'customer_demand': '用户需求',
                    'customer_label': {
                        'xueli':'学历ID',
                        'diqu':'地区名称',
                        'guanxi':'关系',
                        'qinmidu':'亲密度',
                        'yingxiangli':'影响力',
                        'qituxin':'企图心',
                        'shiyetaidu':'事业态度',
                        'renmaiquan':'人脉圈',
                        'jingjinengli':'经济能力',
                    },
                }
        else:

            # 查询客户信息备注
            if oper_type == 'get_customer_note':
                field_dict = {
                    'id': '',
                    'remote_type': '',
                    'customer_id': '',
                    'user_id': '',
                }

                q = conditionCom(request, field_dict)
                objs = models.customer_information_the_user.objects.filter(q).order_by(order)

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                count = objs.count()

                ret_data = []
                remote_type = request.GET.get('remote_type')

                num = 0
                for obj in objs:
                    create_datetime = obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    remote_obj = eval(obj.remote)
                    remote = remote_obj.get('remote')
                    title = remote_obj.get('title')
                    create_date = remote_obj.get('create_date')

                    if int(remote_type) == 2:
                        ret_data.append({
                            'create_date': create_date,
                            'title': title,
                        })
                    elif int(remote_type) == 3:
                        ret_data.append({
                            'title': title,
                        })
                    else:
                        ret_data.append({

                        })

                    ret_data[num]['create_datetime'] = create_datetime
                    ret_data[num]['remote'] = remote
                    ret_data[num]['id'] = obj.id
                    num += 1
                remote_type_choices = []
                for i in models.customer_information_the_user.remote_type_choices:
                    remote_type_choices.append({
                        'id': i[0],
                        'name': i[1]
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'remote_type': remote_type_choices,
                    'count': count,
                    'ret_data': ret_data,
                }

                response.note = {
                    'create_datetime':'创建时间',
                    'remote':'备注',
                    'id':'备注ID',
                    'create_date':'用户自定时间',
                    'title':'标题',
                }

            # 谁看了我 详情
            elif oper_type == 'day_eye_detail':
                user_id = forms_obj.cleaned_data['user_id']
                article_objs = models.SelectArticleLog.objects.filter(inviter_id=user_id, customer_id=o_id)
                info_objs = article_objs.order_by(order)


                # 谁看了我详情 右上角星星数据
                info_data = {
                    'xueli': '初中',
                    'diqu': '北京',
                    'guanxi': '朋友',
                    'qinmidu': 1,
                    'yingxiangli': 1,
                    'qituxin': 1,
                    'shiyetaidu': 1,
                    'renmaiquan': 1,
                    'jingjinengli': 1,
                    'customer_demand':[]
                }
                information_objs = models.user_comments_customer_information.objects.filter(user_id=user_id, customer_id=o_id)
                if information_objs:
                    information_obj = information_objs[0]
                    try:
                        customer_info = eval(information_obj.customer_info)
                    except Exception:
                        customer_info = information_obj.customer_info
                    customer_label = customer_info.get('customer_label')

                    try:
                        customer_demand = json.loads(customer_info.get('customer_demand'))
                    except Exception:
                        customer_demand = customer_info.get('customer_demand')

                    info_data = {
                        'xueli': customer_label.get('xueli'),
                        'diqu': customer_label.get('diqu'),
                        'guanxi': customer_label.get('guanxi'),
                        'qinmidu': customer_label.get('qinmidu'),
                        'yingxiangli': customer_label.get('yingxiangli'),
                        'qituxin': customer_label.get('qituxin'),
                        'shiyetaidu': customer_label.get('shiyetaidu'),
                        'renmaiquan': customer_label.get('renmaiquan'),
                        'jingjinengli': customer_label.get('jingjinengli'),
                        'customer_demand': customer_demand,
                    }
                avg_stars_list = []
                for k, v in info_data.items():
                    if k in ['qinmidu', 'yingxiangli', 'qituxin', 'shiyetaidu', 'renmaiquan', 'jingjinengli']:
                        avg_stars_list.append(int(v))
                avg_stars = sum(avg_stars_list) / 6  # 右上角星星 平均值

                # 客户基本信息
                obj = info_objs[0]
                customer_info = {
                    'customer_id': obj.customer_id,
                    'customer__name': b64decode(obj.customer.name),
                    'customer__set_avator': obj.customer.set_avator,
                    'info_data': info_data,
                    'avg_stars': avg_stars,
                }

                objs = article_objs.values('article_id', 'article__title', 'article__cover_img').annotate(Count('id'))
                is_remake_count = models.customer_information_the_user.objects.filter(user_id=user_id, customer_id=o_id).count()
                count = objs.count()

                is_remake = False
                if is_remake_count >= 1:
                    is_remake = True

                ret_data = []
                for obj in objs:
                    article_id = obj.get('article_id')
                    article_obj = article_objs.filter(article_id=article_id).order_by(order)[:1]

                    time_detail = []    # 查看时长及时间
                    for info_obj in info_objs:
                        if int(info_obj.article_id) == int(article_id):
                            time_length = '1秒'
                            create_datetime = info_obj.create_datetime
                            if info_obj.close_datetime:
                                time_length = get_min_s(info_obj.close_datetime, create_datetime)
                            time_detail.append({
                                'time_length': time_length,
                                'select_datetime': create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                            })

                    create_datetime = article_obj[0].create_datetime
                    after_time = get_min_s(create_datetime, datetime.datetime.today(), ms=1)
                    ret_data.append({
                        'article_id': article_id,
                        'article__title': obj.get('article__title'),
                        'article_info': '看了' + str(obj.get('id__count')) + '次' + '-' + after_time + '前',
                        'time_detail': time_detail,
                        'article__cover_img': obj.get('article__cover_img'),
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'customer_info': customer_info,
                    'ret_data': ret_data,
                    'data_count': count,
                    'is_remake': is_remake,
                }
                response.note = {
                    'customer_id': "客户id",
                    'customer__name': "客户姓名",
                    'customer__set_avator': "客户头像",
                    'article_id': "文章ID",
                    'article__title': "文章标题",
                    'close_datetime': "关闭页面时间",
                    'create_datetime': "创建时间",
                    'article_info': "看了几次 最后一次查看时间",
                    'time_length': "时长",
                    'select_datetime': "查看时间",
                    'article__cover_img': "文章图片",
                    'is_remake': "该客户是否有备注(如果有那么可删除)",
                    'qinmidu': '亲密度',
                    'yingxiangli': '影响力',
                    'qituxin': '企图心',
                    'shiyetaidu': '事业态度',
                    'renmaiquan': '人脉圈',
                    'jingjinengli': '经济能力',
                    'avg_stars':'星星平均值'
                }

            # 按文章查看(天眼功能)列表页
            elif oper_type == 'view_by_article':

                objs = models.SelectArticleLog.objects.filter(
                    inviter_id=user_id
                ).values('article_id', 'article__title').distinct().annotate(Count('id'))

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                count = objs.count()

                ret_data = []
                for obj in objs:
                    article_obj = models.SelectArticleLog.objects.filter(article_id=obj['article_id']).order_by(order)
                    cover_img = article_obj[0].article.cover_img    # 文章封面
                    create_datetime = article_obj[0].create_datetime
                    after_time = get_min_s(create_datetime, datetime.datetime.today(), ms=1)

                    ret_data.append({
                        'article_id': obj['article_id'],
                        'article__title': obj['article__title'],
                        'id__count': obj['id__count'],
                        'after_time': after_time + '前',
                        'cover_img': cover_img,
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                }
                response.note = {
                    'article_id': '文章ID',
                    'article__title': '文章标题',
                    'id__count': '查看该文章人 总数',
                    'cover_img': '文章封面',
                    'after_time': '最后查看日期',
                }

            # 按文章查看(详情)
            elif oper_type == 'view_by_article_detail':
                article_obj = models.SelectArticleLog.objects.filter(
                    inviter_id=user_id,
                    article_id=o_id
                )
                objs = article_obj.values('customer_id', 'customer__name', 'customer__set_avator').distinct().annotate(Count('id'))

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                count = objs.count()
                ret_data = []
                for obj in objs:
                    objs = article_obj.filter(customer_id=obj['customer_id'])[:1]
                    create_datetime = objs[0].create_datetime
                    after_time = get_min_s(create_datetime, datetime.datetime.today(), ms=1)
                    ret_data.append({
                        'customer_id': obj['customer_id'],
                        'customer__set_avator': obj['customer__set_avator'],
                        'customer__name': b64decode(obj['customer__name']),
                        'article_info': '看了' + str(obj['id__count']) + '次-' + after_time + '前',
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                }
                response.note = {
                    'customer_id': '客户ID',
                    'customer__name': '客户名称',
                    'article_info': '该人查看该文章 总数/ 时长',
                }

            # 查询客户资料
            elif oper_type == 'get_customer_info':
                objs = models.user_comments_customer_information.objects.filter(
                    user_id=user_id,
                    customer_id=o_id
                )

                if not objs:
                    customer_info = {
                        'customer_sex': '',
                        'customer_set_avator': '',
                        'customer_name': '',
                        'customer_wechat': '',
                        'customer_phone': '',
                        'customer_professional': '',
                        'customer_birthday': '',
                        'customer_remake': '',
                        'customer_demand': [],
                        'customer_label': {
                            'xueli': '初中',
                            'diqu': '北京',
                            'guanxi': '朋友',
                            'qinmidu': 1,
                            'yingxiangli': 1,
                            'qituxin': 1,
                            'shiyetaidu': 1,
                            'renmaiquan': 1,
                            'jingjinengli': 1,
                        },
                    }
                    models.user_comments_customer_information.objects.create(
                        user_id=user_id,
                        customer_id=o_id,
                        customer_info=customer_info
                    )

                    objs = models.user_comments_customer_information.objects.filter(
                        user_id=user_id,
                        customer_id=o_id
                    )

                obj = objs[0]
                info = eval(obj.customer_info)

                customer_sex = obj.customer.sex
                if info.get('customer_sex'):
                    customer_sex = info.get('customer_sex')

                customer_set_avator = obj.customer.set_avator
                if info.get('customer_set_avator'):
                    customer_set_avator = info.get('customer_set_avator')

                customer = b64decode(obj.customer.name)
                customer_name = customer
                if info.get('customer_name'):
                    customer_name = info.get('customer_name')

                customer_label = info.get('customer_label')
                print('customer_label-------> ', customer_label)
                try:
                    customer_demand = eval(info.get('customer_demand'))
                except Exception:
                    customer_demand = info.get('customer_demand')

                ret_data = {
                    'customer_sex': customer_sex,
                    'customer_set_avator': customer_set_avator,
                    'customer_name': customer_name,
                    'customer_wechat': customer,
                    'customer_phone': info.get('customer_phone'),
                    'customer_professional': info.get('customer_professional'),
                    'customer_birthday': info.get('customer_birthday'),
                    'customer_remake': info.get('customer_remake'),
                    'customer_demand': customer_demand,
                    'customer_label': {
                        'xueli': customer_label.get('xueli'),
                        'diqu': customer_label.get('diqu'),
                        'guanxi': customer_label.get('guanxi'),
                        'qinmidu': customer_label.get('qinmidu'),
                        'yingxiangli': customer_label.get('yingxiangli'),
                        'qituxin': customer_label.get('qituxin'),
                        'shiyetaidu': customer_label.get('shiyetaidu'),
                        'renmaiquan': customer_label.get('renmaiquan'),
                        'jingjinengli': customer_label.get('jingjinengli'),
                    },
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S')
                }

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data':ret_data
                }
                response.note = {
                    'customer_sex': '用户性别 默认微信性别',
                    'customer_set_avator': '用户头像 默认微信头像',
                    'customer_name': '用户姓名 备注 默认微信名称',
                    'customer_wechat': '用户微信名称',
                    'customer_phone': '用户电话',
                    'customer_professional': '用户职业',
                    'customer_birthday': '用户生日',
                    'customer_remake': '用户备注',
                    'customer_demand': '用户需求',
                    'customer_label': {
                        'xueli':'学历ID',
                        'diqu':'地区名称',
                        'guanxi':'关系',
                        'qinmidu':'亲密度',
                        'yingxiangli':'影响力',
                        'qituxin':'企图心',
                        'shiyetaidu':'事业态度',
                        'renmaiquan':'人脉圈',
                        'jingjinengli':'经济能力',
                    }
                }

            else:
                response.code = 402
                response.msg = '请求异常'

    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)

