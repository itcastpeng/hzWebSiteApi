# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse

from publicFunc.condition_com import conditionCom
from api.forms.xcx.template import GetTabbarDataForm, GetPageDataForm
import json
from api.views_dir.page import page_base_data


@account.is_token(models.Customer)
def template(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "GET":
        if oper_type == "get_tabbar_data":
            form_data = {
                'template_id': request.GET.get('template_id'),
            }
            print('form_data -->', form_data)
            forms_obj = GetTabbarDataForm(form_data)
            if forms_obj.is_valid():
                template_id = forms_obj.cleaned_data.get('template_id')
                objs = models.Template.objects.filter(id=template_id)

                if objs:
                    models.ViewCustomerSmallApplet.objects.create(user_id=user_id, template_id=template_id) # 记录日志

                    # 首页页面对象
                    first_page_obj = models.Page.objects.filter(page_group__template_id=template_id)[0]
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'tab_bar_data': objs[0].tab_bar_data,
                        'first_page_id': first_page_obj.id,
                    }
                    response.note = {
                        'tab_bar_data': "底部导航数据",
                        'first_page_id': "首页页面id",
                    }
            else:
                response.code = 402
                response.msg = "请求异常"
                response.data = json.loads(forms_obj.errors.as_json())

        # 获取页面数据
        elif oper_type == "get_page_data":
            form_data = {
                'page_id': request.GET.get('page_id'),
            }
            print('form_data -->', form_data)
            forms_obj = GetPageDataForm(form_data)
            if forms_obj.is_valid():
                page_id = forms_obj.cleaned_data.get('page_id')
                objs = models.Page.objects.filter(id=page_id)

                if objs:
                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'page_data': objs[0].data,
                    }
                    response.note = {
                        'page_data': "页面数据"
                    }
            else:
                response.code = 402
                response.msg = "请求异常"
    return JsonResponse(response.__dict__)

