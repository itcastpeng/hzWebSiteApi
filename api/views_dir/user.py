from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.user import SelectForm, UpdateRoleForm, TransferAllUserInformation
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
            objs = models.UserProfile.objects.filter(q, openid__isnull=False).order_by(order)
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

        # 修改用户角色
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

        # 转接 用户所有信息
        elif oper_type == 'transfer_all_user_information':
            cancel_transfer = request.POST.get('cancel_transfer') # 拒绝交接
            form_data = {
                'user_id':user_id,
                'o_id': o_id,
            }
            transfer_objs = models.Transfer.objects.filter(
                speak_to_people_id=user_id,
                by_connecting_people_id=o_id
            ).order_by('-create_datetime')

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

                    models.TemplateClass.objects.filter(create_user_id=user_id).update(create_user_id=o_id)
                    models.Template.objects.filter(create_user_id=user_id).update(create_user_id=o_id)
                    models.PageGroup.objects.filter(create_user_id=user_id).update(create_user_id=o_id)
                    models.Page.objects.filter(create_user_id=user_id).update(create_user_id=o_id)
                    models.PhotoLibraryGroup.objects.filter(create_user_id=user_id).update(create_user_id=o_id)
                    models.PhotoLibrary.objects.filter(create_user_id=user_id).update(create_user_id=o_id)
                    models.CompomentLibraryClass.objects.filter(create_user_id=user_id).update(create_user_id=o_id)
                    models.CompomentLibrary.objects.filter(create_user_id=user_id).update(create_user_id=o_id)
                    models.CustomerOfficialNumber.objects.filter(user_id=user_id).update(user_id=o_id)
                    models.ClientApplet.objects.filter(user_id=user_id).update(user_id=o_id)

                    code = 200
                    msg = '转接成功'
                    transfer_obj.whether_transfer_successful=4

                else:
                    code = 301
                    msg = json.loads(form_obj.errors.as_json())
            transfer_obj.save()
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
            if refused_invite:
                obj.whether_transfer_successful = 5 # 拒绝
                msg = '已拒绝'
                code = 301

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
                code = 200

            response.code = code
            response.msg = msg

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
                }

                q = conditionCom(request, field_dict)

                print('q -->', q)
                objs = models.UserProfile.objects.filter(q, openid__isnull=False).order_by(order)
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


        #
        elif oper_type == '':
            pass

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
