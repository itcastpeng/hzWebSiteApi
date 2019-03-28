# developer: 张聪
# email: 18511123018@163.com

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header


def send_email(username, password, receiver, subject, text):
    """
    发送邮件
    :param username: 发送邮箱账号
    :param password: 发送邮箱密码
    :param receiver: 接收邮件账号列表，只有一个也要用列表 ['xxxx@qq.com']
    :param subject:  邮件标题
    :param text:     邮件正文内容
    :return:
    """
    # 设置smtplib所需的参数
    # 下面的发件人，收件人是用于邮件传输的。
    smtpserver = 'smtp.163.com'
    # username = 'pin8406284062840v@163.com'
    # password = 'fxfo7136'
    sender = username
    # receiver='XXX@126.com'
    # 收件人为多个收件人
    # receiver = ['2355938018@qq.com']

    # subject = '你好 请问你这边有一手媒体资源可以入驻我们后台吗，不收取任何手续费'
    # 通过Header对象编码的文本，包含utf-8编码信息和Base64编码信息。以下中文名测试ok
    # subject = '中文标题'
    # subject=Header(subject, 'utf-8').encode()

    # 构造邮件对象MIMEMultipart对象
    # 下面的主题，发件人，收件人，日期是显示在邮件页面上的。
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = '{username} <{username}>'.format(username=username)
    # msg['To'] = 'XXX@126.com'
    # 收件人为多个收件人,通过join将列表转换为以;为间隔的字符串
    msg['To'] = ";".join(receiver)
    # msg['Date']='2012-3-16'

    # 构造文字内容
    # text = """我们是微媒共享平台 欢迎您有资源入驻我们平台，长期需要一手媒体资源合作。
    # 目前后台稿件大概一天1000多，提现不需要任何手续费用，如果您有优势的资源也可以入驻进来。一起赚钱。
    # 注册地址：http://www.meijiebao.org.cn/admin/
    # 如果有任何不明白的可以加qq1174796596
    # """
    text_plain = MIMEText(text, 'plain', 'utf-8')
    msg.attach(text_plain)

    # 发送邮件
    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    # 我们用set_debuglevel(1)就可以打印出和SMTP服务器交互的所有信息。
    # smtp.set_debuglevel(1)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()
