import qiniu



def get_qiniu_token():
    SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
    AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'

    # 构建鉴权对象
    q = qiniu.Auth(AccessKey, SecretKey)
    bucket_name = 'bjhzkq_tianyan'
    token = q.upload_token(bucket_name)  # 可以指定key 图片名称
    data = {
        'token': token
    }

    return data
