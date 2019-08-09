from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.user import SelectForm, UpdateRoleForm
import datetime, re, json
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
                    'role': obj.role_id,
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
    # print('request.POST -->', request.POST)
    if request.method == "POST":
        # 设置推荐分类
        if oper_type == "update_recommend_classify":
            classify_id = request.POST.getlist('classify_id[]')
            if classify_id:
                recommend_classify_list = [int(i) for i in classify_id]
                print("recommend_classify_list -->", recommend_classify_list)
                user_obj = models.UserProfile.objects.get(id=user_id)
                user_obj.recommend_classify = recommend_classify_list
                response.code = 200
                response.msg = "设置成功"
            else:
                response.code = 301
                response.msg = "分类id传参异常"

        # 修改头像
        elif oper_type == "update_head_portrait":
            img_path = request.POST.get('img_path')
            if img_path:
                models.UserProfile.objects.filter(id=user_id).update(set_avator=img_path)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "头像不能传参异常"

        # 修改姓名
        elif oper_type == "update_name":
            name = request.POST.get('name')
            if name:
                name = base64_encryption.b64encode(name)
                models.UserProfile.objects.filter(id=user_id).update(name=name)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "姓名传参异常"

        # 修改手机号
        elif oper_type == "update_phone_number":
            phone_number = request.POST.get('phone_number')
            flag = re.match(r"^1\d{10}$", phone_number)      # 验证是否以1开头，并且是11位的数字
            if phone_number and flag:
                models.UserProfile.objects.filter(id=user_id).update(phone_number=phone_number)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "手机号传参异常"

        # 修改微信二维码
        elif oper_type == "update_qr_code":
            qr_code = request.POST.get('qr_code')
            if qr_code:
                models.UserProfile.objects.filter(id=user_id).update(qr_code=qr_code)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "微信二维码传参异常"

        # 修改个性签名
        elif oper_type == "update_signature":
            signature = request.POST.get('signature')
            if signature:
                models.UserProfile.objects.filter(id=user_id).update(signature=signature)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "个性签名传参异常"

        # 修改文章底部是否显示产品
        elif oper_type == "update_show_product":
            show_product = request.POST.get('show_product')
            flag = re.match(r"^[01]$", show_product)

            if show_product and flag:
                models.UserProfile.objects.filter(id=user_id).update(show_product=int(show_product))
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "是否显示产品传参异常"

        # 修改用户角色
        elif oper_type == 'update_role':
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

    else:

        if oper_type == "member_info":
            obj = models.UserProfile.objects.get(id=user_id)

            # vip 类型
            vip_type = obj.get_vip_type_display()

            # 时间对象 - 年月日时分秒
            now_datetime_obj = datetime.datetime.now()

            # 时间对象 - 年月日
            now_date_obj = datetime.date(now_datetime_obj.year, now_datetime_obj.month, now_datetime_obj.day)

            # 计算剩余天数
            remaining_days = (obj.overdue_date - now_date_obj).days

            # 如果已经过期，则剩余过期时间为0，vip类型为vip已过期
            if remaining_days <= 0:
                remaining_days = 0
                vip_type = "vip已过期"

            response.code = 200
            response.data = {
                'vip_type': vip_type,
                'overdue_date': obj.overdue_date.strftime('%Y-%m-%d'),
                'remaining_days': remaining_days
            }

            response.note = {
                'vip_type': "vip类型",
                'overdue_date': "有效期至",
                'remaining_days': "剩余天数"
            }




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
                # 'token': obj.token,
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
