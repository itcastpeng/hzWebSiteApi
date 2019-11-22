from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.user import SelectForm, UpdateRoleForm, TransferAllUserInformation, DeleteTeamMembers, UpdateForm
import datetime, re, json
from publicFunc.api_public import create_error_log
from publicFunc import base64_encryption


@account.is_token(models.UserProfile)
def user(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.UserProfile.objects.select_related('role').filter(q, openid__isnull=False)

            exclude_role_admin = request.GET.get('exclude_role_admin', False)  # 是否排除管理员角色
            if exclude_role_admin:
                role_admin_id_list = [6, 8]  # 管理员角色id
                objs = objs.exclude(role_id__in=role_admin_id_list)

            inviter_id_is_null = request.GET.get('inviter_id_is_null', False)
            if inviter_id_is_null:
                objs = objs.filter(inviter_id__isnull=True)

            objs = objs.order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []




            for obj in objs:
                inviter = 0
                if obj.inviter:
                    inviter = 1

                role_obj = models.Role.objects.filter(id=obj.role_id)
                data_list = []
                for i in role_obj[0].permissions.all():
                    data_list.append(i.name)

                ret_data.append({
                    'id': obj.id,
                    'name': base64_encryption.b64decode(obj.name),
                    'role_id': obj.role_id,
                    'role_name': obj.role.name,
                    'head_portrait': obj.head_portrait,
                    'token': obj.token,
                    'sex_id': obj.sex,
                    'sex': obj.get_sex_display(),
                    'company_name': obj.company_name,
                    'permissions_list': data_list,
                    'inviter': inviter,
                    'remark': obj.remark,
                    'small_program_number': obj.small_program_number,
                    'number_child_users': obj.number_child_users,
                    'last_login_datetime': obj.last_login_datetime.strftime('%Y-%m-%d %H:%M:%S'),
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
                'id': "用户id",
                'name': "微信昵称",
                'role_id': "角色id",
                'role_name': "角色名称",
                'head_portrait': "头像",
                'sex_id': "性别id",
                'sex': "性别",
                'company_name': "公司名称",
                'remark': "备注",
                'last_login_datetime': "最后登录时间",
                'create_datetime': "创建时间",
                'number_child_users': "可创建子账号数量",
                'small_program_number': "可创建小程序数量",
            }

        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.UserProfile)
def user_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 修改用户角色    (即将废弃,被update取代)
        if oper_type == 'update_role':
            form_data = {
                 'role_id': request.POST.get('role_id'),
                 'user_id': user_id,
                 'o_id': o_id
            }

            form_obj = UpdateRoleForm(form_data)
            if form_obj.is_valid():
                role_id = form_obj.cleaned_data.get('role_id')
                o_id = form_obj.cleaned_data.get('o_id')
                models.UserProfile.objects.filter(
                    id=o_id
                ).update(
                    role_id=role_id
                )
                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'role_id': request.POST.get('role_id'),  # 角色id
                'company_name': request.POST.get('company_name'),  # 公司名称
                'remark': request.POST.get('remark'),  # 备注信息
                'small_program_number': request.POST.get('small_program_number'),  # 小程序数量
                'number_child_users': request.POST.get('number_child_users'),  # 子账号数量
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data['o_id']
                role_id = forms_obj.cleaned_data['role_id']  # 角色id
                company_name = forms_obj.cleaned_data['company_name']  # 公司名称
                remark = forms_obj.cleaned_data['remark']  # 备注信息
                small_program_number = forms_obj.cleaned_data['small_program_number']  # 小程序数量
                number_child_users = forms_obj.cleaned_data['number_child_users']  # 子账号数量
                #  查询数据库  用户id
                objs = models.UserProfile.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if objs:
                    objs.update(
                        role_id=role_id,
                        company_name=company_name,
                        remark=remark,
                        small_program_number=small_program_number,
                        number_child_users=number_child_users,
                    )

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = '不存在的数据'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 转接 用户所有信息
        elif oper_type == 'transfer_all_user_information':
            cancel_transfer = request.POST.get('cancel_transfer') # 拒绝交接
            form_data = {
                'user_id':user_id,
                'o_id': o_id,
                # 'transfer_template_id': request.POST.get('transfer_template_id'),
            }
            transfer_objs = models.Transfer.objects.filter(
                speak_to_people_id=user_id,
                by_connecting_people_id=o_id,
                whether_transfer_successful=2
            ).order_by('-create_datetime')
            if transfer_objs:
                transfer_obj = transfer_objs[0]
                if cancel_transfer:
                    transfer_obj.whether_transfer_successful = 5
                    code = 200
                    msg = '已拒绝交接'

                else:
                    form_obj = TransferAllUserInformation(form_data)
                    if form_obj.is_valid():
                        o_id = form_obj.cleaned_data.get('o_id')
                        user_id = form_obj.cleaned_data.get('user_id')

                        applet_objs = models.ClientApplet.objects.filter(user_id=user_id)                   # 小程序
                        models.CustomerOfficialNumber.objects.filter(user_id=user_id).update(user_id=o_id)  # 小程序版本
                        applet_objs.update(user_id=o_id)

                        models.TemplateClass.objects.filter(create_user_id=user_id).update(create_user_id=o_id)             # 模板分类表
                        models.Template.objects.filter(create_user_id=user_id).update(create_user_id=o_id)                  # 模板表

                        models.PhotoLibraryGroup.objects.filter(create_user_id=user_id).update(create_user_id=o_id)         # 图片分类
                        models.PhotoLibrary.objects.filter(create_user_id=user_id).update(create_user_id=o_id)              # 图片

                        models.PageGroup.objects.filter(create_user_id=user_id).update(create_user_id=o_id)                 # 页面分组表
                        models.Page.objects.filter(create_user_id=user_id).update(create_user_id=o_id)                      # 页面表

                        models.CompomentLibraryClass.objects.filter(create_user_id=user_id).update(create_user_id=o_id)     # 组件库分类
                        models.CompomentLibrary.objects.filter(create_user_id=user_id).update(create_user_id=o_id)          # 组件库


                        code = 200
                        msg = '转接成功'
                        transfer_obj.whether_transfer_successful=4

                    else:
                        code = 301
                        msg = json.loads(form_obj.errors.as_json())
                transfer_obj.save()
            else:
                code = 301
                msg = '已过期, 请重新获取二维码'
            response.code = code
            response.msg = msg

        # 是否接受 团队邀请
        elif oper_type == 'accept_team_invitationss':
            new_user_id = request.POST.get('new_user_id') # 受邀请人ID
            parent_id = request.POST.get('parent_id') # 父级用户ID
            timestamp = request.POST.get('time_stamp') # 时间戳
            refused_invite = request.POST.get('refused_invite') # 拒绝邀请

            objs = models.InviteTheChild.objects.filter(
                parent_id=parent_id,
                child_id=new_user_id,
                timestamp=timestamp
            ).order_by('-create_datetime')
            obj = objs[0]
            if objs:
                if refused_invite:
                    obj.whether_transfer_successful = 5 # 拒绝
                    msg = '已拒绝'

                else:
                    user_is_exists = request.POST.get('user_is_exists') # 是否已有用户 如果有 则删除所有数据

                    models.UserProfile.objects.filter(id=new_user_id).update(inviter_id=parent_id)

                    if user_is_exists: # 删除所有数据
                        models.CustomerOfficialNumber.objects.filter(user_id=new_user_id).delete()
                        models.ClientApplet.objects.filter(user_id=new_user_id).delete()
                        models.PhotoLibrary.objects.filter(create_user_id=new_user_id).delete()
                        models.PhotoLibraryGroup.objects.filter(create_user_id=new_user_id).delete()
                        models.Page.objects.filter(create_user_id=new_user_id).delete()
                        models.PageGroup.objects.filter(create_user_id=new_user_id).delete()
                        models.Template.objects.filter(create_user_id=new_user_id).delete()
                        models.TemplateClass.objects.filter(create_user_id=new_user_id).delete()
                        models.CompomentLibrary.objects.filter(create_user_id=new_user_id).delete()
                        models.CompomentLibraryClass.objects.filter(create_user_id=new_user_id).delete()
                    msg = '已接受'
                    obj.whether_transfer_successful = 4

                obj.save()
                code = 200
            else:
                code = 301
                msg = '已过期, 请重新扫描二维码'

            response.code = code
            response.msg = msg

        # 删除团队成员
        elif oper_type == 'delete_team_members':
            form_data = {
                'o_id': o_id,
                'user_id': user_id
            }
            form_obj = DeleteTeamMembers(form_data)
            if form_obj.is_valid():
                user_id = form_obj.cleaned_data.get('user_id')
                o_id = form_obj.cleaned_data.get('o_id')

                models.UserProfile.objects.filter(id=o_id).update(
                    inviter_id=None
                )
                response.code = 200
                response.msg = '删除成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 修改企业名称
        elif oper_type == 'modify_enterprise_name':
            template_id = request.POST.get('template_id')
            enterprise_name = request.POST.get('enterprise_name')
            models.Template.objects.filter(id=template_id).update(enterprise_name=enterprise_name)
            response.code = 200
            response.msg = '修改成功'


    else:

        # 获取团队成员
        if oper_type == 'acquire_team_members':
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                    'name': '__contains',
                }

                q = conditionCom(request, field_dict)
                objs = models.UserProfile.objects.filter(q, inviter_id=user_id).order_by(order)
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    ret_data.append({
                        'id': obj.id,
                        'name': base64_encryption.b64decode(obj.name),
                        'role_id': obj.role_id,
                        'role_name': obj.role.name,
                        'head_portrait': obj.head_portrait,
                        'sex_id': obj.sex,
                        'sex': obj.get_sex_display(),
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })

                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'data_count': count,
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)


# 获取用户信息
def get_userinfo(request):
    response = Response.ResponseObj()
    if request.method == "GET":

        token = request.GET.get('token')
        objs = models.UserProfile.objects.filter(token=token)

        if objs:
            obj = objs[0]
            response.code = 200
            response.data = {
                'id': obj.id,
                'username': obj.username,
                'head_portrait': obj.head_portrait
            }
        else:
            response.code = 402
            response.msg = "token异常"
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)
