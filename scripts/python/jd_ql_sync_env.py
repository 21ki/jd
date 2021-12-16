import os
import time
import json
import re

try:
    import requests
except Exception as e:
    print(e, "\n缺少requests 模块，请执行命令安装：python3 -m pip install requests")
    exit(3)
# 腾讯云青龙
url1 = "http://106.55.250.198:5700/"
client_id1 = "LIy3zy8DA_-J"
client_secret1 = "t9rg6kPbSEPAtDbyf4zQjn-y"
'''
主青龙office
url2 = "http://ql.1nth.com/"
client_id2 = "NzCL2F_hI4zP"
client_secret2 = "50PQNES7D_e6TxEGywpEl_FT"
'''
# 副本青龙home
url2 = "http://wtj.1nth.com:5700/"
client_id2 = "_PxUQT_7yqda"
client_secret2 = "DU-59spwXA8g9QsfijGmop-H"


def gettimestamp():
    return str(int(time.time() * 1000))


def gettoken(self, url_token):
    r = requests.get(url_token).text
    res = json.loads(r)["data"]["token"]
    self.headers.update({"Authorization": "Bearer " + res})


def login(self, baseurl, client_id_temp, client_secret_temp):
    url_token = baseurl + 'open/auth/token?client_id=' + client_id_temp + '&client_secret=' + client_secret_temp
    gettoken(self, url_token)


def getitem(self, baseurl, key, typ):
    url = baseurl + typ + "/envs?searchValue=%s&t=%s" % (key, gettimestamp())
    r = self.get(url)
    item = json.loads(r.text)["data"]
    return item


def getckitem(self, baseurl, key, typ):
    url = baseurl + typ + "/envs?searchValue=JD_COOKIE&t=%s" % gettimestamp()  # JD_COOKIE为默认的环境变量名，该变量里的值默认含pt_pin和pt_key，其他类似默认按照下面注释改
    r = self.get(url)
    for i in json.loads(r.text)["data"]:
        if key in i["value"]:
            return i
    return []


def update(self, baseurl, typ, text, qlid):
    url = baseurl + typ + "/envs?t=%s" % gettimestamp()
    self.headers.update({"Content-Type": "application/json;charset=UTF-8", 'Connection': 'close'})
    data = {
        "name": "JD_COOKIE",
        "value": text,
        "_id": qlid
    }
    r = self.put(url, data=json.dumps(data))
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return False


def insert(self, baseurl, typ, text, ck_remark, env_name):
    url = baseurl + typ + "/envs?t=%s" % gettimestamp()
    self.headers.update({"Content-Type": "application/json;charset=UTF-8", 'Connection': 'close'})
    data = []
    data_json = {
        "value": text,
        "remarks": ck_remark,
        "name": env_name
    }
    data.append(data_json)
    r = self.post(url, json.dumps(data))
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return False


def delete_jd_cookie(self, baseurl, typ, text):
    url = baseurl + typ + "/envs?t=%s" % gettimestamp()
    self.headers.update({"Content-Type": "application/json;charset=UTF-8", 'Connection': 'close'})
    data = [text]
    r = self.delete(url, data=json.dumps(data))
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return False


def filter_by(stu_info, **kwargs):
    params = kwargs

    for key in params:
        print(stu_info.get(key))
        if stu_info.get(key) != params[key]:
            print(key)
            return False
    return True


if __name__ == '__main__':
    # 先清理客户端cookie
    n1 = requests.session()
    login(n1, url2, client_id2, client_secret2)
    ck_id = getitem(n1, url2, "JD_COOKIE", "open")
    for i in ck_id:
       delete_ck_id = i['_id']
       delete_jd_cookie(n1, url2, "open", delete_ck_id)

    # 同步cookie
    m = requests.session()
    login(m, url1, client_id1, client_secret1)
    ck = getitem(m, url1, "JD_COOKIE", "open")
    c_list = []
    c_id = []
    for i in ck:
        tp = i['value']
        ck_id = i['_id']
        #处理KeyError remark为空
        try:
            ck_remark = i['remarks']
        except KeyError:
            ck_remark = "null"
        env_name = i['name']
        # ptpin = re.findall(r"pt_pin=(.*?);", tp)[0]
        # ptpin = "pt_pin=" + ptpin + ';'
        # ptkey = re.findall(r"pt_key=(.*?);", tp)[0]
        # ptkey = "pt_key=" + ptkey + ';'
        # c = ptkey + ptpin
        # c_list.append(ptpin)
        # c_id.append(ck_id)
        print(json.dumps([ck_id]), env_name,ck_remark)
        insert(n1, url2, "open", tp, ck_remark, env_name)
