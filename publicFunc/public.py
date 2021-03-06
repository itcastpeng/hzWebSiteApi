from hurong import models
from publicFunc.qiniu.auth import Auth
from publicFunc.redisOper import get_redis_obj
from publicFunc.account import randon_str
import re, random, requests, json, os, qrcode, time

pcRequestHeader = [
    'Mozilla/5.0 (Windows NT 5.1; rv:6.0.2) Gecko/20100101 Firefox/6.0.2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.16) Gecko/20101130 Firefox/3.5.16',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; .NET CLR 1.1.4322)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; zh-CN; rv:1.9.0.19) Gecko/2010031422 Firefox/3.0.19 (.NET CLR 3.5.30729)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13'
]


# 验证手机号
def verify_phone_number(phone_number):
    phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
    res = re.search(phone_pat, phone_number)
    flag = False
    if res:
        flag = True
    return flag

# 查询手机流量
def get_traffic_information(number):
    headers = {'User-Agent': pcRequestHeader[random.randint(0, len(pcRequestHeader) - 1)]}
    url = 'http://bigdata.sh-fancy.cn/VrUTOCardInfo/CheckCardInfo.do'
    post_data = {
        'card': number
    }
    ret = requests.post(url, headers=headers, data=post_data)
    ret_json = ret.json()
    if ret_json.get('errcode') != 0:
        data = {
            'code': 1,
            'msg': ret_json.get('errmsg')
        }
    else:
        data = {
            'code': 0,
            'cardbaldata': ret_json.get('cardbaldata'),     # 剩余流量
            'cardenddate': ret_json.get('cardenddate'),     # 卡到期时间
            'cardimsi': ret_json.get('cardimsi'),           # ismi号
            'cardno': ret_json.get('cardno'),               # 卡编号
            'cardnumber': ret_json.get('cardnumber'),       # 卡号
            'cardstatus': ret_json.get('cardstatus'),       # 用户状态
            'cardstartdate': ret_json.get('cardstartdate'), # 卡开户时间
            'cardtype': ret_json.get('cardtype'),           # 套餐类型
            'cardusedata': ret_json.get('cardusedata'),     # 已用流量
        }

    return data

# 查询设备 充值信息
def query_device_recharge_information(number):
    headers = {'User-Agent': pcRequestHeader[random.randint(0, len(pcRequestHeader) - 1)]}
    url = 'http://bigdata.sh-fancy.cn/VrUTOCardInfo/getCardRecharge.do'
    post_data = {
        'card': number
    }
    ret = requests.post(url, headers=headers, data=post_data)
    ret_json = ret.json()
    data = {
        'code': 0,
        'data_list': ret_json.get('list')
    }

    return data


# 发送告警信息
def send_error_msg(content, status=None):
    if not status:
        status = 6
    # obj = WorkWeixinApi()
    # if send_type in [1, '1']:
    #     obj.message_send('1539939991515', content)  # 鹏
    # else:
    #     obj.message_send('HeZhongGaoJingJianCe', content)          # 张聪
    #     obj.message_send('HeZhongGongSiJianKong', content)      # 贺昂A

    # 创建告警信息
    # redis_obj = get_redis_obj()
    # redis_key = "mobile_equipment_abnormal_send_message_enterprise_record"
    # if redis_obj.llen(redis_key) > 500:
    #     redis_obj.rpop(redis_key)
    # redis_obj.lpush(redis_key, content)

    models.MobileEquipmentAbnormalSendMessageEnterpriseRecord.objects.create(
        error_msg=content,
        status=status
    )

# 更新 小红书后台 请求 该后台 返回值
def update_xhs_admin_response(request, response):
    method = 1
    if request.method == 'POST':
        method = 2

    models.AskLittleRedBook.objects.filter(  # 更新日志
        status=method,  # POST请求
        request_url=request.path,
    ).order_by('-create_datetime').update(
        response_data=response.__dict__,
    )

# 创建请求日志
def create_xhs_admin_response(request, response, status, url=None, req_type=None):

    if req_type:
        request_type = req_type
    else:
        request_type = 1
        if request.method == 'POST':
            request_type = 2

    if url:
        req_url = url
    else:
        req_url = request.path

    try:
        response_data = response.__dict__
    except Exception:
        response_data = response

    models.AskLittleRedBook.objects.create(  # 更新日志
        request_type=request_type,  # POST请求
        request_url=req_url,
        get_request_parameter=dict(request.GET),
        post_request_parameter=dict(request.POST),
        response_data=response_data,
        status=status
    )

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

# 生成二维码
def get_qrcode(qrcode_path):
    img = qrcode.make(qrcode_path)
    time_name = str(int(time.time())) + '.png'
    with open('{}'.format(time_name), 'wb') as f:
        img.save(f)
    path = upload_qiniu(time_name, 800)
    return path

def requests_img_download(old_url):
    ret = requests.get(old_url)
    path = os.path.join('statics', 'imgs', randon_str() + '.png')
    with open(path, 'wb') as e:
        e.write(ret.content)
    return path

def get_existing_url(url):
    if "www.xiaohongshu.com" in url:
        link = url.split('?')[0]

    elif 'show.meitu.com' in url:  # 美图
        link = url

    elif 'xhsurl' in url:
        link = url.split('，')[0]
        ret = requests.get(link)

        link = ret.url.split('?')[0]

    else:
        ret = requests.get(url, allow_redirects=False)
        link = re.findall('HREF="(.*?)"', ret.text)[0].split('?')[0]
    return link


