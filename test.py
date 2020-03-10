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

from requests import ConnectionError
import requests, random, time
from bs4 import BeautifulSoup

URL = 'http://face.39.net/'

# headers = {'User-Agent': pcRequestHeader[random.randint(0, len(pcRequestHeader) - 1)]}
#
# def post_submit_data(content):
#     data = {
#         'context': content,
#         'platform': '39_美容频道'
#     }
#     ret = requests.post('https://xcx.bjhzkq.com/api_hurong/xiaohongshu/check_forbidden_text', data=data)
#     print('ret.status_code--> ', ret.status_code)
#
# def vpsServerQiandao():
#     params_data = {
#         "vpsName": '36.22.188.42:20049',
#         "task_name": "python爬取数据",
#         "area": '浙江嘉兴电信机房拨号VPS「1G型」'
#     }
#     url = "http://websiteaccount.bjhzkq.com/api/vpsServer"
#     requests.get(url, params=params_data)
#
# # 获取栏目
# def get_platform(url, index):
#     if index == 0:
#         request_url = url
#     else:
#         request_url = url.split('index')[0] + 'index_{}.html'.format(index)
#     print('当前页码链接request_url--> ', request_url)
#
#     ret = requests.get(request_url, headers=headers)
#     ret.encoding = 'gbk'
#     if ret.status_code == 200:
#         soup = BeautifulSoup(ret.text, 'lxml')
#         listbox = soup.find('div', class_='listbox')
#         li_tags_list = listbox.find_all('li')
#         for li_tag in li_tags_list:
#             time.sleep(1)
#             href = li_tag.find('a').attrs.get('href')
#             print('获取内容---------> ', href)
#             get_content(href)
#
#         next_objs = soup.find('a', text='下一页')
#         if next_objs:
#             index += 1
#             get_platform(url, index)
#
# def get_content(url):
#     try:
#         ret = requests.get(url, headers=headers)
#         ret.encoding = 'gbk'
#         soup = BeautifulSoup(ret.text, 'lxml')
#         contentText = soup.find('div', id='contentText')
#         p_tags_list = contentText.find_all('p')
#         content = ''
#         for p_tag in p_tags_list:
#             content += p_tag.get_text().replace('\n', '').strip()
#
#         post_submit_data(content)
#     except ConnectionError:
#         pass



# if __name__ == '__main__':
#     print('----------start-------------')
#     data_list = ['http://face.39.net/mrhf/hfyd/jiemian/index.html', 'http://face.39.net/mrhf/hfyd/bs/bsff/index.html', 'http://face.39.net/mrhf/hfyd/ky/kyff/index.html', 'http://face.39.net/mrhf/hfyd/fs/fsff/index.html', 'http://face.39.net/mrhf/hfyd/mb/mbff/index.html', 'http://face.39.net/yz/', 'http://face.39.net/mrhf/hfyd/qd/qdff/index.html', 'http://face.39.net/mrhf/hfyd/qb/qbff/index.html', 'http://face.39.net/mrhf/%E9%97%AE%E9%A2%98%E8%82%8C%E8%82%A4/heitou/index.html', 'http://face.39.net/mrhf/hfyd/kz/index.html', 'http://face.39.net/mrhf/%E9%97%AE%E9%A2%98%E8%82%8C%E8%82%A4/maokongcuda/index.html', 'http://face.39.net/mrhf/%E9%97%AE%E9%A2%98%E8%82%8C%E8%82%A4/heiyanquan/index.html', 'http://face.39.net/mrhf/hfjq/yanbuhuli/index.html', 'http://face.39.net/mrhf/hfjq/bibuhuli/index.html', 'http://face.39.net/mrhf/hfjq/chunbuhuli/index.html', 'http://face.39.net/mrhf/mxhf/index.html', 'http://face.39.net/man/cs/index.html', 'http://face.39.net/hy/index.html', 'http://face.39.net/mrcz/czcs/index.html', 'http://face.39.net/mrcz/czjq/index.html', 'http://face.39.net/mrxf/hfcs/index.html', 'http://face.39.net/mrxf/fxdiy/index.html']
#     for i in data_list:
#         time.sleep(2)
#         print('=============================科室==========》 ', i)
#         get_platform(i, 0)








# print(log_msg.startswith('请求接口异常'))
#
# if log_msg.startswith('请求接口异常'):
#     log_msg = log_msg.replace('请求接口异常: ', '')
#     log_msg = log_msg.split('返回数据->')
#     print(log_msg[0].split('api_url->')[1])
#     print(log_msg[1])
#
#
#
# import datetime
# now_date_time = datetime.datetime.today()
# last_there_days = (now_date_time - datetime.timedelta(days=2))
#
# print(last_there_days)

# data_list = """271784
# 269473
# 271863
# 272056
# 271485
# 271847
# 270406
# 271787
# 271402
# 271893
# 271643
# 269061
# 271090
# 272032
# 271578
# 271665
# 272033
# 271956
# 272029
# 271794
# 271854
# 272042
# 271746
# 269534
# 271735
# 272075
# 271618
# 271858
# 271689
# 271955
# 271851
# 271681
# 271821
# 271996
# 269208
# 271753
# 262230
# 271648
# 271647
# 271933
# 271651
# 271804
# 269211
# 271743
# 271636
# 271975
# 272007
# 271898
# 269236
# 270919
# 271812
# 263845
# 271998
# 271678
# 272069
# 269643
# 271706
# 270544
# 271786
# 272022
# 271740
# 258927
# 271806
# 272044
# 272035
# 271654
# 271704
# 271775
# 271755
# 271638
# 271763
# 271721
# 271897
# 271785
# 271842
# 271964
# 271748
# 271875
# 271712
# 271968
# 271758
# 271959
# 271780
# 271790
# 271938
# 271776
# 271620
# 271754
# 271822
# 272001
# 271978
# 271946
# 271690
# 271614
# 271896
# 272041
# 271902
# 271757
# 271887
# 271662
# 271716
# 271931
# 271697
# 271865
# 271711
# 271814
# 272051
# 271833
# 271862
# 272009
# 271686
# 271856
# 271635
# 271609
# 271980
# 271737
# 271769
# 271682
# 271781
# 271984
# 271839
# 272057
# 271936
# 272027
# 271675
# 272063
# 271824
# 271634
# 271715
# 271880
# 271688
# 271695
# 271954
# 271756
# 271707
# 271994
# 271624
# 271937
# 271900
# 271916
# 271879
# 271767
# 271733
# 271890
# 271726
# 271818
# 271717
# 271799
# 272000
# 271943
# 271680
# 271861
# 271883
# 272012
# 271718
# 270893
# 271071
# 271523
# 271714
# 271774
# 269191
# 271069
# 271826
# 263882
# 270843
# 271830
# 271782
# 271640
# 271720
# 271752
# 271742
# 271741
# 271674
# 272037
# 271584
# 271864
# 271844
# 271810
# 271617
# 271951
# 271891
# 271882
# 271981
# 271940
# 271677
# 272062
# 271935
# 271849
# 271819
# 271848
# 271825
# 271942
# 271909
# 271725
# 271664
# 271941
# 271766
# 271795
# 271800
# 271761
# 271988
# 271808
# 271626
# 271970
# 271657
# 271693
# 271036
# 271044
# 271960
# 271692
# 272061
# 271881
# 271884
# 271899
# 271867
# 271820
# 271724
# 272036
# 271872
# 271886
# 271731
# 272072
# 272018
# 271859
# 271846
# 271708
# 271930
# 271670
# 271905
# 271929
# 271644
# 271729
# 271877
# 271650
# 271723
# 270646
# 271835
# 272031
# 271793
# 269044
# 271888
# 271658
# 272040
# 271990
# 272015
# 271967
# 270672
# 271816
# 271773
# 271687
# 271831
# 271962
# 271079
# 272058
# 271911
# 271772
# 272028
# 271947
# 271732
# 271777
# 271928
# 271811
# 272026
# 271702
# 272077
# 271744
# 271770
# 272060
# 271850
# 271903
# 271628
# 146426
# 271843
# 271958
# 271736
# 271920
# 272024
# 271973
# 271828
# 271969
# 271807
# 271857
# 271901
# 271834
# 271945
# 271779
# 271749
# 271987
# 271915
# 272014
# 271852
# 271892
# 271924
# 272023
# 271868
# 271747
# 271700
# 271751
# 271115
# 271832
# 271869
# 271645
# 271764
# 271750
# 269480
# 272020
# 271927
# 271791
# 271986
# 271910
# 271652
# 271870
# 271709
# 271876
# 271659
# 271727
# 271698
# 271760
# 271629
# 271649
# 271623
# 271639
# 270829
# 271660
# 270573
# 262206
# 267798
# 270323
# 270458
# 268694
# 270956
# 271001
# 262435
# 250032
# 270467
# 270388
# 271300
# 265687
# 270529
# 259627
# 269638
# 265897
# 271201
# 270800
# 270532
# 270488
# 269672
# 270821
# 269595
# 270756
# 270460
# 269587
# 270513
# 270938
# 270418
# 269645
# 271397
# 269842
# 266981
# 270501
# 270125
# 269569
# 270540
# 261521
# 270793
# 265781
# 269629
# 271566
# 270503
# 271048
# 271334
# 271274
# 271107
# 271393
# 271532
# 271546
# 271459
# 271317
# 271563
# 271337
# 271543
# 271374
# 271491
# 271351
# 271504
# 271598
# 271385
# 271551
# 271576
# 271439
# 271506
# 271395
# 271463
# 271262
# 271430
# 271362
# 271315
# 271387
# 271420
# 271481
# 271587
# 271357
# 271355
# 271579
# 271399
# 271516
# 271376
# 271479
# 271603
# 271383
# 271535
# 271235
# 271230
# 271446
# 271601
# 271332
# 271229
# 271250
# 271304
# 270782
# 271352
# 271558
# 271489
# 271429
# 271295
# 271448
# 271318
# 271220
# 271484
# 271378
# 271236
# 271513
# 271496
# 271581
# 271227"""
#
#
# data_two_list = """270639
# 272497
# 272479
# 272504
# 272524
# 272214
# 272376
# 272193
# 272260
# 272100
# 272397
# 272129
# 272483
# 272478
# 272203
# 271860
# 272226
# 272258
# 272196
# 272223
# 272115
# 272177
# 272242
# 272515
# 272198
# 272543
# 272499
# 272130
# 272181
# 272360
# 272470
# 272343
# 272481
# 272334
# 272255
# 272136
# 272119
# 272508
# 272082
# 272081
# 272492
# 272539
# 272150
# 272084
# 272261
# 272490
# 272550
# 272143
# 272102
# 272516
# 272388
# 272327
# 272415
# 272417
# 272290
# 272322
# 272399
# 272299
# 272329
# 272289
# 272411
# 272407
# 272422
# 272421
# 272313
# 272414
# 272395
# 272340
# 272459
# 272291
# 272306
# 272279
# 272052
# 272314
# 272319
# 272427
# 272297
# 272307
# 272296
# 272442
# 272365
# 272373
# 272304
# 272278
# 272271
# 272362
# 272335
# 272294
# 272452
# 272438
# 272400
# 272292
# 272312
# 272434
# 272432
# 272440
# 272460
# 272276
# 272380
# 272447
# 272305
# 272458
# 272389
# 272333
# 272344
# 272341
# 272316
# 272370
# 272331
# 272282
# 272428
# 272379
# 272445
# 272315
# 272288
# 272387
# 272275
# 272301
# 272302
# 272137
# 272085
# 272366
# 272158
# 272109
# 272157
# 272089
# 272257
# 272111
# 272243
# 272353
# 272117
# 272233
# 272124
# 272092
# 272099
# 264078
# 271495
# 271802
# 271977
# 267277
# 271829
# 269167
# 271768
# 271703
# 266197
# 271549
# 270896
# 271926
# 272053
# 168204
# 263023
# 269157
# 271803
# 272008
# 271789
# 272030
# 251769
# 271792
# 271627"""
#
# data = []
# for i in data_two_list.split('\n'):
#     data.append(int(i))
# print(data)

# import redis
#
# redis_obj = redis.StrictRedis(host='120.133.21.53', port=1110, db=0, decode_responses=True)
# keys = redis_obj.keys("XHS_SCREEN*")
# for key in keys:
#     print('key-----> ', key)
    # uid = key.replace('XHS_SCREEN_', "")
    # data = redis_obj.get(key)
    #
    # data = json.loads(data)
    # links = data["links"]
    #
    # if len(links) > 0:
    #     keywords = data["keywords"]
    #     query_list = []
    #     for keyword in keywords:
    #         if not models.xhs_bpw_keywords.objects.filter(uid=uid, keywords=keyword):
    #             query_list.append(models.xhs_bpw_keywords(uid=uid, keywords=keyword))
    #     models.xhs_bpw_keywords.objects.bulk_create(query_list)
    #     query_list = []
    #     for link in links:
    #         # 处理短链接
    #         while_flag = 0
    #         while True:
    #             while_flag += 1
    #             try:
    #                 if link.startswith("http://t.cn"):
    #                     ret = requests.get(link, allow_redirects='false')
    #                     link = re.findall('HREF="(.*?)"', ret.text)[0].split('?')[0]
    #             except Exception:
    #                 continue
    #             if while_flag >= 5:
    #                 break
    #
    #         if not models.xhs_bpw_biji_url.objects.filter(uid=uid, biji_url=link):
    #             query_list.append(models.xhs_bpw_biji_url(uid=uid, biji_url=link))
    #     models.xhs_bpw_biji_url.objects.bulk_create(query_list)


# p = 'http://t.cn/AiHPm79U,http://t.cn/AiHhXUoX,http://t.cn/AiHUfF7C,http://t.cn/AiHhS6rm,http://t.cn/AiHUQXUS,http://t.cn/AiHcINnD,http://t.cn/AiHKSV9H,http://t.cn/AiHYeACt,http://t.cn/AiH31JQj,http://t.cn/AiHK5vNa,http://t.cn/AiHYdmnB,http://t.cn/AiH33I37,http://t.cn/AiHKtAlA,http://t.cn/AiHYeOkr,http://t.cn/AiH1EEBy,http://t.cn/AiHTL7WV,http://t.cn/AiH1ZIsk,http://t.cn/AiQwYLCB,http://t.cn/AiQLsvEY,http://t.cn/AiH31iMx,http://t.cn/AiQazN9k,http://t.cn/AiQwY50x,http://t.cn/AiQf6Emz,http://t.cn/AiQWpNqK,http://t.cn/AiQYbzfp,http://t.cn/AiQfibgV,http://t.cn/AiQfavlv,http://t.cn/AiQKTLea,http://t.cn/AiQWphgo,http://t.cn/AiQY4wIE,http://t.cn/AiQIZrH2,http://t.cn/AiQfS8Yh,http://t.cn/AiQfHfce,http://t.cn/AiQf6daV,http://t.cn/AiQfoD30,http://t.cn/AiQaz1OU,http://t.cn/AiQaZDbY,http://t.cn/AiQKTwHU,http://t.cn/AiQ9vo3m,http://t.cn/AiQlUYv3,http://t.cn/AiQKTrPZ,http://t.cn/AiQ9x9UG,http://t.cn/AiQWNkkX,http://t.cn/AiQKTAkB,http://t.cn/AiQWp2XE,http://t.cn/AiQY4c4g,http://t.cn/AiQKQv8Q,http://t.cn/AiQWNkou,http://t.cn/AiQYUEbB,http://t.cn/AiQl5ANm,http://t.cn/AiQYUFVX,http://t.cn/AiQYxPDt,http://t.cn/AiQYoqOh'
#
# for i in p.split(','):
#     print('i-----> ', i)


# def index(start, stop):
#     for i in range(start):
#         print(i)


# def test_1():
#     p = {
#     "code":200,
#     "note":{
#
#     },
#     "msg":"查询成功",
#     "data":{
#         "ret_data":[
#             {
#                 "phone_id":301,
#                 "phone_name":"b-53",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:17:39",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 10:59:53",
#                 "phone_number":"15636437304",
#                 "status":"待审核",
#                 "user_id":238,
#                 "user_name":"沦为旧友",
#                 "id":6198,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571307473&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571307473&encrypt=351Vgk934y",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"做双眼皮之前你是什么想法呢？深圳",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/17/微信图片_20191010154500.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/17/微信图片_20191010154543.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/17/微信图片_20191010154548.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":303,
#                 "phone_name":"b-55",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:19:07",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:18:03",
#                 "phone_number":"13039915820",
#                 "status":"待审核",
#                 "user_id":240,
#                 "user_name":"只剩沉默",
#                 "id":6199,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571307561&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571307561&encrypt=OJ1ZEWArPM",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"你们是什么原因想做鼻子的呢？深圳",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/15/mmexport1568298962158.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/15/mmexport1568298910982.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/15/mmexport1568298925993.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":304,
#                 "phone_name":"b-56",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:19:29",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-16 10:27:06",
#                 "phone_number":"15545079864",
#                 "status":"待审核",
#                 "user_id":241,
#                 "user_name":"时光是个罪人",
#                 "id":6200,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571307583&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571307583&encrypt=y516LNANmB",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"我在深圳做面部埋线啦～歪脸妹妹",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/16/IMG20191009172642.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/16/IMG20191009172656_48505157.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/16/IMG20191009172651_10210110.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/16/IMG20190907214216.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":463,
#                 "phone_name":"c-73",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:25:59",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:26:04",
#                 "phone_number":"13199326948",
#                 "status":"待审核",
#                 "user_id":382,
#                 "user_name":"娇纵小可爱",
#                 "id":6204,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571307973&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571307973&encrypt=qZmRgpX2P3",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"北京|大腿吸脂修复小知识了解下",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/11/542920090010375389.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/11/36952037041519353.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/11/466175550748266915.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":468,
#                 "phone_name":"c-77",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:24:22",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:24:24",
#                 "phone_number":"17131405746",
#                 "status":"待审核",
#                 "user_id":386,
#                 "user_name":"诺贝尔可爱奖",
#                 "id":6201,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571307876&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571307876&encrypt=G5PMrRqB1l",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"双眼皮修复你以为什么时候都能做吗？",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/08/5a3050a749e862814e552b665247562_副本_49995555.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":469,
#                 "phone_name":"c-78",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:24:56",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:24:54",
#                 "phone_number":"17158786384",
#                 "status":"待审核",
#                 "user_id":387,
#                 "user_name":"祖国的棒槌",
#                 "id":6202,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571307910&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571307910&encrypt=KNPANydG1d",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"攻略来了~双眼皮修复术后这么吃！",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/14/40561083789553259.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/14/196962894537955234.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/14/441138248809952533.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":470,
#                 "phone_name":"c-79",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:25:23",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:25:26",
#                 "phone_number":"17131405864",
#                 "status":"待审核",
#                 "user_id":388,
#                 "user_name":"王振军双眼皮修复",
#                 "id":6203,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571307937&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571307937&encrypt=Wq10wrZ7PM",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"想要双眼皮修复自然  要多长时间",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/11/想要双眼皮修复自然 需要多长的时间.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/11/微信图片_20180921150554_副本.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":478,
#                 "phone_name":"c-89",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:27:34",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:27:31",
#                 "phone_number":"17158788314",
#                 "status":"待审核",
#                 "user_id":398,
#                 "user_name":"跟空气撒个娇",
#                 "id":6207,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571308068&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571308068&encrypt=351VgkoA4y",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"做完鼻子感觉很失败，不是理想型",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/08/783818254671931316.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/08/809045159652167518.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/08/881133288362773067.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":479,
#                 "phone_name":"c-90",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:28:34",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:28:42",
#                 "phone_number":"17158788294",
#                 "status":"待审核",
#                 "user_id":399,
#                 "user_name":"笑里藏刀我不会",
#                 "id":6208,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571308128&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571308128&encrypt=654KzrG81y",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"做鼻子后的恢复期 忌口也要吃的舒服啊",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/08/生活照 (22)_49565455.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/08/生活照 (23)_49579950.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/08/术后 (3).jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":480,
#                 "phone_name":"c-94",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:29:51",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:29:59",
#                 "phone_number":"17158788734",
#                 "status":"待审核",
#                 "user_id":400,
#                 "user_name":"你我只差一个爱字",
#                 "id":6209,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571308205&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571308205&encrypt=KZ1pZ7vBmn",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"做鼻子有失败的可能吗？做好这些就不用怕",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/09/29/535995507904326756.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/09/29/696292625479014634.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/09/29/769305524221829026.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":485,
#                 "phone_name":"c-96",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:30:43",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:30:46",
#                 "phone_number":"17158788745",
#                 "status":"待审核",
#                 "user_id":405,
#                 "user_name":"等你王者归来—Kris",
#                 "id":6210,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571308257&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571308257&encrypt=VL1zV5vy1Y",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"双眼皮对外貌的影响也太大了吧~",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/09/26/IMG_7660.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/09/26/IMG_7669.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/09/26/IMG_7657.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":488,
#                 "phone_name":"c-99",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:31:35",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:31:43",
#                 "phone_number":"17158788743",
#                 "status":"待审核",
#                 "user_id":408,
#                 "user_name":"媛小媛",
#                 "id":6212,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571308309&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571308309&encrypt=OJ1ZEWeQPM",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"做鼻子有黄金年龄吗？",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/09/27/1 (12).jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/09/27/1 (13).jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":489,
#                 "phone_name":"c-100",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:26:25",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:26:31",
#                 "phone_number":"13214570510",
#                 "status":"待审核",
#                 "user_id":409,
#                 "user_name":"玲玲秋",
#                 "id":6205,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571307999&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571307999&encrypt=oM436Xr719",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"做了腿型矫正，终于告别了O型腿！",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/09/术前 (25)_副本.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/09/后_副本_10153555.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":489,
#                 "phone_name":"c-100",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:31:15",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:31:17",
#                 "phone_number":"13214570510",
#                 "status":"待审核",
#                 "user_id":409,
#                 "user_name":"玲玲秋",
#                 "id":6211,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571308289&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571308289&encrypt=wpm8bJ3Y16",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"问我为什么做双心脸？因为可以变美呀！",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/09/29/术前 (1).jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/09/29/术前 (3).jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             },
#             {
#                 "phone_id":491,
#                 "phone_name":"c-102",
#                 "reading_num":0,
#                 "create_datetime":"2019-10-17 18:26:51",
#                 "biji_url":'null',
#                 "is_delete_old_biji":'false',
#                 "biji_existing_url":'null',
#                 "completion_time":'null',
#                 "status_id":3,
#                 "error_msg":'null',
#                 "biji_type_id":1,
#                 "update_reding_num_time":"",
#                 "biji_type":"img",
#                 "release_time":"2019-10-17 18:26:48",
#                 "phone_number":"13199327804",
#                 "status":"待审核",
#                 "user_id":411,
#                 "user_name":"一只喵的碎碎念",
#                 "id":6206,
#                 "platform":1,
#                 "content":{
#                     "video_url":"https://www.ppxhs.com/show/download-video.html?time=1571308025&video=",
#                     "content":"https://www.ppxhs.com/show/screen-article.html?time=1571308025&encrypt=WAPkaWgY4E",
#                     "@":"",
#                     "topic_name":"",
#                     "location":"",
#                     "title":"北京吸脂经历分享 终于有了漫画腿",
#                     "publish_id":0,
#                     "img_list":[
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/10/术前 (79)_副本.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         },
#                         {
#                             "url":"https://cdn.dmh.bjhzkq.com/cdnppxhs/attachment/images/2019/10/10/术后第七天 (3)_副本.jpg",
#                             "tag":{
#                                 "name":"",
#                                 "location":""
#                             }
#                         }
#                     ],
#                     "type":"images"
#                 }
#             }
#         ],
#         "status_choices":[
#             {
#                 "name":"发布中",
#                 "id":1
#             },
#             {
#                 "name":"已发布",
#                 "id":2
#             },
#             {
#                 "name":"待审核",
#                 "id":3
#             },
#             {
#                 "name":"发布异常",
#                 "id":4
#             },
#             {
#                 "name":"重新发布",
#                 "id":5
#             }
#         ],
#         "count":15,
#         "biji_type_choices":[
#             {
#                 "name":"img",
#                 "id":1
#             },
#             {
#                 "name":"video",
#                 "id":2
#             }
#         ]
#     }}
#     m = ''
#     for i in p['data']['ret_data']:
#         m += ',{}'.format(i.get('id'))
#     print(m)
#
# if __name__ == '__main__':
#     test_1()



#
# p = {'errmsg': 'access_token expired hint: [I502049019!]', 'errcode': 42001}
#
# if p.get('errcode') not in [0, '0']:
#     print('==-')
import time, json, datetime, xml.etree.cElementTree as ET
from publicFunc.crypto_.WXBizMsgCrypt import WXBizMsgCrypt


Encrypt = 'tviRkAmpApm7QlYLdpp47GHeIjiOX7r+CbGbawNGAbPZVvrq7Kb6ChJg1n86ThRJe1IZg3w/JldHLhP+KfnpNSuC5nhz0783Cvyawj72z/7WyGOZup6S+SJALFz5T7mL/X4fo+RJWjX+34FFVu7eWonfnDxMJ4EOKpxC4fPz7QzkMkcZRHKzbVqYN6iW5AYGpT0OrocNt24rUUQpCJQUGPUdiskb9OhbyjXQZBeOesfrhmvIW4/In3gpQzFjsUQlS0MSRPpktXqkKGzaQof6Mnh/6tw1HbudQiYQKw3ty5YFR6MU6DMfjKuAR8Afq3iw7bURhwuqUZoMY6OyEk3mtYKUWMXbiL6JFSL3bNKzCTC09OG4SmXoMsFls2/GxAZ1IypINiJysSsSiRNOb8Lew5MqIoTBGny+iRhxrn6MbRva2mEmRd7jZGlWWRJnJTyW416HP5ieAlbI1loi1g5aag=='
msg_signature = '5775896b713804e262a3b0e03474f146e91b5323'
timestamp = '1578019256'
nonce = '2035862656'

encoding_token = ''
encodingAESKey = ''
encoding_appid = ''

# print('Encrypt, msg_signature, timestamp, nonce-----------------------> ', Encrypt, msg_signature, timestamp, nonce)


wx_obj = WXBizMsgCrypt('sisciiZiJCC6PuGOtFWwmDnIHMszxp', 'sisciiZiJCC6PuGOtFWwmDnIHMsZyXmDnIHMsZyXzxp', 'wx531f7fb3f30231b3')


# ret, decryp_xml = wx_obj.DecryptMsg(Encrypt, msg_signature, timestamp, nonce)

# print(decryp_xml)
# decryp_xml_tree = ET.fromstring(decryp_xml)
# oper_type = decryp_xml_tree.find("InfoType").text
from urllib import parse

phone_number = '13089927032'

data = {
    # "login_url": "http://103.99.210.71:1111",
    "username": "张聪296",
    "password": "zhang_cong.123",
    # "_tn": "NjA4MzNDQUY0REFFNjA4N0FEQTRENzQwQTY2Nzc1NDc%3D",
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}
#
# requests_obj = requests.Session()
# login_url = 'http://103.99.210.71:1111/index.php?g=cust&m=login&a=dologin'
# ret = requests_obj.post(url=login_url, headers=headers, data=data)


# print(json.loads(ret.text))
# print(ret.text)

# ret = requests_obj.get('http://103.99.210.71:1111/index.php?g=cust&m=center&a=index')
# print('-_----------------> ', ret.text)
# now = datetime.date.today()
# yzm_url = data.get('login_url') + '/index.php?g=cust&m=smscust&a=receive'
# data = {
#     'startDate': now,
#     'endDate': now,
#     'mobile': phone_number,
# }

# ret = requests_obj.post(yzm_url, headers=headers, data=data)
# print(ret.text)
# soup = BeautifulSoup(ret.text, 'lxml')
# content = soup.find('div', class_='tab-content')


# !/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# Author: jonyqin
# Created Time: Thu 11 Sep 2014 03:55:41 PM CST
# File Name: demo.py
# Description: WXBizMsgCrypt 使用demo文件
#########################################################################

