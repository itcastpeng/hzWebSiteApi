from hurong import models
from publicFunc import Response, account
from publicFunc.public import requests_log
from django.http import JsonResponse
from hurong.forms.xiaohongshu_userprofile import IsUpdateUserinfoForm, UpdateUserinfoForm, RegistreForm, IsTodayUpdateReading
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
    # print('request.POST -->', request.POST)
    if request.method == "POST":
        # 更新小红书用户信息
        if oper_type == "update_userinfo":
            form_data = {
                'phone_num': request.POST.get('phone_num'),
                'imsi': request.POST.get('imsi'),
                'iccid': request.POST.get('iccid'),
                'name': request.POST.get('name'),
                'xiaohongshu_id': request.POST.get('xiaohongshu_id'),
                'home_url': request.POST.get('home_url'),
                'macaddr': request.POST.get('macaddr'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = UpdateUserinfoForm(form_data)
            if forms_obj.is_valid():

                phone_num = forms_obj.cleaned_data.get('phone_num')
                imsi = forms_obj.cleaned_data.get('imsi')
                iccid = forms_obj.cleaned_data.get('iccid')
                name = forms_obj.cleaned_data.get('name')
                xiaohongshu_id = forms_obj.cleaned_data.get('xiaohongshu_id')
                home_url = forms_obj.cleaned_data.get('home_url')
                macaddr = forms_obj.cleaned_data.get('macaddr')

                if macaddr:
                    data = {'macaddr': macaddr}
                else:
                    data = {'imsi':imsi}
                objs = models.XiaohongshuPhone.objects.filter(**data)
                objs.update(phone_num=phone_num, is_debug=False)
                print("objs --->", objs)
                if objs:
                    obj = objs[0]
                    print('obj.xiaohongshuuserprofile_set -->', obj.xiaohongshuuserprofile_set)
                    if not obj.xiaohongshuuserprofile_set.all():
                        xiaohongshu_userprofile_obj = obj.xiaohongshuuserprofile_set.create(
                            name=name,
                            xiaohongshu_id=xiaohongshu_id,
                            home_url=home_url
                        )
                    else:
                        xiaohongshu_userprofile_obj = models.XiaohongshuUserProfile.objects.get(
                            phone_id=obj
                        )
                        xiaohongshu_userprofile_obj.name = name
                        xiaohongshu_userprofile_obj.xiaohongshu_id = xiaohongshu_id
                        xiaohongshu_userprofile_obj.home_url = home_url
                        xiaohongshu_userprofile_obj.save()

                    # 如果小红书博主注册表中有未注册的,则将信息提交给小红书后台
                    xhs_userprofile_register_objs = models.XiaohongshuUserProfileRegister.objects.filter(
                        name=name,
                        is_register=False,
                    )
                    if xhs_userprofile_register_objs:
                        xhs_userprofile_register_obj = xhs_userprofile_register_objs[0]
                        # print("===============>", xhs_userprofile_register_obj.name, xhs_userprofile_register_obj.uid)
                        # 将注册成功的小红书账号推送到小红书后台
                        api_url = "https://www.ppxhs.com/api/v1/sync/sync-screen-blogger"
                        data = {
                            "id": xhs_userprofile_register_obj.uid,
                            "xhs_id": xiaohongshu_id,
                            "link": home_url,
                            "mobile": phone_num,
                        }
                        ret = requests.post(api_url, data=data)
                        print("ret.json() -->", ret.json())
                        requests_log(api_url, data, ret.json()) # 记录请求日志
                        xhs_userprofile_register_objs.update(
                            is_register=True,
                            register_datetime=datetime.datetime.now()
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

        # 修改阅读量更新时间
        elif oper_type == 'update_reading_update_time':
            form_data = {
                'imsi': request.GET.get('imsi'),
                'iccid': request.GET.get('iccid')
            }
            form_obj = IsTodayUpdateReading(form_data)
            if form_obj.is_valid():
                imsi = form_obj.cleaned_data.get('imsi')
                obj = models.XiaohongshuUserProfile.objects.get(
                    id=imsi
                )
                obj.update_reading_date = datetime.date.today()
                obj.save()
                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

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

        # 查询今天是否更新阅读量
        elif oper_type == 'check_updated_today':
            form_data = {
                'imsi': request.GET.get('imsi'),
                'iccid': request.GET.get('iccid')
            }
            form_obj = IsTodayUpdateReading(form_data)
            if form_obj.is_valid():
                imsi = form_obj.cleaned_data.get('imsi')
                obj = models.XiaohongshuUserProfile.objects.get(
                    id=imsi
                )
                flag = False
                update_reading_date = obj.update_reading_date
                if update_reading_date and update_reading_date == datetime.date.today():
                    flag = True
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    "flag": flag
                }


            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)
