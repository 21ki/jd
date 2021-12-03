#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@Author:Myki
@Blog(个人博客地址): https://www.1nth.com
@WeChat Official Account(微信公众号)：MykiFan
@Github:www.github.com  https://github.com/21ki
cron: 30 9 * * *
new Env('get_ip_public');
"""

import socket
import requests
import re
from sendNotify import send

title = ''
content = ''

class IP:
    @staticmethod
    def get_ip_public():
        """
        获取本机公网IP
        :return:
        """
        try:
            text = requests.get("http://txt.go.sohu.com/ip/soip").text
            ip_public = re.findall(r'\d+.\d+.\d+.\d+', text)[0]
            return ip_public
        except:
            return '0.0.0.0'

    @staticmethod
    def get_ip_local():
        """
        查询本机内网IP
        :return:
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip


if __name__ == '__main__':
    print("内网IP：{}".format(IP.get_ip_local()))
    print("外网IP：{}".format(IP.get_ip_public()))
    title= "get_ip_public"
    content = IP.get_ip_public()
    send(title, content) 
