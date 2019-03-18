
import time
import random
import requests
import xml.dom.minidom as xmldom
from publicFunc import xmldom_parsing
from publicFunc.weixin.weixin_api_public import WeixinApiPublic


class weixin_pay_api(WeixinApiPublic):
    def __init__(self):
        self.mch_id = '1488841842'      # 支付商户号
        self.SHANGHUKEY = 'fk1hzTGe5G5qt2mlR8UD5AqOgftWuTsK'        # 商户api 密钥

    # 生成订单号
    def shengcheng_dingdanhao(self):
        ymdhms = time.strftime("%Y%m%d%H%M%S", time.localtime())  # 年月日时分秒
        timestamp_after_five = str(int(time.time() * 1000))[8:]  # 时间戳 后五位
        dingdanhao = timestamp_after_five + str(ymdhms) + str(random.randint(10, 99))
        return dingdanhao

    # 预支付功能
    def yuzhifu(self, data):
        # mch_id, SHANGHUKEY = self.get_pay_info()
        openid = data.get('openid')
        total_fee = data.get('total_fee')
        appid = data.get('appid')
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'  # 微信支付接

        dingdanhao = self.shengcheng_dingdanhao()       # 生成订单号
        result_data = {
            'appid': appid,                             # appid
            'mch_id': self.mch_id,                           # 商户号
            'nonce_str': self.generateRandomStamping(),     # 32位随机值a
            'openid': openid,                           # 微信用户唯一标识
            'body': '天眼-会员续费'.encode('utf8'),       # 描述
            'out_trade_no': dingdanhao,                 # 订单号
            'total_fee': total_fee,                     # 金额(分 为单位)
            'spbill_create_ip': '0.0.0.0',              # 终端IP

            # 指向--> http://127.0.0.1:8008/api/weixin_pay/wxpay
            'notify_url': 'http://api.zhugeyingxiao.com/tianyan/wxpay',
            'trade_type': 'JSAPI'
        }
        string_sign_temp = self.shengchengsign(result_data, self.SHANGHUKEY)
        result_data['sign'] = self.md5(string_sign_temp).upper()
        xml_data = self.toXml(result_data)
        ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
        ret.encoding = 'utf8'

        dom_tree = xmldom.parseString(ret.text)
        collection = dom_tree.documentElement
        data = ['return_code', 'return_msg']
        result_data = xmldom_parsing.xmldom(collection, data)
        data = ['prepay_id']
        prepay_id = xmldom_parsing.xmldom(collection, data)
        ret_data = {
            'return_code': result_data['return_code'],
            'return_msg': result_data['return_msg'],
            'dingdanhao': dingdanhao,
            'prepay_id': prepay_id,
        }
        return ret_data

    # 回调 判断是否支付成功
    def weixin_back_pay(self, result_data):
        url = 'https://api.mch.weixin.qq.com/pay/orderquery'
        string_sign_temp = self.shengchengsign(result_data, self.SHANGHUKEY)
        result_data['sign'] = self.md5(string_sign_temp).upper()
        xml_data = self.toXml(result_data)
        ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
        ret.encoding = 'utf8'
        dom_tree = xmldom.parseString(ret.text)
        collection = dom_tree.documentElement
        return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data

        return return_code
