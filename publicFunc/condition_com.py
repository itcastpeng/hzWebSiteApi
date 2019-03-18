# 构造搜索条件 q
from django.db.models import Q
# from api import models
# import datetime
# from publicFunc import Response
# import os,json


def conditionCom(request, field_dict):
    q = Q()
    for k, v in field_dict.items():
        value = request.GET.get(k)
        if value:
            if v == '__contains':
                # 模糊查询
                q.add(Q(**{k + '__contains': value}), Q.AND)
            elif v == '__in':
                # 模糊查询
                q.add(Q(**{k + '__in': value}), Q.AND)
            elif v == '__isnull':
                # 是否为空
                flag = False
                if value == '1':
                    flag = True
                q.add(Q(**{k + '__isnull': flag}), Q.AND)
            else:
                q.add(Q(**{k: value}), Q.AND)

    return q
