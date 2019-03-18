from django import forms

from api import models
from django.db.models import Q

# from publicFunc import account
# import time

# 判断级别 最多不能超过三级 分类
# def groupTree(oper_user_id, parent_classify_id, data):
#     result_data = []
#     q = Q()
#     q.add(Q(oper_user_id=oper_user_id) & Q(id=parent_classify_id), Q.AND)
#     objs = models.GoodsClassify.objects.filter(q)
#     for obj in objs:
#
#         current_data = {
#             'id': obj.id,
#         }
#         data.append(obj.id)
#         if parent_classify_id:
#             children_data = groupTree(oper_user_id, obj.parent_classify_id, data)
#             current_data['children'] = children_data
#         result_data.append(current_data)
#
#     return result_data, data

# 商品分类添加
class AddForm(forms.Form):
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '创建人不能为空'
        }
    )

    goods_classify = forms.CharField(
        required=True,
        error_messages={
            'required': "分类名称不能为空"
        }
    )
    # parent_classify_id = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'required': "父级分类类型错误"
    #     }
    # )

    # 查询文章标题是否存在
    def clean_goods_classify(self):
        oper_user_id = self.data['oper_user_id']
        goods_classify = self.data['goods_classify']

        objs = models.GoodsClassify.objects.filter(
            oper_user_id=oper_user_id,
            goods_classify=goods_classify,
        )
        if objs:
            self.add_error('goods_classify', '分类名称已存在')
        else:
            if len(goods_classify) > 10:
                self.add_error('goods_classify', '名称不得大于10个字')
            else:
                return goods_classify

    # def clean_parent_classify_id(self):
    #     parent_classify_id = self.data.get('parent_classify_id')
    #     oper_user_id = self.data['oper_user_id']
    #     if parent_classify_id:
    #         objs = models.GoodsClassify.objects.filter(id=parent_classify_id)
    #         if not objs:
    #             self.add_error('parent_classify_id',  '上级分类不存在')
    #         else:
    #             data = []
    #             result_data, data = groupTree(oper_user_id, parent_classify_id, data)
    #             data_len = len(data)
    #             if data_len >= 2:
    #                 self.add_error('parent_classify_id', '分类不能超过两级')
    #             else:
    #                 return parent_classify_id

# 商品分类更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '分类id不能为空'
        }
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '创建人不能为空'
        }
    )
    goods_classify = forms.CharField(
        required=True,
        error_messages={
            'required': "分类名称不能为空"
        }
    )
    # parent_classify_id = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'required': "父级分类类型错误"
    #     }
    # )

    # 判断是否有该分类
    def clean_o_id(self):
        o_id = self.data.get('o_id')
        parent_classify_id = self.data.get('parent_classify_id')
        objs = models.GoodsClassify.objects.filter(id=o_id)
        if objs:
            if o_id == parent_classify_id:
                self.add_error('parent_classify_id', '父级分类不能选为自己')
            else:
                return o_id, objs
        else:
            self.add_error('o_id', '修改ID不存在')

    # 查询文章标题是否存在
    def clean_goods_classify(self):
        oper_user_id = self.data['oper_user_id']
        goods_classify = self.data['goods_classify']
        o_id = self.data.get('o_id')
        objs = models.GoodsClassify.objects.filter(
            oper_user_id=oper_user_id,
            goods_classify=goods_classify,
        ).exclude(id=o_id)
        if objs:
            self.add_error('goods_classify', '分类名称已存在')
        else:
            if len(goods_classify) > 10:
                self.add_error('goods_classify', '名称不得大于10个字')
            else:
                return goods_classify

    # def clean_parent_classify_id(self):
    #     parent_classify_id = self.data.get('parent_classify_id')
    #     if parent_classify_id:
    #         oper_user_id = self.data['oper_user_id']
    #         o_id = self.data.get('o_id')
    #         objs = models.GoodsClassify.objects.filter(id=parent_classify_id)
    #         if not objs:
    #             self.add_error('parent_classify_id',  '上级分类不存在')
    #         else:
    #             data = []
    #             result_data, data = groupTree(oper_user_id, parent_classify_id, data)
    #             data_len = len(data)
    #             if int(o_id) in data:
    #                 self.add_error('parent_classify_id', '选择该分类 容易造成数据混乱')
    #             else:
    #                 if data_len >= 3:
    #                     self.add_error('parent_classify_id', '分类不能超过三级')
    #                 else:
    #                     return parent_classify_id

# 商品分类删除
class DeleteForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章id不能为空'
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "标题不能为空"
        }
    )
    content = forms.CharField(
        required=True,
        error_messages={
            'required': "内容不能为空"
        }
    )

    # 查询文章标题是否存在
    def clean_o_id(self):
        create_user_id = self.data['create_user_id']
        o_id = self.data['o_id']  # 文章id

        objs = models.Article.objects.filter(
            create_user_id=create_user_id,
            id=o_id,
        )
        if not objs:
            self.add_error('o_id', '文章不存在')
        else:
            return o_id

    # 查询文章标题是否存在
    def clean_title(self):
        create_user_id = self.data['create_user_id']
        title = self.data['title']
        o_id = self.data['o_id']  # 文章id
        print('o_id -->', o_id)
        objs = models.Article.objects.filter(
            create_user_id=create_user_id,
            title=title,
        ).exclude(id=o_id)
        if objs:
            self.add_error('title', '标题已存在')
        else:
            return title


# 商品添加
class AddGoodForm(forms.Form):
    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '创建人不能为空'
        }
    )
    goods_classify_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '商品分类不能为空'
        }
    )
    goods_name = forms.CharField(
        required=True,
        error_messages={
            'required': '商品名称不能为空'
        }
    )
    price = forms.CharField(
        required=True,
        error_messages={
            'required': '商品价格不能为空'
        }
    )
    inventory = forms.IntegerField(
        required=False,
        error_messages={
            'required': '商品库存不能为空'
        }
    )
    freight = forms.IntegerField(
        required=False,
        error_messages={
            'required': '商品运费不能为空'
        }
    )
    goods_describe = forms.CharField(
        required=True,
        error_messages={
            'required': '商品描述不能为空'
        }
    )
    point_origin = forms.CharField(
        required=True,
        error_messages={
            'required': '商品发货地不能为空'
        }
    )
    goods_status = forms.IntegerField(
        required=True,
        error_messages={
            'required': '商品状态不能为空'
        }
    )
    # goods_picture = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': '商品图片不能为空'
    #     }
    # )
    cover_img = forms.CharField(
        required=True,
        error_messages={
            'required': '封面图片不能为空'
        }
    )

    def clean_goods_classify_id(self):
        goods_classify_id = self.data.get('goods_classify_id')
        create_user_id = self.data.get('create_user_id')
        objs = models.GoodsClassify.objects.filter(oper_user_id=create_user_id, id=goods_classify_id)
        if objs:
            return goods_classify_id
        else:
            self.add_error('goods_classify_id', '无此分类')

    def clean_goods_name(self):
        create_user_id = self.data.get('create_user_id')
        goods_name = self.data.get('goods_name')
        objs = models.Goods.objects.filter(goods_classify__oper_user_id=create_user_id, goods_name=goods_name)
        if objs:
            self.add_error('goods_name', '商品名称已存在')
        else:
            return goods_name


# 商品更新
class UpdateGoodForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章id不能为空'
        }
    )

    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '创建人不能为空'
        }
    )
    goods_classify_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '商品分类不能为空'
        }
    )
    goods_name = forms.CharField(
        required=True,
        error_messages={
            'required': '商品名称不能为空'
        }
    )
    # price = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': '商品价格不能为空'
    #     }
    # )
    inventory = forms.IntegerField(
        required=False,
        error_messages={
            'required': '商品库存不能为空'
        }
    )
    # freight = forms.IntegerField(
    #     required=False,
    #     error_messages={
    #         'required': '商品运费不能为空'
    #     }
    # )
    goods_describe = forms.CharField(
        required=True,
        error_messages={
            'required': '商品描述不能为空'
        }
    )
    point_origin = forms.CharField(
        required=True,
        error_messages={
            'required': '商品发货地不能为空'
        }
    )
    goods_status = forms.IntegerField(
        required=True,
        error_messages={
            'required': '商品状态不能为空'
        }
    )
    # goods_picture = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': '商品图片不能为空'
    #     }
    # )
    cover_img = forms.CharField(
        required=True,
        error_messages={
            'required': '封面图片不能为空'
        }
    )

    def clean_goods_classify_id(self):
        goods_classify_id = self.data.get('goods_classify_id')
        create_user_id = self.data.get('create_user_id')
        objs = models.GoodsClassify.objects.filter(oper_user_id=create_user_id, id=goods_classify_id)
        if objs:
            return goods_classify_id
        else:
            self.add_error('goods_classify_id', '无此分类')

    def clean_goods_name(self):
        create_user_id = self.data.get('create_user_id')
        goods_name = self.data.get('goods_name')
        o_id = self.data.get('o_id')
        objs = models.Goods.objects.filter(goods_classify__oper_user_id=create_user_id, goods_name=goods_name).exclude(
            id=o_id)
        if objs:
            self.add_error('goods_name', '商品名称已存在')
        else:
            return goods_name


# 查询
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页显示数量类型错误"
        }
    )

    def clean_current_page(self):
        if 'current_page' not in self.data:
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length
