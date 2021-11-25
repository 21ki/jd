#!/usr/bin/env python3 python
# -*- coding:utf-8 _*-
"""
@Author:Myki
@Blog(个人博客地址): https://www.1nth.com
@WeChat Official Account(微信公众号)：MykiFan
@Github:www.github.com  https://github.com/21ki
"""

import sys
import os
import json
try:
    import requests
except Exception as e:
    print(e, "\n缺少requests 模块，请执行命令安装：pip3 install requests")
    #exit(3)
    os.system('pip3 install requests')


data_file = "./file.json"


def Download(url, path, id):
    try:
        r = requests.get("https://ghproxy.com/" + url, timeout=(5, 10))
        print('This is a \033[1;31m ' + r.request.url + '\033[0m!')
        if r.status_code == 200:
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + '/' + id, "wb") as code:
                code.write(r.content)
        else:
            print(url + 'is not FOUND')
    except:
        print(url + ' \033[1;31m filed \033[0m!')


def ParseData(data_file):
    key_url_list = []
    j = json.load(open(data_file))
    files = j['files']
    for item in files:
        url = item['url']
        id = item['id']
        path = item['path']
        # print(url, id, path)
        Download(url, path, id)


def main():
    ParseData(data_file)


if __name__ == "__main__":
    main()

