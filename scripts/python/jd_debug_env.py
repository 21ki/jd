#!/usr/bin/env python3 python
# -*- coding:utf-8 _*-
"""
@Author:Myki
@Blog(个人博客地址): https://www.1nth.com
@WeChat Official Account(微信公众号)：MykiFan
@Github:www.github.com  https://github.com/21ki
cron: 30 9 * * *
new Env('debuenv');

"""
import os
import subprocess


def get_env():
    # 第二种获取所有变量
    for k, v in os.environ.items():
        print("%s=%s" % (k, v))


def subprocess_():
    """
    subprocess模块执行linux命令
    :return:
    """
    subprocess.call("date")  # 执行ls命令


def main():
    subprocess_()  # 方法1
    get_env()


if __name__ == '__main__':
    main()

