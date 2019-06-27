

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

from bs4 import BeautifulSoup
import requests, random, datetime, re


# 登录手机管理中心 操作

class phone_management():

    def __init__(self):
        self.headers = {'User-Agent': pcRequestHeader[random.randint(0, len(pcRequestHeader) - 1)]}
        self.requests_obj = requests.Session()

    # 登录
    def login(self):
        login_url = "http://47.110.86.5:9999/index.php?g=cust&m=login&a=dologin"
        data = {
            "username": "张聪296",
            "password": "zhang_cong.123",
        }
        self.requests_obj.post(url=login_url, headers=self.headers, data=data)

    # 查询验证码
    def query_verification_code(self, phone_number):
        yzm_url = 'http://47.110.86.5:9999/index.php?g=cust&m=smscust&a=receive'
        now = datetime.date.today()
        data = {
            'startDate': now,
            'endDate': now,
            'mobile': phone_number,
        }
        ret = self.requests_obj.post(yzm_url, headers=self.headers, data=data)
        soup = BeautifulSoup(ret.text, 'lxml')
        content = soup.find('div', class_='tab-content')
        form_obj = content.find('form', class_='js-ajax-form').find_all('tr')
        verification_code = 0
        if len(form_obj) >= 2:
            yzm_obj = form_obj[1] # 获取最后一个验证码
            if_yzm_text = yzm_obj.find_all('td')[1].get_text()
            if '验证码' in if_yzm_text:
                if_yzm_text = if_yzm_text.split('[From')[0]
                yzm = re.search('\d{6}', if_yzm_text)
                verification_code = yzm.group()

        return verification_code

if __name__ == '__main__':
    obj = phone_management()
    obj.login()
    obj.query_verification_code(1)









