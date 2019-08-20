from api import models
from publicFunc import Response, account
import requests, json, time, os
from publicFunc.public import upload_qiniu

encoding_token = 'sisciiZiJCC6PuGOtFWwmDnIHMsZyX'
encodingAESKey = 'sisciiZiJCC6PuGOtFWwmDnIHMsZyXmDnIHMsZyX123'
encoding_appid = 'wx1f63785f9acaab9c'

# 查询 授权的 公众号/小程序 调用凭证是否过期 (操作公众号 调用凭证 过期重新获取)
def QueryWhetherCallingCredentialExpired(appid, auth_type):
    """

    :param appid:  公众号/小程序 appid
    :param auth_type: 类型 (1公众号 2小程序) 区分查询数据库
    :return:
        authorizer_access_token : 调用 凭证
        flag： appid 是否存在
    """
    flag = False
    response = {}
    if auth_type in [1, '1']:
        objs = models.CustomerOfficialNumber.objects.filter(appid=appid)
    else:
        objs = models.ClientApplet.objects.filter(appid=appid)
    if objs:
        flag = True
        obj = objs[0]
        authorizer_access_token_expires_in = obj.authorizer_access_token_expires_in
        authorizer_access_token = obj.authorizer_access_token
        authorizer_refresh_token = obj.authorizer_refresh_token
        time_stamp = authorizer_access_token_expires_in - int(time.time())
        if time_stamp <= 100: # 已经过期
            tripartite_platform_oper_obj = tripartite_platform_oper()
            authorizer_access_token = tripartite_platform_oper_obj.refresh_exchange_calling_credentials(
                appid,
                authorizer_refresh_token,
                auth_type
            )

        response['id'] = obj.id
        response['authorizer_access_token'] = authorizer_access_token
    response['flag'] = flag
    return response


# 获取开放平台信息
def GetTripartitePlatformInfo():
    tripartite_objs = models.TripartitePlatform.objects.filter(appid__isnull=False)
    flag = False
    response = {}
    if tripartite_objs:
        tripartite_obj = tripartite_objs[0]
        response['tripartite_appid'] = tripartite_obj.appid
        response['tripartite_appsecret'] = tripartite_obj.appsecret
        response['component_access_token'] = tripartite_obj.component_access_token
    else:
        flag = True
    response['flag'] = flag

    return response



# 三方平台操作
class tripartite_platform_oper():
    response = Response.ResponseObj()

    # ========================================公共函数==========================================

    def __init__(self):
        obj = models.TripartitePlatform.objects.get(id=1)
        self.component_verify_ticket = obj.component_verify_ticket
        self.token = obj.component_access_token
        self.tripartite_platform_appid = obj.appid
        self.tripartite_platform_appsecret = obj.appsecret
        if int(obj.access_token_time) - int(time.time()) <= 600: # token还有10分钟过期
            self.get_component_access_token(obj)
            obj = models.TripartitePlatform.objects.get(id=1)
            self.token = obj.component_access_token

        self.params = {
            'component_access_token': self.token
        }

    # 获取第三方平台component_access_token
    def get_component_access_token(self, obj):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_component_token'
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "component_appsecret": self.tripartite_platform_appsecret,
            "component_verify_ticket": self.component_verify_ticket
        }
        ret = requests.post(url, data=json.dumps(post_data))
        """
            {
                "component_access_token":"61W3mEpU66027wgNZ_MhGHNQDHnFATkDa9-2llqrMBjUwxRSNPbVsMmyD-yq8wZETSoE5NQgecigDrSHkPtIYA", 
                "expires_in":7200
            }
        """
        print('获取第三方平台component_access_token---------> ', ret.json())
        component_access_token = ret.json().get('component_access_token')
        expires_in = int(time.time()) + ret.json().get('expires_in')
        obj.access_token_time = expires_in
        obj.component_access_token = component_access_token
        obj.save()

    # 获取预授权码 pre_auth_code
    def get_pre_auth_code(self):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode'

        post_data = {
            "component_appid": self.tripartite_platform_appid
        }
        ret = requests.post(url, params=self.params, data=json.dumps(post_data))

        print('获取预授权码 pre_auth_code--------> ', ret.json())
        pre_auth_code = ret.json().get('pre_auth_code')
        return pre_auth_code

    # 使用授权码换取公众号或小程序的接口调用凭据和授权信息exchange_calling_credentials
    def exchange_calling_credentials(self, auth_type, auth_code):
        """

        :param auth_type: 类型 1公众号 2小程序
        :param auth_code: 授权码
        :return:
        """
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth'
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "authorization_code": auth_code,            # 授权code
        }
        ret = requests.post(url, params=self.params, data=json.dumps(post_data))
        print('使用授权码换取公众号或小程序的接口调用凭据和授权信息exchange_calling_credentials=======> ', ret.text)
        authorization_info = ret.json().get('authorization_info')
        if authorization_info:
            authorizer_appid = authorization_info.get('authorizer_appid')
            print('-----------------开始写入',  auth_type, authorizer_appid)
            authorizer_access_token = authorization_info.get('authorizer_access_token')
            expires_in = int(time.time()) + int(authorization_info.get('expires_in'))
            authorizer_refresh_token = authorization_info.get('authorizer_refresh_token')
            # 更新令牌
            if auth_type in [1, '1']: # 公众号
                models.CustomerOfficialNumber.objects.filter(appid=authorizer_appid).update(
                    authorizer_access_token=authorizer_access_token,
                    authorizer_access_token_expires_in=expires_in,
                    authorizer_refresh_token=authorizer_refresh_token
                )
            else: # 小程序
                models.ClientApplet.objects.filter(appid=authorizer_appid).update(
                    authorizer_access_token=authorizer_access_token,
                    authorizer_access_token_expires_in=expires_in,
                    authorizer_refresh_token=authorizer_refresh_token
                )

    # 获取（刷新）授权公众号或小程序的接口调用凭据（令牌）
    def refresh_exchange_calling_credentials(self, appid, token, auth_type):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token'
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "authorizer_appid":appid,
            "authorizer_refresh_token":token,
        }

        ret = requests.post(url, params=self.params, data=json.dumps(post_data))
        ret_json = ret.json()
        print('获取（刷新）授权公众号或小程序的接口调用凭据（令牌）refresh_exchange_calling_credentials----> ', ret_json)
        authorizer_access_token = ret_json.get('authorizer_access_token')
        expires_in = int(time.time()) + int(ret_json.get('expires_in'))
        authorizer_refresh_token = ret_json.get('authorizer_refresh_token')
        # 更新令牌
        if auth_type in [1, '1']:  # 公众号
            models.CustomerOfficialNumber.objects.filter(appid=appid).update(
                authorizer_access_token=authorizer_access_token,
                authorizer_access_token_expires_in=expires_in,
                authorizer_refresh_token=authorizer_refresh_token
            )
        else:  # 小程序
            models.ClientApplet.objects.filter(appid=appid).update(
                authorizer_access_token=authorizer_access_token,
                authorizer_access_token_expires_in=expires_in,
                authorizer_refresh_token=authorizer_refresh_token
            )

        return authorizer_access_token

    # 公众号/小程序 获取授权方的帐号基本信息
    def get_account_information(self, auth_type, appid):
        """
        :param auth_type: 授权方类型 1公众号 2小程序
        :param appid:    # 授权方APPID
        :return:
        """
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info'
        post_data = {
            "component_appid": self.tripartite_platform_appid,    # 第三方APPID
            "authorizer_appid": appid       # 授权方APPID
        }
        ret = requests.post(url, params=self.params, data=json.dumps(post_data))
        ret_json = ret.json()
        print('公众号/小程序 获取授权方的帐号基本信息get_account_information----> ', json.dumps(ret_json))
        ret_json = ret_json.get('authorizer_info')
        # alias = ret_json.get('alias')                       # 授权方公众号所设置的微信号(公众号)
        # miniprograminfo = ret_json.get('miniprograminfo')   # 可根据这个字段判断是否为小程序类型授权(小程序)
        # network = ret_json.get('network')                   # 小程序已设置的各个服务器域名(小程序)
        #
        # func_info = ret_json.get('func_info')               # 公众号授权给开发者的权限集列表
        # business_info = ret_json.get('business_info')       # 用以了解以下功能的开通状况（0代表未开通，1代表已开通)
        # open_store = ret_json.get('open_store')             # 是否开通微信门店功能 open_scan:是否开通微信扫商品功能
        # open_pay = ret_json.get('open_pay')                 # 是否开通微信支付功能 open_card:是否开通微信卡券功能
        # open_shake = ret_json.get('open_shake')             # 是否开通微信摇一摇功能
        # service_type_info = ret_json.get('service_type_info')# 小程序默认为0 公众号 0代表订阅号，1代表由历史老帐号升级后的订阅号，2代表服务号
        # verify_type_info = ret_json.get('verify_type_info') # 授权方认证类型
        # authorization_info = ret_json.get('authorization_info')     # 授权信息
        # authorization_appid = ret_json.get('authorization_appid')   # 授权方appid
        """
                    verify_type_info
                    -1代表未认证，0代表微信认证  # 公共
                    公众号：
                        1代表新浪微博认证，2代表腾讯微博认证，
                        3代表已资质认证通过但还未通过名称认证，
                        4代表已资质认证通过、还未通过名称认证，但通过了新浪微博认证，
                        5代表已资质认证通过、还未通过名称认证，但通过了腾讯微博认证
                """

        nick_name = ret_json.get('nick_name')               # 授权方昵称
        head_img = ret_json.get('head_img')                 # 授权方头像
        user_name = ret_json.get('user_name')               # 授权方原始ID
        qrcode_url = ret_json.get('qrcode_url')             # 二维码图片的URL

        data = {
            'nick_name': nick_name,
            'head_img': head_img,
            'original_id': user_name,
            'qrcode_url': qrcode_url
        }

        if auth_type in [1, '1']:
            models.CustomerOfficialNumber.objects.filter(appid=appid).update(**data)

        else:
            models.ClientApplet.objects.filter(appid=appid).update(**data)

    # 获取授权方的选项设置信息
    def option_setting_information(self, option_name, appid):
        url = 'https://api.weixin.qq.com/cgi-bin/component/ api_get_authorizer_option'
        post_data = {
            "component_appid":self.tripartite_platform_appid,
            "authorizer_appid": appid,
            "option_name": option_name, # 选项名称
        }

        ret = requests.post(url, params=self.params, data=post_data)
        print('-option_setting_information-----------> ', ret.text)

    # 设置授权方的选项信息
    def set_authorizer_information(self, option_name, option_value, appid):
        url = 'https://api.weixin.qq.com/cgi-bin/component/ api_set_authorizer_option'
        post_data = {
            "component_appid": self.tripartite_platform_appid,
            "authorizer_appid": appid,
            "option_name": option_name, # 选项名称
            "option_value": option_value, # 选项值
        }
        ret = requests.post(url, params=self.params, data=post_data)

        print('set_authorizer_information------> ', ret.text)

    # 上传小程序代码====================================小程序函数============================
    def xcx_update_code(self, data):
        # ext_json 格式

        """
            {
                extAppid:"",   授权方APPID
                ext:{           # 自定义字段 可在小程序调用
                    "attr1":"value1",
                    "attr2":"value2",
                },
                extPages:{      # 页面配置
                    "index":{
                    },
                    "search/index":{
                    },
                },
                pages:["index","search/index"],
                "window":{
                },
                "networkTimeout":{
                },
                "tabBar":{
                },
            }

        """

        template_data = self.xcx_get_code_template()
        template_list = template_data.get('template_list')
        template_list = sorted(template_list, key=lambda x: x['create_time'], reverse=True)
        template_id = 0
        user_version = ''
        if len(template_list) >= 1:
            template_id = template_list[0].get('template_id') # 版本号
            user_version = template_list[0].get('user_version')
        user_desc = data.get('user_desc')
        appid = data.get('appid')
        token = data.get('token')
        user_id = data.get('user_id')
        user_token = data.get('user_token')
        id = data.get('id')

        ext_json = {
                'extAppid':appid,   #授权方APPID
                'ext':{           # 自定义字段 可在小程序调用
                    'template_id': id, #小程序ID 查询改小程序模板
                    'user_id': user_id,
                    'token': user_token,
                },
                # 'extPages':{      # 页面配置
                #     "index":{
                #     },
                #     "":{
                #     },
                # },
                # 'pages':["index","pages/index/tabBar01"],
                "window":{
                },
                "networkTimeout":{
                },
                "tabBar":{
                },
            }
        url = 'https://api.weixin.qq.com/wxa/commit?access_token={}'.format(token)

        data = {
            # 代码库中的代码模板ID
            "template_id": template_id,
            "ext_json": json.dumps(ext_json),
            # 代码版本号(自定义)
            "user_version": user_version,
            # 代码描述(自定义)
            "user_desc": user_desc,
        }
        ret = requests.post(url, data=json.dumps(data))
        print('ret.text------> ', ret.text)

    # 获取体验小程序二维码
    def xcx_get_experience_qr_code(self, token):
        url = 'https://api.weixin.qq.com/wxa/get_qrcode?access_token={}'.format(token)
        ret = requests.get(url)
        data = {}
        img_path = str(int(time.time())) + '.png'
        with open(img_path, 'wb') as f:
            f.write(ret.content)
        path = upload_qiniu(img_path, 800)
        data['path'] = path
        return data

    # 获取代码模板库中的所有小程序代码模板
    def xcx_get_code_template(self):
        url = 'https://api.weixin.qq.com/wxa/gettemplatelist?access_token={}'.format(self.token)
        ret = requests.post(url)
        print('获取代码模板库中的所有小程序代码模板=========--------> ', ret.text)
        errcode = ret.json().get('errcode')
        errmsg = ret.json().get('errmsg')
        template_list = ret.json().get('template_list')
        data = {
            'errcode':errcode,
            'template_list':template_list,
            'errmsg':errmsg,
        }
        return data

    # 获取草稿箱内的所有临时代码草稿
    def xcx_get_all_temporary_code_drafts(self):
        url = 'https://api.weixin.qq.com/wxa/gettemplatedraftlist?access_token={}'.format(
            self.token
        )

        ret = requests.get(url)
        print('获取草稿箱内的所有临时代码草稿------------> ', ret.json())
        return ret.json()

    # 将草稿箱的草稿选为小程序代码模版
    def xcx_select_draft_applet_code_template(self, draft_id):
        url = 'https://api.weixin.qq.com/wxa/addtotemplate?access_token={}'.format(self.token)
        data = {
            'draft_id': draft_id
        }
        print('data------> ', data)
        ret = requests.post(url, data=json.dumps(data))
        print('-将草稿箱的草稿选为小程序代码模版=------> ', ret.text)
        return ret.json()

    # 查询某个指定版本的审核状态
    def query_specified_version_code_audit(self, token, auditid):
        url = 'https://api.weixin.qq.com/wxa/get_auditstatus?access_token={}'.format(
            token
        )
        data = {
            'auditid': auditid
        }
        ret = requests.post(url, data=json.dumps(data))
        print('-查询某个指定版本的审核状态------> ', ret.json())
        return ret.json()

    # 查询最新一次提交的审核状态
    def check_status_most_recent_submission(self, token, auditid):
        url = 'https://api.weixin.qq.com/wxa/get_latest_auditstatus?access_token={}'.format(
            token,
        )
        ret = requests.get(url)
        print('查询最新一次提交的审核状态------> ', ret.json())
        return ret.json()

    # 获取小程序的第三方提交代码的页面配置
    def get_code_page_configuration(self, token):
        url = 'https://api.weixin.qq.com/wxa/get_page?access_token={}'.format(
            token
        )
        ret = requests.get(url)
        print('-获取小程序的第三方提交代码的页面配置--------> ', ret.text)
        return ret.json()

    # 将第三方提交的代码包提交审核
    def code_package_submitted_review(self, token):
        params = {
            'access_token': token
        }

        # 获取小程序的第三方提交代码的页面配置
        configuration_url = 'https://api.weixin.qq.com/wxa/get_page'
        configuration_ret = requests.get(configuration_url, params=params).json()
        print('configuration_ret-->', configuration_ret)
        # 获取授权小程序帐号已设置的类目
        class_to_set_url = 'https://api.weixin.qq.com/wxa/get_category'
        class_to_set_ret = requests.get(class_to_set_url, params=params).json()
        category_list = class_to_set_ret.get('category_list')

        url = 'https://api.weixin.qq.com/wxa/submit_audit?access_token={}'.format(
            token
        )
        data = {
            "item_list": [
            {
                "address":configuration_ret.get('page_list')[0],
                "first_class": category_list[0].get('first_class'),
                "second_class": category_list[0].get('second_class'),
                "first_id":category_list[0].get('first_id'),
                "second_id":category_list[0].get('second_id'),
                "tag":"首页",
                "title": "首页"
            }
            ],
                "feedback_info": "",
                "feedback_stuff": ""
        }

        ret = requests.post(url, data=json.dumps(data,  ensure_ascii=False).encode('utf8'))
        print('将第三方提交的代码包提交审核-------------> ', ret.text)
        return ret.json()

    # 发布已通过审核的小程序
    def publish_approved_applets(self, token):
        url = 'https://api.weixin.qq.com/wxa/release?access_token={}'.format(
            token
        )
        ret = requests.post(url)
        print('_--------发布已通过审核的小程序------> ', ret.text)

    # 获取体验者列表
    def Get_list_experiencers(self, token):
        url = 'https://api.weixin.qq.com/wxa/memberauth?access_token={}'.format(
            token
        )
        post_data = {
            "action": "get_experiencer"
        }
        # url = 'https://api.weixin.qq.com/wxa/memberauth'
        ret = requests.post(url, params=self.params, data=json.dumps(post_data))
        print('ret.url-----> ', ret.url)
        return ret.json()

    # 绑定微信用户为小程序体验者
    def bind_weChat_user_small_program_experiencer(self, token, wechatid):
        url = 'https://api.weixin.qq.com/wxa/bind_tester?access_token={}'.format(
            token
        )
        data = {
            'wechatid': wechatid
        }
        ret = requests.post(url, params=self.params, data=json.dumps(data))
        print('绑定微信用户为小程序体验者----->', ret.text)
        return ret.json()

    # 解除绑定小程序的体验者
    def the_experiencer_unbound_applet(self, token, wechatid):
        url = 'https://api.weixin.qq.com/wxa/unbind_tester?access_token={}'.format(
            token
        )
        data = {
            'wechatid': wechatid
        }
        ret = requests.post(url, data=json.dumps(data))
        print('解除绑定小程序的体验者---------> ', ret.text)
        return ret.json()

    # 查询小程序当前隐私设置（是否可被搜索）
    def query_current_privacy_settings(self, token):
        url = 'https://api.weixin.qq.com/wxa/getwxasearchstatus?access_token={}'.format(
            token
        )
        ret = requests.get(url)
        print('查询小程序当前隐私设置-----------> ', url, ret.text)
        return ret.json()

    # 设置小程序隐私设置（是否可被搜索）
    def set_applet_privacy_Settings(self, token, status): # 1表示不可搜索，0表示可搜索
        url = 'https://api.weixin.qq.com/wxa/changewxasearchstatus?access_token={}'.format(token)
        data = {
            'status': status
        }
        ret = requests.post(url, data=json.dumps(data))
        print('设置小程序隐私设置------> ',  url, ret.text)
        return ret.json()

    # 删除指定小程序代码模版
    def deletes_specified_applet_code_template(self, template_id):
        url = 'https://api.weixin.qq.com/wxa/deletetemplate?access_token={}'.format(
            self.token
        )
        post_data = {
            "template_id": template_id
        }
        ret = requests.post(url, data=json.dumps(post_data))
        print('删除指定小程序代码模版=----------------------', ret.json())
        return ret.json()



