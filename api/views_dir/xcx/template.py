from api import models
from publicFunc import Response
from django.http import JsonResponse
from api.forms.xcx.template import GetTabbarDataForm, GetPageDataForm
import json


# @account.is_token(models.Customer)
def template(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "GET":
        template_id = request.GET.get('template_id')

        # 获取底部导航数据
        if oper_type == "get_tab_bar_data":
            # 获取需要修改的信息
            template_id = request.GET.get('template_id')
            template_objs = models.Template.objects.filter(id=template_id)
            if template_objs:
                response.code = 200
                response.data = {
                    'data': template_objs[0].tab_bar_data
                }
            else:
                response.code = 301
                response.msg = "模板id异常"


        elif oper_type == "get_tabbar_data":
            form_data = {
                'template_id': template_id,
            }
            print('form_data -->', form_data)
            forms_obj = GetTabbarDataForm(form_data)
            if forms_obj.is_valid():
                template_id = forms_obj.cleaned_data.get('template_id')
                objs = models.Template.objects.filter(id=template_id)

                if objs:

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

