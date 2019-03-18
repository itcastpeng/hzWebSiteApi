# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse

from publicFunc.condition_com import conditionCom
from api.forms.small_shop import SelectForm, AddGoodForm, UpdateGoodForm
import json


# token验证 微店展示模块
@account.is_token(models.Userprofile)
def small_shop(request):
    response = Response.ResponseObj()
    # user_id = request.GET.get('user_id')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'goods_classify__oper_user_id': '',  # 查看的谁的微店
                'goods_classify_id': '',
                'goods_name': '__contains',
                'create_datetime': '',
                'goods_status': '',
            }
            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.Goods.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:

                # try:
                #     goods_picture = eval(obj.goods_picture)
                # except Exception:
                #     goods_picture = obj.goods_picture

                # print('obj.goods_describe----> ', type(eval(obj.goods_describe)), obj.goods_describe)
                try:
                    goods_describe = eval(obj.goods_describe)
                except Exception:
                    goods_describe = obj.goods_describe

                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'goods_classify_id': obj.goods_classify_id,  # 分类ID
                    'goods_classify': obj.goods_classify.goods_classify,  # 分类名称
                    'goods_name': obj.goods_name,  # 商品名称
                    'price': obj.price,  # 商品价格
                    'inventory': obj.inventory,  # 商品库存
                    'freight': obj.freight,  # 商品运费
                    'goods_describe': goods_describe,  # 商品描述
                    'point_origin': obj.point_origin,  # 商品发货地
                    'goods_status_id': obj.goods_status,  # 商品状态ID
                    'goods_status': obj.get_goods_status_display(),  # 商品状态
                    # 'goods_picture': goods_picture,  # 商品图片
                    'cover_img': obj.cover_img,  # 商品封面图片
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })

            goods_status_list = []
            for i in models.Goods.goods_status_choices:
                goods_status_list.append({
                    'id': i[0],
                    'name': i[1]
                })

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'goods_status_list': goods_status_list,
            }
            response.note = {
                'id': "文章id",
                'goods_classify': '商品分类',
                'goods_name': '分类名称',
                'price': '商品价格',
                'inventory': '商品库存',
                'freight': '商品运费',
                'goods_describe': '商品描述',
                'point_origin': '商品发货地',
                'goods_status': '商品状态',
                # 'goods_picture': '商品图片',
                'create_datetime': '商品创建时间',
            }
        else:
            response.code = 301
            response.data = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"
    print(response.data)
    return JsonResponse(response.__dict__)


# 微店增删改
# token验证
@account.is_token(models.Userprofile)
def small_shop_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 修改微店 静态横图
        if oper_type == "update_small_shop_info":
            small_shop_image = request.POST.get('small_shop_image')
            small_shop_avator = request.POST.get('small_shop_avator')
            small_shop_name = request.POST.get('small_shop_name')
            objs = models.Userprofile.objects.filter(id=user_id)
            if objs:
                objs.update(
                    small_shop_image=small_shop_image,
                    small_shop_name=small_shop_name,
                    small_shop_avator=small_shop_avator,
                )
                response.code = 200
                response.msg = '修改成功'
            else:
                response.code = 301
                response.msg = '非法用户'

        # 添加商品
        elif oper_type == "add_good":
            form_data = {
                'create_user_id': user_id,
                'goods_classify_id': request.POST.get('goods_classify_id'),  # 商品分类
                'goods_name': request.POST.get('goods_name'),  # 商品名称
                'price': request.POST.get('price'),  # 商品价格
                'inventory': request.POST.get('inventory'),  # 库存
                'freight': request.POST.get('freight', 0),  # 运费
                'goods_describe': request.POST.get('goods_describe'),  # 商品描述
                'point_origin': request.POST.get('point_origin'),  # 发货地
                'goods_status': request.POST.get('goods_status', 2),  # 商品状态
                # 'goods_picture': request.POST.get('goods_picture'),  # 商品图片
                'cover_img': request.POST.get('cover_img'),  # 封面图片
            }
            print('form_data-------> ', form_data)

            forms_obj = AddGoodForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                form_obj = forms_obj.cleaned_data
                obj = models.Goods.objects.create(**{
                    'goods_classify_id': form_obj.get('goods_classify_id'),
                    'goods_name': form_obj.get('goods_name'),
                    'price': form_obj.get('price'),
                    'inventory': form_obj.get('inventory'),
                    'freight': form_obj.get('freight'),
                    'goods_describe': form_obj.get('goods_describe'),
                    'point_origin': form_obj.get('point_origin'),
                    'goods_status': form_obj.get('goods_status'),
                    # 'goods_picture': form_obj.get('goods_picture'),
                    'cover_img': form_obj.get('cover_img')
                })
                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改商品
        elif oper_type == "update_good":
            form_data = {
                'o_id': o_id,
                'create_user_id': user_id,
                'goods_classify_id': request.POST.get('goods_classify_id'),  # 商品分类
                'goods_name': request.POST.get('goods_name'),  # 商品名称
                'price': request.POST.get('price'),  # 商品价格
                'inventory': request.POST.get('inventory'),  # 库存
                'freight': request.POST.get('freight', 0),  # 运费
                'goods_describe': request.POST.get('goods_describe'),  # 商品描述
                'point_origin': request.POST.get('point_origin'),  # 发货地
                'goods_status': request.POST.get('goods_status', 2),  # 商品状态
                # 'goods_picture': request.POST.get('goods_picture'),  # 商品图片
                'cover_img': request.POST.get('cover_img'),  # 商品图片
            }

            forms_obj = UpdateGoodForm(form_data)
            if forms_obj.is_valid():
                print('验证通过')
                form_obj = forms_obj.cleaned_data
                models.Goods.objects.filter(id=o_id).update(**{
                    'goods_classify_id': form_obj.get('goods_classify_id'),
                    'goods_name': form_obj.get('goods_name'),
                    # 'price': form_obj.get('price'),
                    'inventory': form_obj.get('inventory'),
                    # 'freight': form_obj.get('freight'),
                    'goods_describe': form_obj.get('goods_describe'),
                    'point_origin': form_obj.get('point_origin'),
                    'goods_status': form_obj.get('goods_status'),
                    # 'goods_picture': form_obj.get('goods_picture'),
                    'cover_img': form_obj.get('cover_img')
                })
                response.code = 200
                response.msg = "修改成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除商品
        elif oper_type == "delete_good":
            objs = models.Goods.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'

    else:

        # 查询微店资料
        if oper_type == 'get_small_shop_info':
            objs = models.Userprofile.objects.filter(id=user_id)
            if objs:
                obj = objs[0]
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'small_shop_avator': obj.small_shop_avator,
                    'small_shop_name': obj.small_shop_name,
                    'small_shop_image': obj.small_shop_image,
                }
                response.node = {
                    'small_shop_avator': '微店头像',
                    'small_shop_name': '微店名称',
                    'small_shop_image': '微店横图',
                }
            else:
                response.code = 301
                response.msg = '非法用户'
        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)


# @account.is_token(models.Customer)
def customer_small_shop(request):
    response = Response.ResponseObj()
    # user_id = request.GET.get('user_id')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'goods_classify__oper_user_id': '',  # 查看的谁的微店
                'goods_classify_id': '',
                'goods_name': '__contains',
                'create_datetime': '',
                'goods_status': '',
            }
            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.Goods.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:

                # try:
                #     goods_picture = eval(obj.goods_picture)
                # except Exception:
                #     goods_picture = obj.goods_picture

                # print('obj.goods_describe----> ', type(eval(obj.goods_describe)), obj.goods_describe)
                try:
                    goods_describe = eval(obj.goods_describe)
                except Exception:
                    goods_describe = obj.goods_describe

                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'goods_classify_id': obj.goods_classify_id,  # 分类ID
                    'goods_classify': obj.goods_classify.goods_classify,  # 分类名称
                    'goods_name': obj.goods_name,  # 商品名称
                    'price': obj.price,  # 商品价格
                    'inventory': obj.inventory,  # 商品库存
                    'freight': obj.freight,  # 商品运费
                    'goods_describe': goods_describe,  # 商品描述
                    'point_origin': obj.point_origin,  # 商品发货地
                    'goods_status_id': obj.goods_status,  # 商品状态ID
                    'goods_status': obj.get_goods_status_display(),  # 商品状态
                    # 'goods_picture': goods_picture,  # 商品图片
                    'cover_img': obj.cover_img,  # 商品封面图片
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })

            goods_status_list = []
            for i in models.Goods.goods_status_choices:
                goods_status_list.append({
                    'id': i[0],
                    'name': i[1]
                })

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'goods_status_list': goods_status_list,
            }
            response.note = {
                'id': "文章id",
                'goods_classify': '商品分类',
                'goods_name': '分类名称',
                'price': '商品价格',
                'inventory': '商品库存',
                'freight': '商品运费',
                'goods_describe': '商品描述',
                'point_origin': '商品发货地',
                'goods_status': '商品状态',
                # 'goods_picture': '商品图片',
                'create_datetime': '商品创建时间',
            }
        else:
            response.code = 301
            response.data = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"
    print(response.data)
    return JsonResponse(response.__dict__)