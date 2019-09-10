from hurong import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.package_management import AddForm, SelectForm, UpdateForm, DeleteForm
import requests, datetime, json


@account.is_token(models.UserProfile)
def package_management(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'package_type':'',
                'package_name':'__contains',
                'package_path':'__contains',
                'platform':'',
                'is_delete':'',
            }

            q = conditionCom(request, field_dict)

            objs = models.InstallationPackage.objects.filter(q, is_delete=0).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                ret_data.append({
                    'id': obj.id,
                    'package_type': obj.get_package_type_display(),
                    'package_type_id': obj.package_type,
                    'package_path': obj.package_path,
                    'package_name': obj.package_name,
                    'platform': obj.platform,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'package_type_choices': [{'id':i[0], 'name':i[1]} for i in models.InstallationPackage.package_type_choices]
            }

        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)



@account.is_token(models.UserProfile)
def package_management_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == "POST":
        form_data = {
            'oper_user_id': user_id,
            'package_type': request.POST.get('package_type'),
            'package_path': request.POST.get('package_path'),
            'package_name': request.POST.get('package_name'),
            'platform': request.POST.get('platform', 1),
        }

        # 添加
        if oper_type == "add":
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                models.InstallationPackage.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = '创建成功'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改安装包
        elif oper_type == 'update':
            form_data['o_id'] = o_id
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                cleaned_data = forms_obj.cleaned_data
                o_id = cleaned_data.get('o_id')

                objs = models.InstallationPackage.objects.filter(id=o_id)
                objs.update(**{
                    'package_type':cleaned_data.get('package_type'),
                    'package_name':cleaned_data.get('package_name'),
                    'platform':cleaned_data.get('platform'),
                    'package_path':cleaned_data.get('package_path'),
                    'oper_user_id':user_id,
                })
                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除安装包
        elif oper_type == 'delete':
            form_data['o_id'] = o_id
            forms_obj = DeleteForm(form_data)
            if forms_obj.is_valid():
                response.code = 200
                response.msg = '删除成功'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = "请求异常"

    else:

        # 获取安装包 最高的版本
        if oper_type == 'get_highest_version':
            package_type = request.GET.get('package_type', 1)
            platform = request.GET.get('platform', 1)

            objs = models.InstallationPackage.objects.filter(
                is_delete=0,
                package_type=package_type,
                platform=platform
            ).order_by('-id')
            if objs:
                obj = objs[0]
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'id': obj.id,
                    'package_type':obj.package_type,
                    'package_name':obj.package_name,
                    'package_path':obj.package_path,
                    'platform':obj.platform,
                }
            else:
                response.code = 301
                response.msg = '暂无安装包'

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
