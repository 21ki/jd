#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@Author:Myki
@Blog(个人博客地址): https://www.1nth.com
@WeChat Official Account(微信公众号)：MykiFan
@Github:www.github.com  https://github.com/21ki
cron: 50 23 * * *
new Env('jd_sync_ck')
"""
import time
import requests
import json
import re

data_file = "account.json"
url = ""

payload = {}
headers = {}


def gettimestamp():
    return str(int(time.time() * 1000))


def check_url(host, token):
    url = host + "open/configs/files"
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json;charset=UTF-8'
    }
    try:
        r = requests.request("GET", url, headers=headers, data=payload, timeout=15)
        if json.loads(r.text)["code"] == 200:
            print("url有效")
            return 200
        elif json.loads(r.text)["code"] == 401:
            print("token无效")
            return 401
        else:
            print("未知错误")
            return 500
    except requests.exceptions.ConnectionError:
        print("url不可用")
        return 500


def gettoken(host, client_id, client_secret):
    url = host + 'open/auth/token?client_id=' + client_id + '&client_secret=' + client_secret
    r = requests.request("GET", url, headers=headers, data=payload).text
    # r = requests.get(url).text
    if json.loads(r)["code"] == 200:
        token = json.loads(r)["data"]["token"]
        expiration = json.loads(r)["data"]["expiration"]
    else:
        print(url + 'is not FOUND')
    return token, expiration


def getitem(host, token, searchValue):
    url = host + "open/envs?searchValue=%s&t=%s" % (searchValue, gettimestamp())
    headers = {
        "Authorization": "Bearer " + token
    }
    r = requests.request("GET", url, headers=headers, data=payload)
    try:
        item = json.loads(r.text)["data"]
        return item
    except KeyError:
        return False


def update_json(token_dst_y, expiration_dst_y, account, json_count):
    with open(data_file, "r", encoding="utf-8") as jsonFile:
        data = json.load(jsonFile)

    data[account][json_count]["token"] = token_dst_y
    data[account][json_count]["expiration"] = expiration_dst_y * 1000
    with open(data_file, "w") as jsonFile:
        json.dump(data, jsonFile, ensure_ascii=False, indent=4)
    jsonFile.close()


# 插入ck
def insert(host, token, ck_v, ck_remark, env_name):
    url = host + "open/envs?t=%s" % gettimestamp()
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json;charset=UTF-8'
    }
    data = []
    data_json = {
        "value": ck_v,
        "remarks": ck_remark,
        "name": env_name
    }

    data.append(data_json)
    payload = json.dumps(data)
    r = requests.request("POST", url, headers=headers, data=payload)
    item = json.loads(r.text)["data"]
    return item


def delete_ck(host, token, ck_id_list):
    url = host + "open/envs?t=%s" % gettimestamp()
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json;charset=UTF-8'
    }
    payload = json.dumps(ck_id_list)
    r = requests.request("DELETE", url, headers=headers, data=payload)
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return False


def check_ck(ck):
    url = "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion"
    payload = {}
    headers = {
        'Host': 'me-api.jd.com',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Cookie': ck,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1',
        'Accept-Language': 'zh-cn',
        'Referer': 'https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    try:
        r = requests.request("GET", url, headers=headers, data=payload)
        # print(r.text)
        data = r.json()
        if data['retcode'] == "1001":
            print("cookie不可用")
            return False
        else:
            nickname = data['data']['userInfo']['baseInfo']['nickname']
            print(nickname)
            return nickname
    except Exception as e:
        print("此cookie无法完成检测，请自行斟酌！\n\n{cookie}\n\n错误：{e}")
        return True


def main():
    j = json.load(open(data_file))
    # DST_QL服务器信息
    dst_host = j["dst_account"][0]["host"]
    dst_token = j["dst_account"][0]["token"]
    dst_client_id = j["dst_account"][0]["client_id"]
    dst_client_secret = j["dst_account"][0]["client_secret"]
    expiration = j["dst_account"][0]["expiration"]
    check_host = check_url(dst_host, dst_token)
    if check_host == 200:
        print("url可用")
    elif check_host == 401:
        print("401")
        token_dst_y, expiration_dst_y = gettoken(dst_host, dst_client_id, dst_client_secret)
        update_json(token_dst_y, expiration_dst_y, "dst_account", dst_count)

    files = j['src_account']
    uncount = 0
    for item in files:
        time_now = gettimestamp()
        host = item['host']
        id = item['id']
        expiration = item['expiration']
        client_id = item['client_id']
        client_secret = item['client_secret']
        remarks = item['remarks']
        token = item['token']
        print(
            '\033[1;31m====================================================== 执行第{}个账号 =====================================================\033[0m'.format(
                uncount + 1))
        print()
        # print(remarks + " {}".format(host))

        # 判断token是否失效
        check_host = check_url(dst_host, dst_token)
        if check_host == 200:
            print("url可用")
        elif check_host == 401:
            print("401")
            token_y, expiration_y = gettoken(host, client_id, client_secret)
            update_json(token_y, expiration_y, "src_account", uncount)

        # 获取客户端JD_COOKIE
        check_host = check_url(host, token)
        # 判断token是否可用不可用直接跳过下一个账号
        if check_host == 200:
            print("url可用")
            ck = getitem(host, token, "JD_COOKIE")
            c_list = []
            c_id = []
            print('执行同步中......')
            for i in ck:
                ck_v = i['value']
                ck_id = i['_id']
                ck_name = i['name']
                try:
                    ck_remark = i['remarks']
                except KeyError:
                    ck_remark = "null"
                print(ck_v, ck_remark, ck_name)
                insert(dst_host, dst_token, ck_v, ck_remark, ck_name)

        elif check_host == 401:
            print("401")
            token_y, expiration_y = gettoken(host, client_id, client_secret)
            update_json(token_y, expiration_y, "src_account", uncount)

            ck = getitem(host, token_y, "JD_COOKIE")
            c_list = []
            c_id = []
            print('执行同步中......')
            for i in ck:
                ck_v = i['value']
                ck_id = i['_id']
                ck_name = i['name']
                try:
                    ck_remark = i['remarks']
                except KeyError:
                    ck_remark = "null"
                print(ck_v, ck_remark, ck_name)
                insert(dst_host, dst_token, ck_v, ck_remark, ck_name)

        else:
            continue
        uncount += 1

    # 清理重复的CK
    dst_ql_ck_id = getitem(dst_host, dst_token, "JD_COOKIE")
    ck_id_dict = {}
    ck_id_list = []
    for i in dst_ql_ck_id:
        ptpin = re.findall(r"pt_pin=(.*?);", i["value"])[0]
        id = i['_id']
        dict1 = {ptpin: id}
        if ptpin not in ck_id_dict:
            ck_id_dict.update(dict1)
        else:
            ck_id_list.append(id)
    print(ck_id_list)
    delete_ck(dst_host, dst_token, ck_id_list)


if __name__ == "__main__":
    main()
