from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from hurong.forms.role import AddForm, UpdateForm, SelectForm
from hurong.views_dir.permissions import init_data
import json


# cerf  token验证 角色管理
@csrf_exempt
@account.is_token(models.UserProfile)
def role(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)

            order = request.GET.get('order', '-create_datetime')
            user_id = request.GET.get('user_id')
            userObjs = models.UserProfile.objects.filter(id=user_id)

            field_dict = {
                'id': '',
                'name': '__contains',
                'create_date': '',
                'oper_user__username': '__contains',
            }
            q = conditionCom(request, field_dict)
            # print('q -->', q)
            objs = models.Role.objects.filter(q).order_by(order)
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:

                # 获取选中的id，然后组合成前端能用的数据
                permissionsData = []
                if obj.permissions:
                    permissionsList = [i['id'] for i in obj.permissions.values('id')]
                    if len(permissionsList) > 0:
                        permissionsData = init_data(selected_list=permissionsList)

                #  如果有oper_user字段 等于本身名字
                oper_user_username = ''
                oper_user_id = ''
                if obj.oper_user:
                    oper_user_id = obj.oper_user_id
                    oper_user_username = obj.oper_user.username

                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,  # 角色名称
                    'permissionsData': permissionsData,  # 角色权限
                    'oper_user_id': oper_user_id,  # 操作人ID
                    'oper_user__username': oper_user_username,  # 操作人
                    'create_date': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
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
            response.data = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.UserProfile)
def role_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        user_id = request.GET.get('user_id')

        # 添加角色
        if oper_type == "add":
            form_data = {
                'oper_user_id': request.GET.get('user_id'),  # 操作人ID
                'name': request.POST.get('name'),  # 角色名称
                'permissionsList': request.POST.get('permissionsList'),  # 角色权限
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                obj = models.Role.objects.create(**{
                    'name': forms_obj.cleaned_data.get('name'),
                    'oper_user_id': forms_obj.cleaned_data.get('oper_user_id'),
                })
                permissionsList = forms_obj.cleaned_data.get('permissionsList')
                print('permissionsList -->', permissionsList)
                obj.permissions = permissionsList
                obj.save()
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改角色
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),  # 角色名称
                'oper_user_id': request.GET.get('user_id'),  # 操作人ID
                'permissionsList': request.POST.get('permissionsList'),  # 角色权限
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']  # 角色名称
                oper_user_id = forms_obj.cleaned_data['oper_user_id']  # 操作人ID
                permissionsList = forms_obj.cleaned_data['permissionsList']  # 角色权限
                #  查询数据库  用户id
                objs = models.Role.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if objs:
                    objs.update(
                        name=name,
                        oper_user_id=oper_user_id,
                    )

                    objs[0].permissions = permissionsList

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = '不存在的数据'

            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除角色
        elif oper_type == "delete":
            # 删除 ID
            objs = models.Role.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                userObj = models.UserProfile.objects.get(
                    id=user_id,
                )
                if userObj.role_id == obj.id:
                    response.code = 301
                    response.msg = '不能删除自己角色'

                else:
                    if not models.UserProfile.objects.filter(
                        role_id__in=[o_id]
                    ):
                        objs.delete()
                        response.code = 200
                        response.msg = "删除成功"
                    else:
                        response.code = 301
                        response.msg = '该角色下存在用户'

            else:
                response.code = 302
                response.msg = '删除ID不存在'

    else:
        # 获取角色对应的权限
        if oper_type == "get_rules":

            objs = models.Role.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                rules_list = [i['name'] for i in obj.permissions.values('name')]
                print('dataList -->', rules_list)
                response.data = {
                    'rules_list': rules_list
                }

                response.code = 200
                response.msg = "查询成功"

        else:
            response.code = 402
            response.msg = "请求异常"


    return JsonResponse(response.__dict__)
