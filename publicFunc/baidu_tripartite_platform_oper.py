from api import models
from publicFunc import Response, account
import requests, json, time, os
from publicFunc.qiniu.auth import Auth
from publicFunc.redisOper import get_redis_obj
from publicFunc import Response

baidu_tripartite_platform_key = 'PCwOy1gDSz0cAixIMIli4hBIzHaz4Kib' # 第三方平台Key

# 百度小程序返回值处理
def baidu_applet_return_data(return_data, add_msg):
    response = Response.ResponseObj()
    code = return_data.get('errno')
    msg = return_data.get('msg')
    data = return_data.get('data')
    if code in [0, '0']:
        code = 200
        msg = str(add_msg) + '成功'
    response.code = code
    response.msg = msg
    response.data = data
    return response

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
            self.pre_auth_code = ret_data.get('pre_auth_code')
            pre_auth_code_time = int(time.time()) + int(ret_data.get('expires_in'))  # 有效时长

            BaiduTripartitePlatformObjs.update(
                pre_auth_code=self.pre_auth_code,
                pre_auth_code_time=pre_auth_code_time
            )

    # 使用 授权码 调用 小程序凭证
    def get_get_small_program_authorization_credentials(self, auth_code, template_id, user_id):
        url = 'https://openapi.baidu.com/rest/2.0/oauth/token' #使用授权码换小程序的接口调用凭据和授权信息
        params = {
            'access_token': self.access_token,
            'code': auth_code,
            'grant_type': 'app_to_tp_authorization_code',
        }
        ret = requests.get(url, params=params)
        ret_json_credentials = ret.json()
        access_token = ret_json_credentials.get('access_token')

        url = 'https://openapi.baidu.com/rest/2.0/smartapp/app/info?access_token={}'.format(access_token)
        ret = requests.get(url)     # 获取小程序基础信息
        ret_json = ret.json().get('data')
        print('v-获取小程序基础信息---------------------> ', ret_json)
        app_id = ret_json.get('app_id')
        small_data = {
            'appid':app_id,
            'access_token':access_token,
            'refresh_token': ret_json_credentials.get('refresh_token'),
            'access_token_time': int(time.time()) + int(ret_json_credentials.get('expires_in')),
            'program_name': ret_json.get('app_name'),     # 小程序的名称
            'app_key': ret_json.get('app_key'),       # 小程序的key
            'app_desc': ret_json.get('app_desc'),     # 小程序的介绍内容
            'photo_addr': json.loads(ret_json.get('photo_addr'))[0].get('cover'), # 小程序图标
            'template_id': template_id,
            'user_id': user_id,
        }
        print('small_data----------> ', small_data)
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
        whether_audit = True
        if not data.get('whether_audit'):
            whether_audit = False

        ext_json = {
            "extEnable": True,
            "extAppid": data.get('appid'),
            "directCommit": whether_audit,
            "ext": {
                'template_id': data.get('id'),  # 小程序ID 查询改小程序模板
                # 'user_id': 4,
                # 'token': 'f0b813db005dd5273cd9d6129c75fc4c',
                'user_id': data.get('user_id'),
                'token': data.get('user_token'),
            },
            "window": {                         # 用于设置 SWAN 的状态栏、导航条、标题、窗口背景色。
                # "backgroundTextStyle": "light",
                # "navigationBarBackgroundColor": "#fff",
                # "navigationBarTitleText": "Demo",
                # "navigationBarTextStyle": "black"
            },
            "tabBar": {                         # 用于设置客户端底部的tab栏：可通过tabBar设置tab的颜色、个数、位置、背景色等内容。
            },
            "networkTimeout": {             # 网络超时
                # "request": 20000,
                # "downloadFile": 20000
            }
        }
        print('ext_json-------------------------------------> ', ext_json)
        post_data = {
            'access_token': data.get('token'),
            'template_id': data.get('template_id'),
            'ext_json': json.dumps(ext_json),           # ext
            'user_version': data.get('version'),                         # 版本号
            'user_desc': 'xxxx',                            # 描述
        }
        response = Response.ResponseObj()
        ret = requests.post(url, data=post_data)
        print('r未授权的小程序账号上传小程序代码et.json()------------> ', ret.json())
        code = 301
        if ret.json().get('errno') in [0, '0']:
            code = 200
        msg = ret.json().get('msg')
        response.code = code
        response.msg = msg
        return response

    # 获取模板列表
    def get_template_list(self, page, page_size):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/template/gettemplatelist'
        params = {
            'access_token': self.access_token,
            'page': 1,
            'page_size': 200,
        }
        ret = requests.get(url, params=params)
        print('-获取模板列表-=-------------> ', ret.json())
        response = Response.ResponseObj()
        code = 301
        msg = ret.json().get('error_msg')
        if not msg:
            msg = ret.json().get('msg')
        if ret.json().get('errno') in [0, '0']:
            code = 200
        response.code = code
        response.msg = msg
        list = sorted(ret.json().get('data').get('list'), key=lambda x: x['create_time'], reverse=True) # 排序
        response_data = ret.json().get('data')
        start_line = (int(page) - 1) * int(page_size)
        stop_line = start_line + int(page_size)
        response_data['list'] = list[int(start_line): int(stop_line)]
        response.data = response_data
        return response

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
        print('获取模板草稿列表-------------------> ', ret.json())
        response = Response.ResponseObj()
        code = 301
        msg = ret.json().get('error_msg')
        if not msg:
            msg = ret.json().get('msg')
        if ret.json().get('errno') in [0, '0']:
            code = 200
        response.code = code
        response.msg = msg
        response.data = ret.json().get('data')
        return response

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
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/submitaudit?access_token={}'.format(data.get('token'))
        post_data = {
            'content': data.get('content'),                 # 送审描述
            'package_id': data.get('package_id'),           # 代码包id
            'remark': data.get('remark'),                   # 备注
        }
        ret = requests.post(url, data=post_data)
        print('ret.json(), post_data----------------------> ', ret.json(), post_data)
        response = Response.ResponseObj()
        code = 301
        msg = ret.json().get('error_msg')
        if not msg:
            msg = ret.json().get('msg')
        if ret.json().get('errno') in [0, '0']:
            code = 200
        response.code = code
        response.msg = msg
        return response

    # 发布已审核的小程序
    def release_approved_applet(self, package_id, token):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/release?access_token={}'.format(token)
        post_data = {
            'package_id': package_id,
        }
        print('package_id=------------------------------------------> ', package_id)
        ret = requests.post(url, data=post_data)
        print('r发布已审核的小程序et.json()--------------------> ', ret.json())
        response = Response.ResponseObj()
        code = 301
        msg = ret.json().get('error_msg')
        if not msg:
            msg = ret.json().get('msg')
        if ret.json().get('errno') in [0, '0']:
            code = 200
        response.code = code
        response.msg = msg
        return response

    # 小程序版本回滚
    def small_program_version_roll_back(self, package_id, token):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/rollback?access_token={}'.format(token)
        post_data = {
            'package_id': package_id
        }
        ret = requests.post(url, data=post_data)
        response = Response.ResponseObj()
        code = 301
        msg = ret.json().get('error_msg')
        if not msg:
            msg = ret.json().get('msg')
        if ret.json().get('errno') in [0, '0']:
            code = 200
        response.code = code
        response.msg = msg
        return response

    # 小程序审核撤回
    def small_procedure_review_withdrawal(self, package_id, token):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/withdraw?access_token={}'.format(token)
        post_data = {
            'package_id': package_id
        }
        ret = requests.post(url, data=post_data)
        response = Response.ResponseObj()
        code = 301
        msg = ret.json().get('error_msg')
        if not msg:
            msg = ret.json().get('msg')
        if ret.json().get('errno') in [0, '0']:
            code = 200
        response.code = code
        response.msg = msg
        return response

    # 获取小程序包列表
    def gets_list_small_packages(self, access_token):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/package/get'
        params = {
            'access_token': access_token
        }
        ret = requests.get(url, params=params)
        print('获取小程序包列表------------------> ', ret.json())
        response = Response.ResponseObj()
        code = 301
        msg = ret.json().get('error_msg')
        if ret.json().get('errno') in [0, '0']:
            msg = ret.json().get('msg')
            code = 200
        data_result = sorted(ret.json().get('data'), key=lambda x: x['commit_time'], reverse=True)  # 排序
        data_list = []
        for data in data_result:

            data_status = data.get('status')
            if data_status in [3, '3']:
                status = '开发版本'
            elif data_status in [4, '4']:
                status = '审核中'
            elif data_status in [5, '5']:
                status = '审核失败'
            elif data_status in [6, '6']:
                status = '审核通过'
            elif data_status in [8, '8']:
                status = '回滚中'
            else:
                status = '线上版本'

            data['status'] = status
            data_list.append(data)

        response.code = code
        response.msg = msg
        response.data = data_list
        response.note = {
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

    # 获取二维码
    def get_qr_code(self, package_id, width, token):
        params = {
            'width': width, # 默认200px，最大1280px，最小200px
        }
        if package_id:
            params['package_id'] = package_id # 可指定代码包id(只支持审核、开发、线上版本)，不传默认线上版本。
        print('params-----------------> ', params)
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/app/qrcode?access_token={}'.format(token)
        ret = requests.get(url, params=params)
        img_path = str(int(time.time())) + '.png'
        with open(img_path, 'wb') as f:
            f.write(ret.content)
        path = upload_qiniu(img_path, 800)
        return path

    # web化开关
    def web_the_switch(self, web_status):
        # web_status 1:开启 2:关闭
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/app/modifywebstatus?access_token={}'.format(self.access_token)
        post_data = {
            'web_status': web_status,
        }
        ret = requests.post(url, data=post_data)
        response = baidu_applet_return_data(ret.json(), '操作')
        return response

    # 小程序熊掌ID绑定
    def small_procedures_bear_paw_ID_binding(self):
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/promotion/bind/xzh?access_token={}'.format(self.access_token)
        ret = requests.post(url)
        response = baidu_applet_return_data(ret.json(), '操作')
        return response

    # 提交sitemap
    def submit_sitemap(self, type, url_list):
        # type 上传级别 0：周级别，一周左右生效；1：天级别，2~3天生效
        url = 'https://openapi.baidu.com/rest/2.0/smartapp/access/submit/sitemap?access_token={}'.format(self.access_token)
        post_data = {
            'url_list': url_list,
            'type': type,
        }
        ret = requests.post(url, data=post_data)
        response = baidu_applet_return_data(ret.json(), '操作')
        return response

    # 判断小程序access_token是否过期
    def determines_whether_access_token_expired(self, appid):
        obj = models.BaiduSmallProgramManagement.objects.get(appid=appid)

        url = 'https://openapi.baidu.com/rest/2.0/oauth/token'  # 刷新接口凭证
        params = {
            'access_token': self.access_token,
            'refresh_token': obj.refresh_token,
            'grant_type': 'app_to_tp_refresh_token',
        }

        if obj.access_token_time - int(time.time()) <= 60:
            ret = requests.get(url, params=params)
            obj.access_token =ret.json().get('access_token')
            obj.refresh_token = ret.json().get('refresh_token')
            obj.access_token_time = int(time.time()) + int(ret.json().get('expires_in'))
            obj.save()
        return obj.access_token

# 上传七牛云
def upload_qiniu(img_path, img_size):
    redis_obj = get_redis_obj()
    url = 'https://up-z1.qiniup.com/'
    upload_token = redis_obj.get('qiniu_upload_token')
    if not upload_token:
        qiniu_data_path = os.path.join(os.getcwd(), "publicFunc", "qiniu", "qiniu_data.json")
        with open(qiniu_data_path, "r", encoding="utf8") as f:
            data = json.loads(f.read())
            access_key = data.get('access_key')
            secret_key = data.get('secret_key')
            obj = Auth(access_key, secret_key)
            upload_token = obj.upload_token("xcx_wgw_zhangcong")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13'
    }
    with open(img_path, 'rb') as f:
        imgdata = f.read()

    files = {
        'file': imgdata
    }

    data = {
        'token': upload_token,
    }
    ret = requests.post(url, data=data, files=files, headers=headers)
    key = "http://qiniu.bjhzkq.com/{key}?imageView2/0/h/{img_size}".format(
        key=ret.json()["key"],
        img_size=img_size
    )
    if os.path.exists(img_path):
        os.remove(img_path)  # 删除本地图片
    return key
















