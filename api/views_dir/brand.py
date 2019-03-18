# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse

from publicFunc.condition_com import conditionCom
from api.forms.brand import AddForm, SelectForm
import json


# token验证 用户展示模块
@account.is_token(models.Userprofile)
def brand(request):
    response = Response.ResponseObj()
    # user_id = request.GET.get('user_id')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'name': '__contains',
                'classify_id': '__in',
                'create_user_id': '',
                'create_datetime': '',
            }
            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.Classify.objects.filter(create_user__isnull=False).filter(q).order_by(order)
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
                    'name': obj.name,
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
                'id': "品牌id",
                'title': "品牌名称",
                'create_datetime': "创建时间",
            }

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.Userprofile)
def brand_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'create_user_id': user_id,
                'name': request.POST.get('name'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                name = forms_obj.cleaned_data.get('name')

                # 判断需要添加的品牌名称是否存在，如果不存在则添加
                classify_objs = models.Classify.objects.filter(
                    create_user__isnull=False,
                    name=name
                )

                if classify_objs:   # 品牌分类已经存在
                    classify_id = classify_objs[0].id

                else:   # 品牌分类不存在
                    obj = models.Classify.objects.create(name=name, create_user_id=user_id)
                    print(obj.id)
                    classify_id = obj.id

                models.Userprofile.objects.get(id=user_id).brand_classify.add(classify_id)

                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': classify_id}
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            models.Userprofile.objects.get(id=user_id).brand_classify.remove(o_id)

            response.code = 200
            response.msg = "删除成功"

    else:
        # 获取我的品牌列表
        if oper_type == "get_brand_list":
            brand_objs = models.Userprofile.objects.get(id=user_id).brand_classify.all()

            # 返回的数据
            ret_data = []

            for obj in brand_objs:
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
            }

            response.note = {
                'id': "品牌id",
                'title': "品牌名称",
                'create_datetime': "创建时间",
            }

    return JsonResponse(response.__dict__)
