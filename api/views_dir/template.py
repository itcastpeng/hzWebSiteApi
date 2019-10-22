# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.db.models import Q
from publicFunc.condition_com import conditionCom
from api.forms.template import AddForm, UpdateForm, SelectForm, GetTabBarDataForm, UpdateClassForm, UserAddTemplateForm, \
    BindTemplatesAndApplets, UnbindAppletAndTemplate, UpdateTemplateName
from api.views_dir.page import page_base_data
from publicFunc.role_choice import admin_list
from publicFunc.public import get_qrcode
from hz_website_api_celery.tasks import get_xcx_qrcode
import json


@account.is_token(models.UserProfile)
def template(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            is_all = request.GET.get('is_all') #
            user_id = request.GET.get('user_id')
            user_obj = models.UserProfile.objects.get(id=user_id)
            if user_obj.inviter:
                user_id = user_obj.inviter_id
            obj = models.UserProfile.objects.get(id=user_id)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'name': '__contains',
                'template_class_id': '',
                'create_datetime': '',
            }
            q = conditionCom(request, field_dict)
            if obj.role_id in [7, '7'] and not is_all:
                q.add(Q(create_user_id=user_id), Q.AND)
            else:
                q.add(Q(create_user__role_id__in=admin_list), Q.AND)
            objs = models.Template.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                template_class_id = ''
                template_class_name = ''
                if obj.template_class:
                    template_class_id = obj.template_class_id
                    template_class_name = obj.template_class.name

                is_authorization = False
                apple_objs = obj.clientapplet_set.all()
                if apple_objs and apple_objs[0].is_authorization:
                    is_authorization = True

                xcx_appid = ''
                xcx_id = ''
                if apple_objs and apple_objs[0].template:
                    xcx_id = apple_objs[0].id
                    xcx_appid = apple_objs[0].appid

                # 将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'is_authorization': is_authorization,
                    'share_qr_code': obj.share_qr_code,
                    'logo_img': obj.logo_img,
                    'xcx_id': xcx_id,
                    'qrcode': obj.qrcode,
                    'xcx_qrcode': obj.xcx_qrcode,
                    'xcx_appid': xcx_appid,
                    'thumbnail': obj.thumbnail,
                    'template_class_name': template_class_name,
                    'template_class_id': template_class_id,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            response.note = {
                'id': "模板id",
                'name': '模板名称',
                'create_datetime': '创建时间',
                'share_qr_code': '分享二维码',
                'logo_img': 'logo图片',
                'is_authorization': '是否授权',
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def template_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    user_obj = models.UserProfile.objects.get(id=user_id)
    if user_obj.inviter:
        user_id = user_obj.inviter_id
    if request.method == "POST":

        # 创建模板
        if oper_type == "add":
            form_data = {
                'create_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'thumbnail': request.POST.get('thumbnail'), # 缩略图
                'template_class_id': request.POST.get('template_class_id'), # 缩略图
            }
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                template_obj = models.Template.objects.create(
                    create_user_id=forms_obj.cleaned_data.get('create_user_id'),
                    name=forms_obj.cleaned_data.get('name'),
                    thumbnail=forms_obj.cleaned_data.get('thumbnail'),
                    template_class_id=forms_obj.cleaned_data.get('template_class_id'),
                )
                template_obj.qrcode = get_qrcode('https://xcx.bjhzkq.com/wx/?id={}'.format(template_obj.id)) # 更新二维码
                if not template_obj.xcx_qrcode:
                    get_xcx_qrcode.delay(template_obj.id, user_id, user_obj.token)


                page_group_obj = models.PageGroup.objects.create(
                    name="默认组",
                    template=template_obj
                )

                print('page_base_data -->', page_base_data)
                page_obj = models.Page.objects.create(
                    name="首页",
                    page_group=page_group_obj,
                    data=json.dumps(page_base_data)
                )

                tab_bar_base_data = {
                    "type": "tab_bar",
                    "txt": "底部导航",
                    "style": {
                        'borderStyle': 'solid',  # 顶部边框 solid->实线  dotted->点线  dashed->虚线
                        'borderColor': '#d8d8d8',  # 顶部边框颜色
                        'borderWidth': 1,  # 顶部边框粗细
                        'backgroundColor': '#ffffff',  # 背景颜色
                        'color': '#515a6e',  # 文字颜色-未选中
                        'selectedColor': '#1296db'  # 文字颜色-选中
                    },
                    "data": [
                        {
                            "page_id": page_obj.id,
                            "text": '导航1',
                            "icon_path": '/statics/admin_imgs/tabbar/homepage.png',
                            "selected_icon_path": '/statics/admin_imgs/tabbar/homepage_selected.png'
                        },
                        {
                            "page_id": page_obj.id,
                            "text": '导航2',
                            "icon_path": '/statics/admin_imgs/tabbar/people.png',
                            "selected_icon_path": '/statics/admin_imgs/tabbar/people_selected.png'
                        }
                    ]
                }
                template_obj.tab_bar_data = json.dumps(tab_bar_base_data)
                template_obj.save()
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': template_obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除 模板
        elif oper_type == "delete":
            if not models.ClientApplet.objects.filter(template_id=o_id):
                objs = models.Template.objects.filter(id=o_id)
                if objs:
                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 302
                    response.msg = '删除ID不存在'
            else:
                response.code = 301
                response.msg = '请先解绑小程序'

        # 更改模板
        elif oper_type == "update":
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
                'logo_img': request.POST.get('logo_img'),
                'tab_bar_data': request.POST.get('tab_bar_data'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                # print("验证通过")
                # print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']
                logo_img = forms_obj.cleaned_data['logo_img']
                tab_bar_data = forms_obj.cleaned_data['tab_bar_data']
                update_data = {}
                if logo_img:
                    update_data['logo_img'] = logo_img
                if name:
                    update_data['name'] = name
                if tab_bar_data:
                    update_data['tab_bar_data'] = tab_bar_data

                # 更新数据
                models.Template.objects.filter(id=o_id).update(**update_data)
                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改模板分类id/name
        elif oper_type == "update_class":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'class_id': request.POST.get('class_id'),
                'name': request.POST.get('name'),
            }

            forms_obj = UpdateClassForm(form_data)
            if forms_obj.is_valid():
                # print("验证通过")
                # print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']
                class_id = forms_obj.cleaned_data['class_id']

                # 更新数据
                models.Template.objects.filter(id=o_id).update(
                    template_class_id=class_id,
                    name=name
                )

                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 客户创建模板
        elif oper_type == 'user_add_template': # 新建新模板  和 更换模板(需要传递旧模板ID 删除数据)
            old_template_id = request.POST.get('template_id')
            form_data = {
                'template_id':o_id,
                # 'page_id':request.POST.get('page_id')
            }
            form_obj = UserAddTemplateForm(form_data)
            if form_obj.is_valid():
                template_id, data = form_obj.cleaned_data.get('template_id')
                if old_template_id : # 如果有旧模板ID 则删掉
                    template_objs = models.Template.objects.filter(id=old_template_id )
                    page_group_objs = models.PageGroup.objects.filter(template_id=template_objs[0].id)
                    for page_group_obj in page_group_objs:
                        models.Page.objects.filter(page_group_id=page_group_obj.id).delete()
                    page_group_objs.delete()
                    template_objs.update(**data)
                    obj = template_objs[0]

                else: # 生成新模板
                    data['create_user_id'] = user_id
                    obj = models.Template.objects.create(**data)
                    obj.qrcode = get_qrcode('https://xcx.bjhzkq.com/wx/?id={}'.format(obj.id))  # 更新二维码
                    if not obj.xcx_qrcode:
                        get_xcx_qrcode.delay(obj.id, user_id, user_obj.token)

                tab_bar_data = json.loads(obj.tab_bar_data) # 将page_id 更改

                page_group_objs = models.PageGroup.objects.filter(template_id=o_id)
                for page_group_obj in page_group_objs:
                    PageGroupObj = models.PageGroup.objects.create(
                        name=page_group_obj.name,
                        template_id=obj.id,
                        create_user_id=user_id,
                    )
                    for page_set in page_group_obj.page_set.all():
                        page_obj = models.Page.objects.get(id=page_set.id)
                        page_obj = models.Page.objects.create(
                            name=page_obj.name,
                            page_group=PageGroupObj,
                            data=page_obj.data,
                            create_user_id=user_id
                        )
                        for tab_data in tab_bar_data.get('data'):
                            print('page_obj.id--------------------------------> ', page_obj.id, tab_data.get('page_id'))
                            if str(page_set.id) == tab_data.get('page_id'):
                                tab_data['page_id'] = page_obj.id

                if old_template_id:
                    template_objs.update(tab_bar_data=json.dumps(tab_bar_data))
                else:
                    obj.tab_bar_data = json.dumps(tab_bar_data)
                    obj.save()

                response.code = 200
                response.msg = '创建成功'
                response.data = {
                    'id': obj.id,
                }
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 绑定模板和小程序
        elif oper_type == 'bind_templates_and_applets':
            form_data = {
                'template_id': request.POST.get('template_id'),
                'appid': request.POST.get('appid'),
                'user_id': user_id,
            }
            form_obj = BindTemplatesAndApplets(form_data)
            if form_obj.is_valid():
                appid = form_obj.cleaned_data.get('appid')
                template_id = form_obj.cleaned_data.get('template_id')
                models.ClientApplet.objects.filter(
                    appid=appid
                ).update(
                    template_id=template_id
                )
                response.code = 200
                response.msg = '绑定成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 解除绑定小程序和模板
        elif oper_type == 'unbind_applet_and_template':
            form_data = {
                'appid': request.POST.get('appid'),
                'user_id': user_id,
            }
            form_obj = UnbindAppletAndTemplate(form_data)
            if form_obj.is_valid():
                appid = form_obj.cleaned_data.get('appid')
                user_id = form_obj.cleaned_data.get('user_id')
                objs = models.ClientApplet.objects.filter(
                    appid=appid,
                    user_id=user_id
                )
                objs.update(template=None)
                response.code = 200
                response.msg = '解除绑定成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

    else:
        # 获取底部导航数据
        if oper_type == "get_tab_bar_data":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id
            }

            forms_obj = GetTabBarDataForm(form_data)
            if forms_obj.is_valid():
                # print("验证通过")
                # print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']

                template_objs = models.Template.objects.filter(id=o_id)
                if template_objs:
                    response.code = 200
                    response.data = {
                        'data': template_objs[0].tab_bar_data
                    }
                else:
                    response.code = 301
                    response.msg = "模板id异常"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 发布审核时 判断模板是否关联 小程序
        elif oper_type == 'determines_whether_template_associated_applet':
            objs = models.ClientApplet.objects.filter(user_id=user_id)
            flag = False
            for obj in objs:
                if obj.template:
                    if obj.template_id == int(o_id):
                        flag = True
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'flag': flag
            }

        # 查询该用户 模板绑定的小程序信息
        elif oper_type == 'template_binding_applet_information':
            objs = models.ClientApplet.objects.filter(
                user_id=user_id,
                template_id=o_id,
            )
            data_dict = {}
            if objs:
                obj = objs[0]
                data_dict['xcx_appid'] = obj.appid
                data_dict['xcx_head_img'] = obj.head_img
                data_dict['xcx_nick_name'] = obj.nick_name
                data_dict['xcx_id'] = obj.id
                code = 200
                msg = '查询成功'

            else:
                code = 301
                msg = '未绑定小程序'

            response.code = code
            response.msg = msg
            response.data = {
                'data_dict': data_dict
            }
        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
