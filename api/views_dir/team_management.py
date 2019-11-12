from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.team_management import SelectForm
import json




@csrf_exempt
@account.is_token(models.UserProfile)
def team_management_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 更改团队权限
        if oper_type == 'update_team':
            players_id = request.POST.get('players_id') # 队员ID
            template_list = request.POST.get('template_list') # 权限模板列表
            objs = models.UserProfile.objects.filter(id=players_id)
            if objs:
                objs.update(select_template_list=json.dumps(template_list))
                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = '队员错误'


    else:
        # 获取角色对应的权限
        if oper_type == "get_team_data":
            forms_obj = SelectForm(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                order = request.GET.get('order', '-create_datetime')
                field_dict = {
                    'id': '',
                }
                q = conditionCom(request, field_dict)

                objs = models.UserProfile.objects.filter(q, inviter_id=user_id).order_by(order)
                count = objs.count()
                if length != 0 and not request.GET.get('id'):
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                ret_data = []
                for obj in objs:
                    data = {
                        'id': obj.id,
                        'name': obj.name,
                    }

                    if request.GET.get('id'):
                        template_objs = models.Template.objects.filter(id__in=json.loads(obj.select_template_list))
                        template_list = []
                        for template_obj in template_objs:
                            template_list.append({
                                'id': template_obj.id,
                                'name': template_obj.name,
                            })
                        data['template_list'] = template_list

                    ret_data.append(data)

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'count': count,
                    'ret_data':ret_data
                }

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = "请求异常"


    return JsonResponse(response.__dict__)
