from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from publicFunc.send_email import SendEmail
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.xiaohongshu_userprofile import IsUpdateUserinfoForm, UpdateUserinfoForm, RegistreForm
from django.db.models import Q
import redis
import json
import requests
import datetime
import re


# @account.is_token(models.UserProfile)
# def xiaohongshu_userprofile(request):
#     response = Response.ResponseObj()
#     if request.method == "GET":
#         forms_obj = SelectForm(request.GET)
#         if forms_obj.is_valid():
#             user_id = request.GET.get('user_id')
#             current_page = forms_obj.cleaned_data['current_page']
#             length = forms_obj.cleaned_data['length']
#             # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
#             order = request.GET.get('order', '-create_datetime')
#             field_dict = {
#                 'id': '',
#                 'status': '',
#                 'select_type': '',
#                 'keywords': '__contains',
#                 'create_datetime': '',
#             }
#
#             q = conditionCom(request, field_dict)
#
#             print('q -->', q)
#             objs = models.XiaohongshuFugai.objects.filter(q).order_by(order)
#             print(objs)
#             count = objs.count()
#
#             if length != 0:
#                 if count < 10:
#                     current_page = 1
#                 start_line = (current_page - 1) * length
#                 stop_line = start_line + length
#                 objs = objs[start_line: stop_line]
#
#             ret_data = []
#             for obj in objs:
#                 #  将查询出来的数据 加入列表
#                 update_datetime = ""
#                 if obj.update_datetime:
#                     update_datetime = obj.update_datetime.strftime('%Y-%m-%d %H:%M:%S')
#
#                 keywords = "({select_type}) {keywords}".format(
#                     keywords=obj.keywords,
#                     select_type=obj.get_select_type_display()
#                 )
#                 ret_data.append({
#                     'id': obj.id,
#                     'keywords': keywords,
#                     'url': obj.url,
#                     'rank': obj.rank,
#                     'biji_num': obj.biji_num,
#                     'status': obj.get_status_display(),
#                     'status_id': obj.status,
#                     'select_type': obj.get_select_type_display(),
#                     'select_type_id': obj.select_type,
#                     'create_user__username': obj.create_user.username,
#                     'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
#                     'update_datetime': update_datetime,
#                 })
#             #  查询成功 返回200 状态码
#             response.code = 200
#             response.msg = '查询成功'
#             response.data = {
#                 'ret_data': ret_data,
#                 'data_count': count,
#                 'status_choices': models.XiaohongshuFugai.status_choices,
#                 'select_type_choices': models.XiaohongshuFugai.select_type_choices,
#             }
#             response.note = {
#                 'id': "下拉词id",
#                 'keywords': "搜索词",
#                 'url': "匹配url",
#                 'rank': "排名",
#                 'biji_num': "笔记数",
#                 'status': "状态",
#                 'status_id': "状态id",
#                 'select_type': "搜索类型",
#                 'select_type_id': "搜索类型id",
#                 'create_user__username': "创建人",
#                 'create_datetime': "创建时间",
#                 'update_datetime': "更新时间",
#             }
#         else:
#             print("forms_obj.errors -->", forms_obj.errors)
#             response.code = 402
#             response.msg = "请求异常"
#             response.data = json.loads(forms_obj.errors.as_json())
#     return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.UserProfile)
def xiaohongshu_userprofile_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "POST":
        # 更新小红书用户信息
        if oper_type == "update_userinfo":
            form_data = {
                'imsi': request.POST.get('imsi'),
                'iccid': request.POST.get('iccid'),
                'name': request.POST.get('name'),
                'xiaohongshu_id': request.POST.get('xiaohongshu_id'),
                'home_url': request.POST.get('home_url'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = UpdateUserinfoForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")

                imsi = forms_obj.cleaned_data.get('imsi')
                iccid = forms_obj.cleaned_data.get('iccid')
                name = forms_obj.cleaned_data.get('name')
                xiaohongshu_id = forms_obj.cleaned_data.get('xiaohongshu_id')
                home_url = forms_obj.cleaned_data.get('home_url')

                print("imsi -->", imsi)
                print("iccid -->", iccid)
                for obj in models.XiaohongshuPhone.objects.all():
                    print('obj -->', obj)
                objs = models.XiaohongshuPhone.objects.filter(
                    imsi=imsi,
                    # iccid=iccid
                )
                print("objs --->", objs)
                if objs:
                    obj = objs[0]
                    print('obj.xiaohongshuuserprofile_set -->', obj.xiaohongshuuserprofile_set)
                    if not obj.xiaohongshuuserprofile_set.all():
                        obj.xiaohongshuuserprofile_set.create(
                            name=name,
                            xiaohongshu_id=xiaohongshu_id,
                            home_url=home_url
                        )
                    else:
                        obj.xiaohongshuuserprofile_set.all().update(
                            name=name,
                            xiaohongshu_id=xiaohongshu_id,
                            home_url=home_url
                        )
                response.code = 200
                response.msg = "更新成功"
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "registre":
            print("registre")
            form_data = {
                'uid': request.POST.get('uid'),
                'name': request.POST.get('name'),
                'head_portrait': request.POST.get('head_portrait'),
                'gender': request.POST.get('gender'),
                'birthday': request.POST.get('birthday')
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = RegistreForm(form_data)
            if forms_obj.is_valid():
                models.XiaohongshuUserProfileRegister.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        # 判断是否需要更新个人信息
        if oper_type == "is_update_userinfo":
            form_data = {
                'imsi': request.GET.get('imsi'),
                'iccid': request.GET.get('iccid')
            }
            forms_obj = IsUpdateUserinfoForm(form_data)
            if forms_obj.is_valid():
                imsi = forms_obj.cleaned_data['imsi']
                iccid = forms_obj.cleaned_data['iccid']

                objs = models.XiaohongshuUserProfile.objects.filter(
                    phone_id__imsi=imsi,
                    phone_id__iccid=iccid
                )

                is_update = False
                if not objs:    # 没有数据,需要更新
                    is_update = True

                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    "is_update": is_update
                }
            else:
                print("forms_obj.errors -->", forms_obj.errors)
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)