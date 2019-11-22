from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.message_inform import AddForm, UpdateForm, SelectForm
import json


# 消息通知管理
def save_msg_inform(user_id, msg, is_send_admin=False, only_send_admin=False):
    """

    :param user_id:         发送消息通知给谁
    :param msg:             消息内容
    :param is_send_admin:   是否发送给管理员角色
    :param only_send_admin:   是否只发送给管理员角色
    :return:
    """

    if not only_send_admin:
        models.MessageInform.objects.create(
            create_user_id=user_id,
            msg=msg
        )

    # 发消息给管理员
    if is_send_admin:
        admin_user_id_data = models.UserProfile.objects.filter(role_id__in=[8]).values('id')
        for admin_user_id in admin_user_id_data:
            models.MessageInform.objects.create(
                create_user_id=admin_user_id['id'],
                msg=msg
            )


# cerf  token验证 角色管理
@csrf_exempt
@account.is_token(models.UserProfile)
def message_inform(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            user_id = forms_obj.cleaned_data['user_id']
            order = request.GET.get('order', '-create_datetime')

            field_dict = {
                'id': '',
                'status': '',
            }
            q = conditionCom(request, field_dict)
            objs = models.MessageInform.objects.filter(q).filter(create_user_id=user_id).order_by(order)
            count = objs.count()
            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:

                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'msg': obj.msg,  # 消息数据
                    'status': obj.status,  # 查阅状态
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
            response.data = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.UserProfile)
def message_inform_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        user_id = request.GET.get('user_id')

        # 添加
        if oper_type == "add":
            pass
            # form_data = {
            #     'create_user_id': user_id,                        # 操作人ID
            #     'template_id': request.POST.get('template_id'),               # 模板id
            #     'data': request.POST.get('data'),               # 表单数据
            # }
            # #  创建 form验证 实例（参数默认转成字典）
            # forms_obj = AddForm(form_data)
            # if forms_obj.is_valid():
            #     obj = models.Form.objects.create(**{
            #         'template_id': forms_obj.cleaned_data.get('template_id'),
            #         'data': forms_obj.cleaned_data.get('data'),
            #         'create_user_id': forms_obj.cleaned_data.get('create_user_id'),
            #     })
            #
            #     response.code = 200
            #     response.msg = "添加成功"
            #     response.data = {'testCase': obj.id}
            # else:
            #     print("验证不通过")
            #     response.code = 301
            #     response.msg = json.loads(forms_obj.errors.as_json())

        # 修改
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'status': request.POST.get('status'),               # 模板id
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                # status = forms_obj.cleaned_data['status']  # 操作人ID
                #  查询数据库  用户id
                objs = models.MessageInform.objects.filter(
                    id=o_id,
                )
                #  更新 数据
                if objs:
                    objs.update(
                        status=True,
                    )
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = '不存在的数据'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # # 删除
        # elif oper_type == "delete":
        #     # 删除 ID
        #     objs = models.Form.objects.filter(id=o_id)
        #     if objs:
        #         objs.delete()
        #         response.code = 200
        #         response.msg = "删除成功"
        #     else:
        #         response.code = 302
        #         response.msg = '删除ID不存在'

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
