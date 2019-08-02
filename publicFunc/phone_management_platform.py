

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
import requests, random, datetime, re, json


# 登录手机管理中心 操作

class phone_management():

    def __init__(self):
        self.headers = {'User-Agent': pcRequestHeader[random.randint(0, len(pcRequestHeader) - 1)]}
        self.requests_obj = requests.Session()
        self.now = datetime.date.today()

    # 登录
    def login(self):
        data = [
            {
                "login_url":"http://47.110.86.5:9999",
                "username": "张聪296",
                "password": "zhang_cong.123",
            },{
                "login_url":"http://120.55.80.27:9999",
                "username": "张聪0627",
                "password": "zhang_cong.123",
            }
        ]
        return data

    # 查询验证码
    def query_verification_code(self, phone_number):
        zh_data = self.login()
        verification_code = 0
        for data in zh_data:
            login_url = data.get('login_url') + '/index.php?g=cust&m=login&a=dologin'
            self.requests_obj.post(url=login_url, headers=self.headers, data=data)
            yzm_url = data.get('login_url') + '/index.php?g=cust&m=smscust&a=receive'
            data = {
                'startDate': self.now,
                'endDate': self.now,
                'mobile': phone_number,
            }
            ret = self.requests_obj.post(yzm_url, headers=self.headers, data=data)
            soup = BeautifulSoup(ret.text, 'lxml')
            content = soup.find('div', class_='tab-content')
            form_obj = content.find('form', class_='js-ajax-form').find_all('tr')
            # if len(form_obj) >= 2:
            #     print('form_obj---------> ', form_obj)
                # yzm_obj = form_obj[1] # 获取最后一个验证码
            for yzm_obj in form_obj:
                if '验证码' in yzm_obj.get_text():
                    now = datetime.datetime.today()
                    deletionTime = (now - datetime.timedelta(minutes=5))
                    yzm_time = yzm_obj.find_all('td')[2].get_text()
                    yzm_time = datetime.datetime.strptime(yzm_time, '%Y-%m-%d %H:%M:%S')
                    if yzm_time >= deletionTime:
                        if_yzm_text = yzm_obj.find_all('td')[1].get_text()
                        if '验证码' in if_yzm_text:
                            if_yzm_text = if_yzm_text.split('[From')[0]
                            yzm = re.search('\d{6}', if_yzm_text)
                            verification_code = yzm.group()

            if not verification_code:
                continue
            else:
                break

        return verification_code

    # 获取当天所有短信
    def get_all_information_day(self):
        zh_data = self.login()
        data_list = []
        for data in zh_data:
            login_url = data.get('login_url') + '/index.php?g=cust&m=login&a=dologin'
            try:
                self.requests_obj.post(url=login_url, headers=self.headers, data=data)
            except Exception:
                pass
            yzm_url = data.get('login_url') + '/index.php?g=cust&m=smscust&a=receive'
            data = {
                'startDate': self.now,
                'endDate': self.now,
            }
            try:
                ret = self.requests_obj.post(yzm_url, headers=self.headers, data=data)
                soup = BeautifulSoup(ret.text, 'lxml')
                content = soup.find('div', class_='tab-content')
                form_objs = content.find('form', class_='js-ajax-form').find_all('tr')
                for form_obj in form_objs:
                    tr_tags = form_obj.find_all('td')
                    if len(tr_tags) >= 1:
                        result_data = []
                        for tr_tag in tr_tags:
                            text = tr_tag.get_text()
                            if text:
                                result_data.append(text)
                        data_list.append({
                            'phone_number': result_data[0],
                            'content': result_data[1],
                            'date_time': result_data[2],
                            'serial_number': result_data[3],
                        })
            except Exception:
                pass
        return data_list


    # 查询所有手机号
    def get_all_phone_num(self):
        zh_data = self.login()
        phone_num_list = []
        for data in zh_data:
            login_url = data.get('login_url') + '/index.php?g=cust&m=login&a=dologin'
            self.requests_obj.post(url=login_url, headers=self.headers, data=data)
            num = 1
            break_flag = False
            while True:
                if break_flag:
                    break
                yzm_url = data.get('login_url') + '/index.php?g=cust&m=cardno_cust&a=sub&p={}'.format(num)
                ret = self.requests_obj.post(yzm_url, headers=self.headers)
                soup = BeautifulSoup(ret.text, 'lxml')
                tbody = soup.find('tbody')
                tr_tags = tbody.find_all('tr')
                for tr_tag in tr_tags:
                    phone_num = tr_tag.find_all('td')[1].get_text().strip()
                    if phone_num in phone_num_list:
                        break_flag = True
                        break
                    phone_num_list.append(phone_num)
                num += 1
        return phone_num_list

if __name__ == '__main__':
    obj = phone_management()
    obj.login()
    phone_number = '13089927032'
    print(obj.query_verification_code(phone_number))









