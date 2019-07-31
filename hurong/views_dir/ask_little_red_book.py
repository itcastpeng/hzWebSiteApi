from hurong import models
from publicFunc import Response, account
from django.http import JsonResponse
from hurong.forms.public_form import SelectForm
from publicFunc.condition_com import conditionCom
from django.db.models import Q
import json




@account.is_token(models.UserProfile)
def ask_little_red_book(request):
    response = Response.ResponseObj()
    if request.method == 'POST':
        pass
        # objs = models.noteAssociationScreenshot.objects.filter(
        #     create_datetime__gte='2019-07-01 00:00:00'
        # )
        # print(objs.query)


    else:
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            field_dict = {
                'id': '',
                'comments_status': '',
                'request_type': '',
                'xhs_user_id': '',
                'status': '',
                'request_url': '__contains',
            }

            q = conditionCom(request, field_dict)
            order = request.GET.get('order', '-create_datetime')

            objs = models.AskLittleRedBook.objects.filter(q).order_by(order)
            error = request.GET.get('error') # 0全部  1：非200 2：200
            if error:
                if error in [1, '1']:  # 查询异常的
                    objs = objs.exclude(response_data__contains=200)

                else:
                    objs = objs.filter(response_data__contains=200)



            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                get_request_parameter = obj.get_request_parameter
                if get_request_parameter:
                    get_request_parameter = eval(get_request_parameter)

                post_request_parameter = obj.post_request_parameter
                if post_request_parameter:
                    post_request_parameter = eval(post_request_parameter)

                response_data = obj.response_data
                if response_data:
                    response_data = eval(response_data)

                ret_data.append({
                    'request_url': obj.request_url,
                    'get_request_parameter': get_request_parameter,
                    'post_request_parameter': post_request_parameter,
                    'response_data': response_data,
                    'request_type_id': obj.request_type,
                    'request_type': obj.get_request_type_display(),
                    'status_id': obj.status,
                    'status': obj.get_status_display(),
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'count': count,
                'status_choices': [{'id': i[0], 'name': i[1]} for i in models.AskLittleRedBook.status_choices],
                'request_type_choices': [{'id': i[0], 'name': i[1]} for i in models.AskLittleRedBook.request_type_choices]
            }

        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)



# 栏目异常数量
@account.is_token(models.UserProfile)
def abnormal_number_columns(request):
    response = Response.ResponseObj()
    if request.method == 'POST':
        pass

    else:
        exclude_list = [22, 10, 6]
        yidongshebei_num = models.XiaohongshuPhone.objects.filter(
            name__isnull=False,
            status=2
        ).exclude(id__in=exclude_list).count()

        biji_num = models.XiaohongshuBiji.objects.filter(
            status=3
        ).count()

        huifupinglun_num = models.commentResponseForm.objects.filter(
            comment_completion_time__isnull=True
        ).count()

        sixin_num = models.XiaohongshuDirectMessagesReply.objects.filter(
            status=1
        ).count()

        delete_little_num = models.littleRedBookReviewForm.objects.filter(
            delete=2
        ).count()

        unregistered_num = models.XiaohongshuUserProfileRegister.objects.filter(
            is_register=False
        ).count()

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'yidongshebei_num': yidongshebei_num,
            'biji_num': biji_num,
            'huifupinglun_num': huifupinglun_num,
            'sixin_num': sixin_num,
            'delete_little_num': delete_little_num,
            'unregistered_num': unregistered_num,
        }
        response.note = {
            'yidongshebei_num': '移动设备异常总数',
            'biji_num': '笔记异常总数',
            'huifupinglun_num': '待回复评论总数',
            'delete_little_num': '待删除的评论总数',
            'sixin_num': '待回复私信总数',
            'unregistered_num': '未注册数量',
        }


    return JsonResponse(response.__dict__)


# 查询告警信息
# @account.is_token(models.UserProfile)
def query_mobile_equipment_alarm_information(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        field_dict = {
            'id': '',
            'error_msg': '__contains',
            'status': '',
        }
        q = conditionCom(request, field_dict)
        order = request.GET.get('order', '-create_datetime')
        objs = models.MobileEquipmentAbnormalSendMessageEnterpriseRecord.objects.filter(q).order_by(order)
        count = objs.count()

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]

        ret_data = []
        for obj in objs:
            ret_data.append({
                'error_msg': obj.error_msg,
                'status_id': obj.status,
                'status': obj.get_status_display(),
                'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            })
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': ret_data,
            'count': count,
            'status_choices': [{'id':i[0], 'name': i[1]} for i in models.MobileEquipmentAbnormalSendMessageEnterpriseRecord.status_choices],
        }

    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)






















