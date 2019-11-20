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
            experience = request.GET.get('experience')      # 是否是体验版,该字段有值则为体验版
            template_objs = models.Template.objects.filter(id=template_id)
            if template_objs:
                tab_bar_data = template_objs[0].tab_bar_data
                if experience:  # 如果是体验版,则获取开发数据
                    tab_bar_data = template_objs[0].tab_bar_data_dev

                response.code = 200
                response.data = {
                    'data': tab_bar_data
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
            experience = request.GET.get('experience')      # 是否是体验版,该字段有值则为体验版
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
                    page_data = objs[0].data
                    if experience:  # 如果是体验版,则获取开发数据
                        page_data = objs[0].data_dev
                    response.data = {
                        'page_data': page_data
                    }
                    response.note = {
                        'page_data': "页面数据"
                    }
            else:
                response.code = 402
                response.msg = "请求异常"

        # 查询场景值
        elif oper_type == 'query_triggered_logging_scenario':
            template_id = request.GET.get('template_id')
            objs = models.Template.objects.filter(id=template_id)
            if objs:
                obj = objs[0]
                ret_data = {
                    'name_card_details': obj.name_card_details,
                    'name_save_address_book': obj.name_save_address_book,
                    'name_make_phone_call': obj.name_make_phone_call,
                    'name_my': obj.name_my,
                    'name_article_details': obj.name_article_details,
                    'name_service_details': obj.name_service_details,
                    'name_share_page': obj.name_share_page,

                    'phone_card_details': obj.phone_card_details,
                    'phone_save_address_book': obj.phone_save_address_book,
                    'phone_make_phone_call': obj.phone_make_phone_call,
                    'phone_my': obj.phone_my,
                    'phone_article_details': obj.phone_article_details,
                    'phone_service_details': obj.phone_service_details,
                    'phone_submit_form': obj.phone_submit_form,
                    'phone_submit_article': obj.phone_submit_article,
                    'phone_submit_service_order': obj.phone_submit_service_order,
                    'phone_vote': obj.phone_vote,
                    'phone_share_page': obj.phone_share_page,
                }
                response.code = 200
                response.msg = '查询成功'
                response.data = ret_data
            else:
                response.code = 301
                response.msg = '模板错误'
            response.note = {
                'name_card_details': '进入名片详情',
                'name_save_address_book': '保存通讯录',
                'name_make_phone_call': '拨打电话',
                'name_my': '我的',
                'name_article_details': '文章详情',
                'name_service_details': '服务详情',
                'name_share_page': '分享页面',

                'phone_card_details': '进入名片详情',
                'phone_save_address_book': '保存通讯录',
                'phone_make_phone_call': '拨打电话',
                'phone_my': '我的',
                'phone_article_details': '文章详情',
                'phone_service_details': '服务详情',
                'phone_submit_form': '提交表单',
                'phone_submit_article': '提交文章',
                'phone_submit_service_order': '提交服务订单',
                'phone_vote': '投票',
                'phone_share_page': '分享页面',
            }
    return JsonResponse(response.__dict__)

