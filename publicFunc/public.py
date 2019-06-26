
import re




def verify_phone_number(phone_number):
    phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
    res = re.search(phone_pat, phone_number)
    flag = False
    if res:
        flag = True
    return flag







