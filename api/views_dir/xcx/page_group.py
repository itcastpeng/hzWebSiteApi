
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.xcx.page_group import SelectForm
import json


# @account.is_token(models.UserProfile)
def page_group(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'template_id': '',
                'name': '__contains',
                'create_datetime': '',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.PageGroup.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            default_page_id = None
            for obj in objs:
                # 获取分组下面的页面数据
                page_objs = obj.page_set.all()
                page_data = []
                for page_obj in page_objs:
                    if not default_page_id:
                        default_page_id = page_obj.id
                    page_data.append({
                        'id': page_obj.id,
                        'name': page_obj.name
                    })

                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'page_data': page_data,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'default_page_id': default_page_id,
            }
            response.note = {
                'id': "页面分组id",
                'name': '页面分组名称',
                'create_datetime': '创建时间',
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


