from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse, HttpResponse
from api.forms.tripartite_platform import AuthorizationForm
from publicFunc.tripartite_platform_oper import tripartite_platform_oper as tripartite_platform
from publicFunc.crypto_.WXBizMsgCrypt import WXBizMsgCrypt
import time, json, datetime, xml.etree.cElementTree as ET, requests


@account.is_token(models.UserProfile)
def tripartite_platform_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 授权事件接收  （微信后台10分钟一次回调该接口 传递component_verify_ticket）
        if oper_type == 'tongzhi':
            signature = request.GET.get('signature')
            timestamp = request.GET.get('timestamp')
            nonce = request.GET.get('nonce')
            msg_signature = request.GET.get('msg_signature')
            user_id = request.GET.get('user_id')
            postdata = request.body.decode(encoding='UTF-8')

            xml_tree = ET.fromstring(postdata)
            Encrypt = xml_tree.find('Encrypt').text

            wx_obj = WXBizMsgCrypt('sisciiZiJCC6PuGOtFWwmDnIHMsZyX', 'sisciiZiJCC6PuGOtFWwmDnIHMsZyXmDnIHMsZyX123', 'wx1f63785f9acaab9c')
            ret, decryp_xml = wx_obj.DecryptMsg(Encrypt, msg_signature, timestamp, nonce)

            decryp_xml_tree = ET.fromstring(decryp_xml)
            ComponentVerifyTicket = decryp_xml_tree.find("ComponentVerifyTicket").text
            models.TripartitePlatform.objects.filter(
                appid=xml_tree.find('AppId').text
            ).update(
                component_verify_ticket=ComponentVerifyTicket,
                linshi=decryp_xml
            )


            return HttpResponse('success')
    else:

        objs = models.TripartitePlatform.objects.filter(appid__isnull=False)
        if objs:
            obj = objs[0]

            appid = obj.appid
            appsecret = obj.appsecret
            access_token = obj.component_access_token
            tripartite_objs = tripartite_platform(appid, appsecret) # 实例化三方平台

            # 授权
            if oper_type == "authorization":
                form_data = {
                    'user_id': user_id,
                    'appid': request.GET.get('appid'),
                }

                #  创建 form验证 实例（参数默认转成字典）
                forms_obj = AuthorizationForm(form_data)
                if forms_obj.is_valid():
                    get_pre_auth_code = tripartite_objs.get_pre_auth_code() # 获取预授权码

                    redirect_url = 'https://xcx.bjhzkq.com/api_hurong/xhs_phone_management/get_equipment_log'
                    wx_url = """
                    https://mp.weixin.qq.com/safe/bindcomponent?action=bindcomponent&auth_type=3&no_scan=1&component_appid={component_appid}&pre_auth_code={pre_auth_code}&redirect_uri={redirect_uri}&auth_type={auth_type}&biz_appid={biz_appid}#wechat_redirect
                    """.format(
                        component_appid=appid,              # 三方平台APPID
                        pre_auth_code=get_pre_auth_code,    # 预授权码
                        redirect_uri=redirect_url,          # 回调URL
                        auth_type='',                       # 授权账户类型
                        biz_appid=''
                    )
                    print('wx_url--> ', wx_url)
                    # ret = requests.post(wx_url)
                    # print('ret-------> ', ret.text)


                else:
                    response.code = 301
                    response.msg = json.loads(forms_obj.errors.as_json())

            # 用户确认 同意授权 回调
            elif oper_type == 'authorize_callback':
                pass

            # component_verify_ticket回调
            elif oper_type == 'component_verify_ticket_callback':
                body_data = request.body.decode(encoding='UTF-8')
                print('body_data-----> ', body_data)
                return HttpResponse('success')

            else:
                response.code = 402
                response.msg = "请求异常"
        else:
            response.code = 301
            response.msg = '三方平台获取失败'
    return JsonResponse(response.__dict__)

