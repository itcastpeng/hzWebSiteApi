# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse

from publicFunc.condition_com import conditionCom
from api.forms.xcx.template import SelectForm
import json
from api.views_dir.page import page_base_data


@account.is_token(models.ClientUserProfile)
def template(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        form_data = {
            'template_id': request.GET.get('template_id'),
        }
        print('form_data -->', form_data)
        forms_obj = SelectForm(form_data)
        if forms_obj.is_valid():
            template_id = forms_obj.cleaned_data.get('template_id')
            objs = models.Template.objects.filter(id=template_id)

            if objs:
                #  查询成功 返回200 状态码
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'tab_bar_data': objs[0].tab_bar_data,
                }
                response.note = {
                    'tab_bar_data': "底部导航数据"
                }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)

