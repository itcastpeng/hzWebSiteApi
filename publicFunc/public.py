from publicFunc.weixin.workWeixin.workWeixinApi import WorkWeixinApi
from hurong import models
import re, random, requests

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



# 创建请求日志 requests 请求外界
def requests_log(url, request_parameters, response_content):
    models.externalRequestRecord.objects.create(**{
        'request_parameters': request_parameters,  # 请求参数
        'request_url': url,
        'response_content': response_content # 响应数据
    })

def send_error_msg(content, send_type=None):
    obj = WorkWeixinApi()
    if send_type in [1, '1']:
        obj.message_send('1539939991515', content)  # 鹏
    else:
        obj.message_send('HeZhongGaoJingJianCe', content)          # 张聪
        obj.message_send('HeZhongGongSiJianKong', content)      # 贺昂A

