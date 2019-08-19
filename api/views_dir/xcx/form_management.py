from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.xcx.form_management import AddForm, UpdateForm, SelectForm
from publicFunc.role_choice import admin_list
import json

# 模板 表单
@account.is_token(models.UserProfile)
def form_management(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'template_id': '',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.ReservationForm.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                try:
                    form_content = json.loads(obj.form_content)
                except Exception:
                    form_content = obj.form_content

                ret_data.append({
                    'id': obj.id,
                    'template_id': obj.template_id,
                    'template_name': obj.template.name,
                    'form_content': form_content,
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

            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


@account.is_token(models.UserProfile)
def form_management_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    form_data = {
        'o_id': o_id,
        'create_user_id': user_id,
        'form_content': request.POST.get('form_content'),
        'template_id': request.POST.get('template_id'),
    }
    if request.method == "POST":

        # 添加表单数据
        if oper_type == "add":
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                template_id = forms_obj.cleaned_data.get('template_id')
                form_content = forms_obj.cleaned_data.get('form_content')

                obj = models.ReservationForm.objects.create(
                    template_id=template_id,
                    form_content=form_content,
                )
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            objs = models.ReservationForm.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"

            else:
                response.code = 302
                response.msg = '删除ID不存在'

        elif oper_type == "update":
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data['o_id']
                form_content = forms_obj.cleaned_data['form_content']

                # 更新数据
                models.ReservationForm.objects.filter(id=o_id).update(form_content=form_content)
                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
