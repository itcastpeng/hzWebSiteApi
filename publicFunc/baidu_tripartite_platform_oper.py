from api import models
from publicFunc import Response, account
import requests, json, time, os
from publicFunc.qiniu.auth import Auth
from publicFunc.redisOper import get_redis_obj


baidu_tripartite_platform_key = 'PCwOy1gDSz0cAixIMIli4hBIzHaz4Kib' # 第三方平台Key

# 百度小程序返回值处理
def baidu_applet_return_data(return_data, add_msg):
    code = return_data.get('errno')
    msg = return_data.get('msg')
    data = return_data.json().get('data')
    if code in [0, '0']:
        code = 200
        msg = str(add_msg) + '成功'

    return {'code': code, 'msg': msg, 'data': data}

# 三方平台操作
class tripartite_platform_oper():
    response = Response.ResponseObj()

    # ========================================公共函数==========================================

    def __init__(self):
        BaiduTripartitePlatformObjs = models.BaiduTripartitePlatformManagement.objects.filter(id=1)
        BaiduTripartitePlatformObj = BaiduTripartitePlatformObjs[0]
        ticket = BaiduTripartitePlatformObj.ticket
        access_token_time = BaiduTripartitePlatformObj.access_token_time
        pre_auth_code_time = BaiduTripartitePlatformObj.pre_auth_code_time
        self.access_token = BaiduTripartitePlatformObj.access_token

        if int(access_token_time) - int(time.time()) <= 600: # token还有10分钟过期

            url = 'https://openapi.baidu.com/public/2.0/smartapp/auth/tp/token'
            params = {
                'client_id': baidu_tripartite_platform_key,
                'ticket': ticket
            }
            ret = requests.get(url, params=params)
            ret_data = ret.json().get('data')
            self.access_token = ret_data.get('access_token')  # access_token
            access_token_time = int(time.time()) + int(ret_data.get('expires_in'))  # 有效时长
            scope = ret_data.get('scope')  # 权限说明

            BaiduTripartitePlatformObjs.update(
                access_token=self.access_token,
                access_token_time=access_token_time
            )

        if int(pre_auth_code_time) - int(time.time()) <= 60: # 预授权码还有1分钟到期
            url = 'https://openapi.baidu.com/rest/2.0/smartapp/tp/createpreauthcode'
            params = {
                'access_token': self.access_token
            }
            ret = requests.get(url, params=params)
            ret_data = ret.json().get('data')
            self.pre_auth_code = ret_data.get('pre_auth_code')  # access_token
            pre_auth_code_time = int(time.time()) + int(ret_data.get('expires_in'))  # 有效时长

            BaiduTripartitePlatformObjs.update(
                pre_auth_code=self.pre_auth_code,
                pre_auth_code_time=pre_auth_code_time
            )

    # 使用 授权码 调用 小程序凭证
    def get_get_small_program_authorization_credentials(self, auth_code):
        url = 'https://openapi.baidu.com/rest/2.0/oauth/token'
        params = {
            'access_token': self.access_token,
            'code': auth_code,
            'grant_type': 'app_to_tp_authorization_code',
        }
        ret = requests.get(url, params=params)
        ret_json = ret.json().get('data')
        access_token = ret_json.get('access_token')

        url = 'https://openapi.baidu.com/rest/2.0/smartapp/app/info?access_token={}'.format(access_token)
        ret = requests.get(url)
        ret_json = ret.json().get('data')
        print('使用 授权码 调用 小程序凭证=-=================> ', ret_json)
        app_id = ret_json.get('app_id')
        small_data = {
            'appid':app_id,
            'access_token':access_token,
            'refresh_token': ret_json.get('refresh_token'),
            'access_token_time': ret_json.get('expires_in'),
            'app_name': ret_json.get('app_name')  ,     # 小程序的名称
            'app_key': ret_json.get('app_key')  ,       # 小程序的key
            'app_desc': ret_json.get('app_desc')  ,     # 小程序的介绍内容
            'photo_addr': ret_json.get('photo_addr')  , # 小程序图标
        }

        # qualification = ret_json.get('qualification')   # 小程序账号对应的主体信息
        # qualification_name = qualification.name     # 主体名称

        objs = models.BaiduSmallProgramManagement.objects.filter(
            appid=app_id
        )
        if objs:
            objs.update(**small_data)
        else:
            models.BaiduSmallProgramManagement.objects.create(**small_data)


    # 未授权的小程序账号上传小程序代码
    def upload_small_program_code(self, data):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/upload'
        ext_json = {
            "extEnable": True,
            "extAppid": data.get('appid'),
            "directCommit": False,
            "ext": {

            },
            "window": {                         # 用于设置 SWAN 的状态栏、导航条、标题、窗口背景色。
                "backgroundTextStyle": "light",
                "navigationBarBackgroundColor": "#fff",
                "navigationBarTitleText": "Demo",
                "navigationBarTextStyle": "black"
            },
            "tabBar": {                         # 用于设置客户端底部的tab栏：可通过tabBar设置tab的颜色、个数、位置、背景色等内容。
            },
            "networkTimeout": {             # 网络超时
                "request": 20000,
                "downloadFile": 20000
            }
        }

        post_data = {
            'access_token': self.access_token,
            'template_id': data.get('template_id'),
            'ext_json': json.dumps(ext_json),           # ext
            'user_version': '',                         # 版本号
            'user_desc': '',                            # 描述
        }

        ret = requests.post(url, data=post_data)
        response_data = baidu_applet_return_data(ret.json(), '上传')
        return response_data

    # 获取模板列表
    def get_template_list(self, page, page_size):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/template/gettemplatelist'
        params = {
            'access_token': self.access_token,
            'page': page,
            'page_size': page_size,
        }
        ret = requests.get(url, params=params)
        response_data = baidu_applet_return_data(ret.json(), '查询')
        response_data['data'] = ret.json().get('data')
        return response_data

    # 删除模板
    def delete_template(self, template_id):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/template/deltemplate'
        post_data = {
            'template_id': template_id,
            'access_token': self.access_token
        }
        ret = requests.post(url, data=post_data)
        response_data = baidu_applet_return_data(ret.json(), '删除')
        return response_data

    # 获取模板草稿列表
    def gets_the_template_draft_list(self, page, page_size):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/template/gettemplatedraftlist'
        params = {
            'access_token': self.access_token,
            'page': page,
            'page_size': page_size
        }
        ret = requests.get(url, params=params)
        response_data = baidu_applet_return_data(ret.json(), '查询')
        return response_data

    # 添加草稿至模板
    def add_draft_to_template(self, draft_id, user_desc):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/template/addtotemplate'
        params = {
            'draft_id': draft_id,               # 草稿ID
            'access_token': self.access_token,
            'user_desc': user_desc,             # 自定义模板名称，30字以内
        }
        ret = requests.post(url, params=params)
        response_data = baidu_applet_return_data(ret.json(), '添加')
        return response_data

    # 为授权的小程序提交审核
    def submit_approval_authorized_mini_program(self, data):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/submitaudit'
        post_data = {
            'access_token': self.access_token,
            'content': data.get('content'),                 # 送审描述
            'package_id': data.get('package_id'),           # 代码包id
            'remark': data.get('remark'),                   # 备注
        }

        ret = requests.post(url, data=post_data)
        response = baidu_applet_return_data(ret.json(), '提交授权')
        return response

    # 发布已审核的小程序
    def release_approved_applet(self, package_id):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/release'
        post_data = {
            'access_token': self.access_token,
            'package_id': package_id,
        }
        ret = requests.post(url, data=post_data)
        response = baidu_applet_return_data(ret.json(), '发布小程序')
        return response

    # 小程序版本回滚
    def small_program_version_roll_back(self, package_id):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/rollback'
        post_data = {
            'access_token': self.access_token,
            'package_id': package_id
        }
        ret = requests.post(url, data=post_data)
        response = baidu_applet_return_data(ret.json(), '回滚')
        return response

    # 小程序审核撤回
    def small_procedure_review_withdrawal(self, package_id):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/withdraw'
        post_data = {
            'access_token': self.access_token,
            'package_id': package_id
        }
        ret = requests.post(url, data=post_data)
        response = baidu_applet_return_data(ret.json(), '撤回')
        return response

    # 获取小程序包列表
    def gets_list_small_packages(self):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/get'
        params = {
            'access_token': self.access_token
        }
        ret = requests.get(url, params=params)
        response = baidu_applet_return_data(ret.json(), '获取小程序包列表')
        response['note'] = {
            'version': '版本号',
            'remark': '备注',
            'msg': '审核信息',
            'committer': '提交人',
            'status': '状态 1线上版本 3开发版本 4审核中 5审核失败 6审核通过 8回滚中',
            'commit_time': '提交时间',
            'version_desc': '版本描述',
            'package_id': '代码包id',
            'rollback_version': '上一个线上版本的版本号',
            'upload_status': '上传状态 1上传中 3上传失败',
            'upload_status_desc': '上传状态描述',
        }
        return response

    # 获取授权小程序包详情
    def get_details_authorization_package(self, package_id, package_type):
        # package_type 1线上版本 3开发中 4审核中 5审核失败 6审核通过 8回滚中

        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/getdetail'
        params = {
            'access_token': self.access_token,
            'type': package_type, # 小程序状态，不指定package_id的情况下默认是线上版本
            'package_id': package_id
        }

        ret = requests.get(url, params=params)
        response = baidu_applet_return_data(ret.json(), '获取详情')
        response['note'] = {
            'version': '版本号',
            'remark': '备注',
            'msg': '审核信息',
            'committer': '提交人',
            'status': '状态 1线上版本 3开发版本 4审核中 5审核失败 6审核通过 8回滚中',
            'commit_time': '提交时间',
            'version_desc': '版本描述',
            'package_id': '代码包Id',
        }
        return response












