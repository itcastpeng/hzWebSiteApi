from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.article_management import AddForm, UpdateForm, SelectForm
import json

# 文章
# @account.is_token(models.UserProfile)
def article_management(request):
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
                'article_class_id': '',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.Article.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                ret_data.append({
                    'id': obj.id,
                    'template_id': obj.template_id,
                    'thumbnail': obj.thumbnail,
                    'article_introduction': obj.article_introduction,
                    'article_title': obj.article_title,
                    'template_name': obj.template.name,
                    'article_content': obj.article_content,
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

