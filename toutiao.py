#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time,sys    # 时间函数库，包含休眠函数sleep()
import requests
import random

def select_url(urls):
    url_num = len(urls)
    idx = random.sample(range(url_num), 1)[0]
    return urls[idx]

urls = ['http://www.toutiao.com/i6395480813235864065/',
    'http://www.toutiao.com/i6394392968265990657/', 
    'http://www.toutiao.com/a6395402834254233857/']    # 希望刷阅读量的文章的URL
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
refererData = 'http://www.toutiao.com/i6393266363812545025/'

proxies = {
  'http': 'http://user:passwd@proxy.com:22569',
  'https': 'http://user:passwd@proxy.com:22569',
}


data = ''    # 将GET方法中待发送的数据设置为空
headers = {'User-Agent' : user_agent, 'Referer' : refererData}    # 构造GET方法中的Header
count = 0    # 初始化计数器


while 1:
    requests.get(select_url(urls), headers = headers, proxies = proxies )
    count += 1    # 计数器加1
    time.sleep(random.sample(range(1,5),1)[0] ) #waite for random seconds

    if count % 20 == 0:
        print(count)
    elif count % 100 == 0:
        time.sleep(30)
    elif count == 10000:
        sys.exit("10k complete!")

'''
Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0
'''
