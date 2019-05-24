

import requests
import time
import os
import json


workWeixinDataPath = os.path.join(os.getcwd(), 'publicFunc', 'weixin', 'workWeixin', 'workweixin.json')        # 存放数据的json文件


class WorkWeixinApi(object):

    def __init__(self):
        # self.corpid = 'ww24123520340ba230'                                      # 企业ID
        self.corpid = 'wx81159f52aff62388'                                      # 企业ID  雷达
        # self.agentId = '1000002'                                                 # 应用 AgentId
        self.agentId = '1000008'                                                 # 应用 AgentId 雷达
        # self.corpSecret = 'mcbKC5PcuUKw28vFr7Qk5kpfe3pUuqPjX6Cz54H0FxE'    # 应用密钥
        self.corpSecret = 'Cl94UPitHm81hrE7zo7X1eMXcNIFXWjAvP1jP_uKGnQ'    # 应用密钥 雷达

        self.token = {
            'access_token': '',
            'time_stamp': ''
        }

    # 判断 token 是否过期
    def is_token_expires(self):
        with open (workWeixinDataPath, 'r') as f:
            fileData = f.read()
            fileJsonData = json.loads(fileData)
            access_token = fileJsonData.get('access_token')
            time_stamp = fileJsonData.get('time_stamp')
            now_time_stamp = int(time.time())
            if access_token and time_stamp and now_time_stamp - time_stamp < 7000:
                self.token = {
                    'access_token': access_token,
                    'time_stamp': time_stamp
                }
            else:
                self.gettoken()

    # 获取 access_token
    def gettoken(self):
        print('获取 access_token  ----->')
        params = {
            'corpid': self.corpid,
            'corpsecret': self.corpSecret,
        }
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        ret = requests.get(url=url, params=params)
        ret_json = ret.json()
        if ret_json['errcode'] == 0:
            access_token = ret_json['access_token']
            self.token = {
                'access_token': access_token,
                'time_stamp': int(time.time())
            }

            with open(workWeixinDataPath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.token))

        else:
            print('请求异常 ----------->', ret_json)

    # 获取用户id
    def user_simplelist(self):
        self.is_token_expires()  # 判断 token 是否过期
        params = {
            'access_token': self.token['access_token'],
            'department_id': 1,
        }
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/simplelist'
        ret = requests.get(url, params=params)
        ret_json = ret.json()

        if ret_json['errcode'] == 0:
            print('userlist ---->', ret_json['userlist'])

        else:
            print('请求异常 ----------->', ret_json)

    # 发送应用消息
    def message_send(self, userID, content):
        self.is_token_expires()  # 判断 token 是否过期
        params = {
            'access_token': self.token['access_token'],
        }
        text_data = {
            "touser": str(userID),
            "msgtype": "text",
            "agentid": self.agentId,
            "text": {
                "content": content
            }
        }
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'

        ret = requests.post(url=url, params=params, data=json.dumps(text_data, ensure_ascii=False).encode("utf-8"))
        print(ret.text)



if __name__ == '__main__':
    workWeixinDataPath = './workweixin.json'
    obj = WorkWeixinApi()
    # obj.gettoken()
    # obj.user_simplelist()
    phone_names = ["001", "002"]
    content = """小红书机器异常，请及时处理:  \n{phone_names}
    """.format(phone_names="\n".join(phone_names))
    obj.message_send('ZhangCong', content)
