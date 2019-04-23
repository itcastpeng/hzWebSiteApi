# from django.shortcuts import render
from hurong import models
from publicFunc import Response
from publicFunc import account
from publicFunc.send_email import SendEmail
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from hurong.forms.task_list import SelectForm, AddForm, UpdateForm, TestForm
import json
from django.db.models import Q


@account.is_token(models.UserProfile)
def task_list(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            # print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            # q.add(Q(**{k + '__contains': value}), Q.AND)
            role_id = models.UserProfile.objects.get(id=user_id).role_id_id
            if role_id != 1:    # 非管理员角色只能看自己的
                q.add(Q(**{'create_user_id': user_id}), Q.AND)

            objs = models.TaskList.objects.filter(is_delete=False).filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'status': obj.get_status_display(),
                    'status_id': obj.status,
                    'percentage_progress': obj.percentage_progress,
                    'send_email_title': obj.send_email_title,
                    'send_email_content': obj.send_email_content,
                    'create_user__username': obj.create_user.username,
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
                'id': "任务id",
                'name': "任务名称",
                'percentage_progress': "任务进度",
                'send_email_title': "发送邮件标题",
                'send_email_content': "发送邮件内容",
                'create_user__username': "创建人",
                'create_datetime': "创建时间",
                'status': "状态名称",
                'status_id': "状态值",
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.UserProfile)
def task_list_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "POST":
        # 添加用户
        if oper_type == "add":
            form_data = {
                'create_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
                'send_email_title': request.POST.get('send_email_title'),
                'send_email_content': request.POST.get('send_email_content'),
                'send_email_list': request.POST.get('send_email_list'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                create_data = {
                    'create_user_id': forms_obj.cleaned_data.get('create_user_id'),
                    'name': forms_obj.cleaned_data.get('name'),
                    'send_email_title': forms_obj.cleaned_data.get('send_email_title'),
                    'send_email_content': forms_obj.cleaned_data.get('send_email_content'),
                }
                send_email_list = forms_obj.cleaned_data.get('send_email_list')
                print('create_data -->', create_data, send_email_list)
                obj = models.TaskList.objects.create(**create_data)

                query = []
                for send_email in send_email_list:
                    query.append(
                        models.TaskInfo(to_email=send_email, task_list=obj)
                    )
                models.TaskInfo.objects.bulk_create(query)

                response.code = 200
                response.msg = "添加成功"
                response.data = {
                    'testCase': 1,
                    'id': 1,
                }
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "delete":
            # 删除 ID
            task_list_objs = models.TaskList.objects.filter(id=o_id)
            if task_list_objs:
                if task_list_objs[0].status == 1:
                    task_list_objs.update(is_delete=True)
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 300
                    response.msg = "该任务正在操作中，不能删除"

        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'password': request.POST.get('password'),
                'status': request.POST.get('status'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data['o_id']
                update_data = {
                    'status': forms_obj.cleaned_data['status'],
                }
                password = forms_obj.cleaned_data['password']
                if password:
                    update_data['password'] = password

                # 更新数据
                models.UserProfile.objects.filter(id=o_id).update(**update_data)

                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "test":
            form_data = {
                'send_email_title': request.POST.get('send_email_title'),
                'send_email_content': request.POST.get('send_email_content'),
                'send_email_list': request.POST.get('send_email_list'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = TestForm(form_data)
            if forms_obj.is_valid():
                send_email_title = forms_obj.cleaned_data.get('send_email_title')
                send_email_content = forms_obj.cleaned_data.get('send_email_content')
                send_email_list = forms_obj.cleaned_data.get('send_email_list')

                while True:
                    email_user_obj = models.EmailUserInfo.objects.all().order_by('use_number')[0]
                    email_user_obj.use_number += 1
                    email_user_obj.save()
                    email_user = email_user_obj.email_user
                    email_pwd = email_user_obj.email_pwd
                    print(email_user, email_pwd)
                    send_email_obj = SendEmail(email_user, email_pwd, send_email_list, send_email_title,
                                               send_email_content)
                    send_email_obj.send_email()
                    if send_email_obj.send_status:
                        response.code = 200
                        response.msg = "发送成功"
                        response.data = {
                            'testCase': 1,
                            'id': 1,
                            'email_user': email_user,
                            'email_pwd': email_pwd,
                        }
                        break
                    else:
                        email_user_obj.is_available = False
                        email_user_obj.save()

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        elif oper_type == "save_task":
            task_info_id_list = request.POST.get('task_info_id_list')
            task_list_id = request.POST.get('task_list_id')
            send_status = request.POST.get('send_status')
            email_user_id = request.POST.get('email_user_id')
            print(send_status)

            # 发送成功
            if send_status == "True":
                models.TaskInfo.objects.filter(id__in=json.loads(task_info_id_list)).update(status=2)
                task_list_obj = models.TaskList.objects.get(id=task_list_id)
                is_send_count = task_list_obj.taskinfo_set.filter(status=2).count()  # 已经发送成功的总数
                count = task_list_obj.taskinfo_set.count()  # 该任务的总任务数
                # print(is_send_count, count, is_send_count / count)
                task_list_obj.percentage_progress = int(is_send_count / count * 100)
                task_list_obj.save()
            else:
                # 发布失败，修改账号状态
                models.EmailUserInfo.objects.filter(id=email_user_id).update(is_available=False)

            response.code = 200
            response.msg = "保存成功"

    else:
        if oper_type == "get_task":

            # 开始任务
            task_list_objs = models.TaskList.objects.exclude(Q(percentage_progress=100) | Q(status__gte=3)).filter(is_delete=False)[0: 1]
            if task_list_objs:
                # 发送标题和内容
                task_list_obj = task_list_objs[0]
                task_list_obj.status = 2
                task_list_obj.save()

                send_email_title = task_list_obj.send_email_title
                send_email_content = task_list_obj.send_email_content

                # 收件人列表
                task_info_objs = task_list_obj.taskinfo_set.filter(status=1)[0: 5]
                task_info_id_list = []
                send_email_list = []
                for task_info in task_info_objs:
                    task_info_id_list.append(task_info.id)
                    send_email_list.append(task_info.to_email)

                email_user_obj = models.EmailUserInfo.objects.all().order_by('use_number')[0]
                email_user_obj.use_number += 1
                email_user_obj.save()
                email_user = email_user_obj.email_user
                email_pwd = email_user_obj.email_pwd
                print(email_user, email_pwd, send_email_list)
                response.data = {
                    'email_user_id': email_user_obj.id,
                    'email_user': email_user,
                    'email_pwd': email_pwd,
                    'send_email_list': send_email_list,
                    'task_info_id_list': task_info_id_list,
                    'send_email_title': send_email_title,
                    'send_email_content': send_email_content,
                    'task_list_id': task_list_obj.id,
                }
            response.code = 200

        elif oper_type == "get_xiala_keywords":
            response.data = '"丰唇", "颈纹", "漂唇", "祛疤", "祛斑", "纹眉", "纹绣", "植眉", "薄唇", "背部", "鼻部", "除皱", "大腿", "点痣", "短鼻", "额头", "耳部", "腹部", "厚唇", "肩膀", "睫毛", "酒窝", "口唇", "两颚", "隆鼻", "隆胸", "毛发", "眉毛", "美肤", "皮肤", "祛痘", "祛痣", "去皱", "手臂", "瘦脸", "缩阴", "体检", "臀部", "脱毛", "卧蚕", "洗牙", "下巴", "小腿", "胸部", "牙齿", "眼部", "眼袋", "眼科", "腰部", "长鼻", "整形", "美容", "磨骨", "去痣", "洗眉", "吸脂", "补牙", "拔牙", "整形", "体检", "妇产", "中医", "肾病", "妇科", "口腔", "植发", "骨科", "胃肠", "儿科", "眼科", "玻尿酸", "丰额头", "丰耳垂", "丰面颊", "丰下巴", "改脸型", "黑眼圈", "开眼角", "烤瓷牙", "美容冠", "美瞳线", "祛胎记", "祛眼袋", "瘦肩针", "瘦脸针", "瘦腿针", "双下巴", "双眼皮", "水光针", "抬头纹", "微整形", "洗纹身", "修复类", "牙贴面", "植胡须", "植睫毛", "嘴角纹", "V型脸", "杯状耳", "妇产科", "近视眼", "祛副乳", "去副乳", "去色素", "溶脂针", "肉毒素", "上眼睑", "太阳穴", "脱唇毛", "脱腋毛", "招风耳", "种植牙", "去眼袋", "眼综合", "丰眼窝", "丰卧蚕", "填泪沟", "鼻综合", "垫鼻尖", "垫下巴", "隆眉弓", "耳再造", "孕睫术", "去疤痕", "美白针", "去狐臭", "洗眼线", "洗唇线", "脱胡须", "脱腿毛", "脱背毛", "瘦大腿", "瘦手臂", "瘦腰腹", "瘦臀部", "瘦小腿", "瘦后背", "优立塑", "热立塑", "瘦肩膀", "抗衰老", "热玛吉", "超声刀", "热拉提", "去颈纹", "瓷贴面", "检测类", "爱贝芙", "溶解酶", "皮肤科", "白癜风", "耳鼻喉", "凹陷填充", "鼻部整形", "鼻孔缩小", "鼻梁整形", "鼻形矫正", "鬓角移植", "彩光嫩肤", "唇部脱毛", "点阵激光", "电波拉皮", "副乳切除", "光滑脱毛", "光子嫩肤", "果酸换肤", "黑脸娃娃", "激光祛痣", "激光洗眉", "假体丰胸", "假体隆鼻", "酒窝成形", "巨乳缩小", "泪沟填充", "毛发加密", "毛发移植", "毛发种植", "眉弓填充", "美白嫩肤", "面部脱毛", "面部整形", "皮肤美白", "去颊脂垫", "手臂吸脂", "私密移植", "私密整形", "四肢脱毛", "腿部吸脂", "臀部吸脂", "脱络腮胡", "微针美塑", "卧蚕成形", "吸脂减肥", "吸脂瘦脸", "胸部脱毛", "胸部修复", "胸部整形", "牙齿矫正", "牙齿美白", "牙齿美容", "眼部吸脂", "眼部整形", "眼睑下垂", "眼窝填充", "腋下脱毛", "注射隆鼻", "蛀牙补牙", "疤痕植发", "鼻部修复", "鼻骨矫正", "鼻尖整形", "鼻翼缩小", "产后修复", "唇部整形", "唇厚改薄", "大腿吸脂", "耳部整形", "丰苹果肌", "丰太阳穴", "妇科疾病", "妇科检查", "改善肤质", "贵族手术", "颌角整形", "颌面整形", "黑头粉刺", "胡须种植", "激光溶脂", "激光脱毛", "假体取出", "健康管理", "胶原蛋白", "近视矫正", "口腔修复", "冷冻溶脂", "毛孔粗大", "眉毛种植", "美体塑形", "面部轮廓", "面部提升", "面部填充", "面部吸脂", "嫩肤美白", "女性私密", "皮肤美容", "其他整形", "青春抗衰", "祛斑祛红", "祛皱紧肤", "去红血丝", "全身脱毛", "全身吸脂", "颧骨颧弓", "颧骨整形", "乳房再造", "乳房整形", "乳头矫正", "乳头整形", "软骨隆鼻", "生活美容", "失败修复", "手臂脱毛", "手部吸脂", "私密种植", "头发种植", "腿部脱毛", "歪鼻矫正", "歪脸纠正", "纹绣漂红", "吸脂塑身", "下巴吸脂", "下巴整形", "线雕隆鼻", "牙齿修复", "牙齿治疗", "牙齿种植", "腰腹吸脂", "阴茎增大", "永久脱毛", "月光脱毛", "脂肪丰胸", "脂肪填充", "注射丰唇", "注射瘦脸", "注射下巴", "综合隆鼻", "嘴角上提", "北京整形", "整形医院", "上海整形", "开内眼角", "开外眼角", "去黑眼圈", "眼袋修复", "眼型矫正", "下睑下至", "切眉提眉", "隆鼻修复", "鼻孔矫正", "鼻型矫正", "宽鼻矫正", "长鼻矫正", "垫鼻基底", "去双下巴", "耳形矫正", "磨下颌角", "颧骨内推", "乳晕漂红", "果酸焕肤", "黄金微针", "像素激光", "皮秒激光", "激光祛斑", "中药祛斑", "E光祛斑", "激光祛疤", "手术祛疤", "药物祛疤", "注射祛疤", "手术切痣", "激光点痣", "白瓷娃娃", "E光嫩肤", "补水保湿", "无针水光", "水氧活肤", "冰点脱毛", "光子脱毛", "脱发际线", "身体脱毛", "私密脱毛", "脱手脚毛", "脱手臂毛", "脱手背毛", "假体隆胸", "复合隆胸", "乳头缩小", "乳晕缩小", "胸型美化", "隆胸修复", "丰臀提臀", "假体丰臀", "射频溶脂", "隔空溶脂", "埋线减肥", "吸脂修复", "自体脂肪", "除皱抗衰", "埋线提升", "激光提升", "去鱼尾纹", "去抬头纹", "去法令纹", "去川字纹", "去妊娠纹", "人中缩短", "唇型美化", "M唇手术", "厚唇改薄", "兔唇手术", "去露龈笑", "隐形矫正", "舌侧矫正", "喷砂洗牙", "冷光美白", "皓齿美白", "树脂贴面", "根管治疗", "治疗脱发", "睫毛种植", "鬓角种植", "胸毛种植", "检查测试", "皮肤检测", "术前面诊", "面诊咨询", "注射美容", "注射修复", "女性私密", "私密漂红", "阴蒂整形", "G点注射", "男性私密", "试管婴儿", "不孕不育", "婚纱摄影", "鼻小柱延长", "比基尼脱毛", "川字纹除皱", "发际线移植", "眉间纹填充", "苹果肌注射", "祛除法令纹", "祛痘祛痘印", "腰腹部吸脂", "鱼尾纹除皱", "BOTOX", "奥美定取出", "玻尿酸注射", "处女膜修复", "地包天纠正", "发际线矫正", "发际线调整", "发际线脱毛", "韩式双眼皮", "抗衰抗初老", "埋线双眼皮", "美人尖种植", "青春烔目术", "全切双眼皮", "驼峰鼻矫正", "激光去眼袋", "内切去眼袋", "外切去眼袋", "射频去眼袋", "埋线去眼袋", "眼综合整形", "双眼皮修复", "内眼角修复", "外眼角修复", "手术造卧蚕", "眼周年轻化", "眼部热玛吉", "玻尿酸隆鼻", "鼻综合整形", "手术缩鼻翼", "手术缩鼻头", "鹰钩鼻矫正", "朝天鼻矫正", "假体丰额头", "假体垫眉弓", "招风耳矫正", "副耳去除术", "杯状耳矫正", "轮廓三件套", "下巴截骨术", "上下颚整形", "半永久化妆", "半永久纹眉", "半永久纹唇", "红蓝光祛痘", "扩张器祛疤", "激光去胎记", "手术去胎记", "注射去狐臭", "手术去狐臭", "超微小气泡", "激光去黑头", "吸脂去副乳", "手术去副乳", "吸脂瘦大腿", "吸脂瘦手臂", "吸脂瘦腰腹", "腹壁成形术", "吸脂瘦臀部", "吸脂瘦小腿", "吸脂瘦后背", "吸脂瘦肩膀", "大脚骨手术", "玻尿酸除皱", "肉毒素除皱", "颈部热玛吉", "颈部超声刀", "嗨体去颈纹", "人中缩短术", "丰唇/唇珠", "玻尿酸丰唇", "嘴角上扬术", "合金烤瓷牙", "纯钛烤瓷牙", "全瓷烤瓷牙", "超声波洗牙", "发际线种植", "其他填充剂", "注射物取出", "小阴唇整形", "鼻头鼻翼缩小", "隆鼻失败修复", "祛痘祛疤祛痣", "乳房下垂矫正", "乳头乳晕整形", "乳晕乳头漂红", "自体软骨隆鼻", "自体脂肪丰胸", "SPA/按摩", "半永久美瞳线", "半永久纹眉毛", "鼻部失败修复", "胶原蛋白注射", "抗衰老&去皱", "脸部脂肪移植", "乳房下垂提升", "上睑下垂矫正", "胸部失败修复", "眼部失败修复", "注射丰苹果肌", "注射丰太阳穴", "自体脂肪隆胸", "射频去黑眼圈", "微针去黑眼圈", "激光去黑眼圈", "玻尿酸丰眼窝", "玻尿酸丰卧蚕", "玻尿酸填泪沟", "硅胶假体隆鼻", "膨体假体隆鼻", "自体脂肪隆鼻", "自体真皮隆鼻", "肉毒素缩鼻头", "假体垫鼻基底", "光纤溶脂瘦脸", "取颊脂垫瘦脸", "激光溶脂瘦脸", "射频溶脂瘦脸", "玻尿酸丰下巴", "下巴假体取出", "假体丰太阳穴", "吸脂去双下巴", "玻尿酸丰额头", "玻尿酸隆眉弓", "玻尿酸丰面颊", "玻尿酸丰耳垂", "人造酒窝手术", "颧骨颧弓整形", "半永久纹眼线", "半永久睫毛线", "微针美塑祛痘", "皮肤磨削祛疤", "去色素/胎记", "E光去红血丝", "激光去红血丝", "光子去红血丝", "洗纹绣/纹身", "其他肤质问题", "激光去脂肪粒", "乳头内陷矫正", "胸部假体取出", "隆胸失败修复", "优立塑瘦大腿", "热立塑瘦大腿", "优立塑瘦手臂", "热立塑瘦手臂", "优立塑瘦腰腹", "热立塑瘦腰腹", "优立塑瘦臀部", "热立塑瘦臀部", "优立塑瘦小腿", "热立塑瘦小腿", "优立塑瘦后背", "热立塑瘦后背", "自体脂肪丰臀", "优立塑瘦肩膀", "热立塑瘦肩膀", "吸脂失败修复", "其他美体塑形", "自体脂肪丰手", "自体脂肪修复", "拉皮手术提升", "悬吊手术提升", "微针紧致提升", "RF射频紧肤", "射频去妊娠纹", "微晶去妊娠纹", "激光去妊娠纹", "玻尿酸去颈纹", "其他皱纹问题", "自体脂肪丰唇", "玻尿酸丰唇珠", "手术去露龈笑", "陶瓷托槽矫正", "金属托槽矫正", "自锁托槽矫正", "贵金属烤瓷牙", "面部毛发种植", "身体毛发种植", "私密毛发种植", "激光私密紧致", "手术私密紧致", "太阳穴凹陷填充", "双眼皮失败修复", "光纤溶脂去眼袋", "眶隔释放去眼袋", "玻尿酸去黑眼圈", "眼整形失败修复", "自体脂肪丰眼窝", "自体脂肪填泪沟", "胶原蛋白填泪沟", "曼特波假体隆鼻", "自体肋软骨隆鼻", "自体耳软骨隆鼻", "鼻中隔软骨隆鼻", "手术延长鼻小柱", "玻尿酸丰鼻基底", "自体软骨垫鼻尖", "自体真皮垫鼻尖", "自体脂肪丰下巴", "硅胶假体垫下巴", "膨体假体垫下巴", "玻尿酸面部填充", "玻尿酸丰太阳穴", "自体脂肪丰额头", "玻尿酸丰苹果肌", "自体脂肪隆眉弓", "自体脂肪丰面颊", "自体脂肪丰耳垂", "颧骨颧弓整形术", "半永久纹发际线", "CO2点阵激光", "电波&微针导入", "乳头/乳晕整形", "胸部注射物取出", "冷冻溶脂瘦大腿", "激光溶脂瘦大腿", "光纤溶脂瘦大腿", "隔空溶脂瘦大腿", "射频溶脂瘦大腿", "激光溶脂瘦手臂", "冷冻溶脂瘦手臂", "光纤溶脂瘦手臂", "隔空溶脂瘦手臂", "射频溶脂瘦手臂", "射频溶脂瘦腰腹", "冷冻溶脂瘦腰腹", "激光溶脂瘦腰腹", "光纤溶脂瘦腰腹", "隔空溶脂瘦腰腹", "冷冻溶脂瘦臀部", "隔空溶脂瘦臀部", "激光溶脂瘦臀部", "射频溶脂瘦臀部", "光纤溶脂瘦臀部", "小腿神经阻断术", "射频溶脂瘦小腿", "激光溶脂瘦小腿", "冷冻溶脂瘦小腿", "光纤溶脂瘦小腿", "隔空溶脂瘦小腿", "激光溶脂瘦后背", "射频溶脂瘦后背", "冷冻溶脂瘦后背", "隔空溶脂瘦后背", "光纤溶脂瘦后背", "瘦全身/多部位", "冷冻溶脂瘦肩膀", "隔空溶脂瘦肩膀", "激光溶脂瘦肩膀", "射频溶脂瘦肩膀", "小切口手术提升", "内窥镜手术提升", "SMAS除皱术", "肉毒素去鱼尾纹", "玻尿酸去法令纹", "肉毒素去法令纹", "肉毒素去川字纹", "肉毒素去口周纹", "肉毒素去木偶纹", "肉毒素去鼻背纹", "肉毒素去露龈笑", "无托槽隐形矫正", "二氧化锆烤瓷牙", "肉毒素颏肌放松", "肉毒素治疗多汗", "超声刀私密紧致", "眼部整形失败修复", "自体脂肪丰鼻基底", "曼特波假体垫下巴", "自体脂肪面部填充", "自体脂肪丰太阳穴", "光纤溶脂去双下巴", "自体脂肪丰苹果肌", "下颚前突/地包天", "上颚前突/天包地", "祛痘/痘坑/痘印", "全身/多部位脱毛", "水动力吸脂瘦大腿", "水动力吸脂瘦手臂", "水动力吸脂瘦腰腹", "水动力吸脂瘦臀部", "水动力吸脂瘦小腿", "水动力吸脂瘦后背", "水动力吸脂瘦肩膀", "自体脂肪形体雕塑", "自体脂肪失败修复", "自体脂肪去法令纹", "自体脂肪私密紧致", "全面部/多部位填充", "PRP自体血清美肤", "鼻头/鼻翼/鼻孔矫正", "上下颚手术/突嘴矫正", "PRPⅢ自体干细胞注射", "V-LINE瓜子脸手术", "肉毒素注射（BOTOX）"'
        else:
            response.code = 402
            response.msg = "请求异常"
    return JsonResponse(response.__dict__)
