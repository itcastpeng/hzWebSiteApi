from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.article_management import AddForm, UpdateForm, SelectForm
import json

# 文章
@account.is_token(models.UserProfile)
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


@account.is_token(models.UserProfile)
def article_management_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    form_data = {
        'o_id': o_id,
        'create_user_id': user_id,
        'article_content': request.POST.get('article_content'),     # 文章内容
        'article_title': request.POST.get('article_title'),         # 文章标题
        'thumbnail': request.POST.get('thumbnail'),                 # 缩略图
        'template_id': request.POST.get('template_id'),             # 模板ID
    }
    if request.method == "POST":

        # 添加文章数据
        if oper_type == "add":
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                template_id = forms_obj.cleaned_data.get('template_id')
                article_content = forms_obj.cleaned_data.get('article_content')
                article_title = forms_obj.cleaned_data.get('article_title')
                thumbnail = forms_obj.cleaned_data.get('thumbnail')

                obj = models.Article.objects.create(
                    article_content=article_content,
                    article_title=article_title,
                    thumbnail=thumbnail,
                    template_id=template_id,
                )
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            objs = models.Article.objects.filter(id=o_id)
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
                article_content = forms_obj.cleaned_data['article_content']
                article_title = forms_obj.cleaned_data['article_title']
                thumbnail = forms_obj.cleaned_data['thumbnail']

                # 更新数据
                models.Article.objects.filter(id=o_id).update(
                    article_content=article_content,
                    article_title=article_title,
                    thumbnail=thumbnail,
                )
                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
