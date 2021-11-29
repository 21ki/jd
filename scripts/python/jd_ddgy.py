#!/usr/bin/python3
# -*- coding: utf8 -*-
"""
cron: 30 9 * * *
new Env('订单公益');
入口：https://gongyi.m.jd.com/m/welfare/donate/index.html?projectId=941&inviteCode=9879c00ca80744c9abb10a125b27ea6f&_ts=1636595385378&utm_user=plusmember&ad_od=share&utm_source=androidapp&utm_medium=appshare&utm_campaign=t_335139774&utm_term=Wxfriends
"""

# 是否开启通知，Ture：发送通知，False：不发送
isNotice = True
# UA 可自定义你的, 默认随机生成UA。
UserAgent = ''

import json
import random
import os, re, sys
from urllib.parse import unquote
from urllib.parse import quote

try:
    import requests
except Exception as e:
    print(e, "\n缺少requests 模块，请在青龙后台-依赖管理-Python3 搜索安装")
    exit(3)

try:
    import aiohttp
except Exception as e:
    print(e, "\n缺少aiohttp 模块，请在青龙后台-依赖管理-Python3 搜索安装")
    exit(3)

try:
    import asyncio
except Exception as e:
    print(e, "\n缺少asyncio 模块，请在青龙后台-依赖管理-Python3 搜索安装")
    exit(3)

##############

requests.packages.urllib3.disable_warnings()
# host_api = 'https://api.m.jd.com/client.action'
pwd = os.path.dirname(os.path.abspath(__file__)) + os.sep

def getEnvs(label):
    try:
        if label == 'True' or label == 'yes' or label == 'true' or label == 'Yes':
            return True
        elif label == 'False' or label == 'no' or label == 'false' or label == 'No':
            return False
    except:
        pass
    try:
        if '.' in label:
            return float(label)
        elif '&' in label:
            return label.split('&')
        elif '@' in label:
            return label.split('@')
        else:
            return int(label)
    except:
        return label


class getJDCookie(object):
    # 适配各种平台环境ck

    def getckfile(self):
        global v4f
        curf = pwd + 'JDCookies.txt'
        v4f = '/jd/config/config.sh'
        ql_new = '/ql/config/env.sh'
        ql_old = '/ql/config/cookie.sh'
        if os.path.exists(curf):
            with open(curf, "r", encoding="utf-8") as f:
                cks = f.read()
                f.close()
            r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
            cks = r.findall(cks)
            if len(cks) > 0:
                return curf
            else:
                pass
        if os.path.exists(ql_new):
            print("当前环境青龙面板新版")
            return ql_new
        elif os.path.exists(ql_old):
            print("当前环境青龙面板旧版")
            return ql_old
        elif os.path.exists(v4f):
            print("当前环境V4")
            return v4f
        return curf

    # 获取cookie
    def getCookie(self):
        global cookies
        ckfile = self.getckfile()
        try:
            if os.path.exists(ckfile):
                with open(ckfile, "r", encoding="utf-8") as f:
                    cks = f.read()
                    f.close()
                if 'pt_key=' in cks and 'pt_pin=' in cks:
                    r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
                    cks = r.findall(cks)
                    if len(cks) > 0:
                        if 'JDCookies.txt' in ckfile:
                            print("当前获取使用 JDCookies.txt 的cookie")
                        cookies = ''
                        for i in cks:
                            if 'pt_key=xxxx' in i:
                                pass
                            else:
                                cookies += i
                        return
            else:
                with open(pwd + 'JDCookies.txt', "w", encoding="utf-8") as f:
                    cks = "#多账号换行，以下示例：（通过正则获取此文件的ck，理论上可以自定义名字标记ck，也可以随意摆放ck）\n账号1【Curtinlv】cookie1;\n账号2【TopStyle】cookie2;"
                    f.write(cks)
                    f.close()
            if "JD_COOKIE" in os.environ:
                if len(os.environ["JD_COOKIE"]) > 10:
                    cookies = os.environ["JD_COOKIE"]
                    print("已获取并使用Env环境 Cookie")
        except Exception as e:
            print(f"【getCookie Error】{e}")

    # 检测cookie格式是否正确
    def getUserInfo(self, ck, pinName, userNum):
        url = 'https://me-api.jd.com/user_new/info/GetJDUserInfoUnion?orgFlag=JD_PinGou_New&callSource=mainorder&channel=4&isHomewhite=0&sceneval=2&sceneval=2&callback=GetJDUserInfoUnion'
        headers = {
            'Cookie': ck,
            'Accept': '*/*',
            'Connection': 'close',
            'Referer': 'https://home.m.jd.com/myJd/home.action',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'me-api.jd.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'zh-cn'
        }
        try:
            resp = requests.get(url=url, verify=False, headers=headers, timeout=60).text
            r = re.compile(r'GetJDUserInfoUnion.*?\((.*?)\)')
            result = r.findall(resp)
            userInfo = json.loads(result[0])
            nickname = userInfo['data']['userInfo']['baseInfo']['nickname']
            return ck, nickname
        except Exception:
            context = f"账号{userNum}【{pinName}】Cookie 已失效！请重新获取。"
            print(context)
            return ck, False

    def iscookie(self):
        """
        :return: cookiesList,userNameList,pinNameList
        """
        cookiesList = []
        userNameList = []
        pinNameList = []
        if 'pt_key=' in cookies and 'pt_pin=' in cookies:
            r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
            result = r.findall(cookies)
            if len(result) >= 1:
                print("您已配置{}个账号\n".format(len(result)))
                u = 1
                for i in result:
                    r = re.compile(r"pt_pin=(.*?);")
                    pinName = r.findall(i)
                    pinName = unquote(pinName[0])
                    # 获取账号名
                    ck, nickname = self.getUserInfo(i, pinName, u)
                    if nickname != False:
                        cookiesList.append(ck)
                        userNameList.append(nickname)
                        pinNameList.append(pinName)
                    else:
                        u += 1
                        continue
                    u += 1
                if len(cookiesList) > 0 and len(userNameList) > 0:
                    return cookiesList, userNameList, pinNameList
                else:
                    print("没有可用Cookie，已退出")
                    exit(3)
            else:
                print("cookie 格式错误！...本次操作已退出")
                exit(4)
        else:
            print("cookie 格式错误！...本次操作已退出")
            exit(4)


getCk = getJDCookie()
getCk.getCookie()

# 获取v4环境 特殊处理
try:
    with open(v4f, 'r', encoding='utf-8') as v4f:
        v4Env = v4f.read()
    r = re.compile(r'^export\s(.*?)=[\'\"]?([\w\.\-@#&=_,\[\]\{\}\(\)]{1,})+[\'\"]{0,1}$',
                   re.M | re.S | re.I)
    r = r.findall(v4Env)
    curenv = locals()
    for i in r:
        if i[0] != 'JD_COOKIE':
            curenv[i[0]] = getEnvs(i[1])
except:
    pass


def userAgent():
    """
    随机生成一个UA
    :return: jdapp;iPhone;9.4.8;14.3;xxxx;network/wifi;ADID/201EDE7F-5111-49E8-9F0D-CCF9677CD6FE;supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone13,4;addressid/2455696156;supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1
    """
    if not UserAgent:
        uuid = ''.join(random.sample('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 40))
        addressid = ''.join(random.sample('1234567898647', 10))
        iosVer = ''.join(
            random.sample(["14.5.1", "14.4", "14.3", "14.2", "14.1", "14.0.1", "13.7", "13.1.2", "13.1.1"], 1))
        iosV = iosVer.replace('.', '_')
        iPhone = ''.join(random.sample(["8", "9", "10", "11", "12", "13"], 1))
        ADID = ''.join(random.sample('0987654321ABCDEF', 8)) + '-' + ''.join(
            random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(
            random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 12))
        return f'jdapp;iPhone;10.0.4;{iosVer};{uuid};network/wifi;ADID/{ADID};supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone{iPhone},1;addressid/{addressid};supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS {iosV} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'
    else:
        return UserAgent


## 获取通知服务
class msg(object):
    def __init__(self, m=''):
        self.str_msg = m
        self.message()

    def message(self):
        global msg_info
        print(self.str_msg)
        try:
            msg_info = "{}\n{}".format(msg_info, self.str_msg)
        except:
            msg_info = "{}".format(self.str_msg)
        sys.stdout.flush()

    def getsendNotify(self, a=0):
        if a == 0:
            a += 1
        try:
            url = 'https://gitee.com/curtinlv/Public/raw/master/sendNotify.py'
            response = requests.get(url)
            if 'curtinlv' in response.text:
                with open('sendNotify.py', "w+", encoding="utf-8") as f:
                    f.write(response.text)
            else:
                if a < 5:
                    a += 1
                    return self.getsendNotify(a)
                else:
                    pass
        except:
            if a < 5:
                a += 1
                return self.getsendNotify(a)
            else:
                pass

    def main(self):
        global send
        cur_path = os.path.abspath(os.path.dirname(__file__))
        sys.path.append(cur_path)
        if os.path.exists(cur_path + "/sendNotify.py"):
            try:
                from sendNotify import send
            except:
                self.getsendNotify()
                try:
                    from sendNotify import send
                except:
                    print("加载通知服务失败~")
        else:
            self.getsendNotify()
            try:
                from sendNotify import send
            except:
                print("加载通知服务失败~")
        ###################


msg().main()


# @logger.catch
async def get_headers():
    """
    获取请求头
    :return:
    """
    headers = {
        'Host': 'ms.jr.jd.com',
        'Connection': 'keep-alive',
        'Origin': 'https: // gongyi.m.jd.com',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'WebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 MicroMessenger/8.0.3.1880(0x28000334) Process/appbrand1 WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm32 MiniProgramEnv/android',
        'X-Requested-With': 'com.jingdong.app.mall',
        'accesstoken': 'bf7bf003946047c7263abd91aae71b07',
        'Accept-Encoding': 'gzip,br,deflate',
        'Referer': 'https://gongyi.m.jd.com/m/welfare/donate/index.html',
    }
    return headers


async def post(session, url, body=None):
    try:
        if body is None:
            body = {}
        response = await session.post(url=url, data=body)
        await asyncio.sleep(1)
        text = await response.text()
        data = json.loads(text)
        return data
    except Exception as e:
        print('请求服务器错误, {}!'.format(e.args))
        return {
            'success': False
        }


async def get(session, url):
    try:
        response = await session.get(url=url)
        await asyncio.sleep(1)
        text = await response.text()
        data = json.loads(text)
        return data
    except Exception as e:
        print('请求服务器错误, {}!'.format(e.args))
        return {
            'success': False
        }


# POST https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/getToBeCollect HTTP/1.1  获取任务列表
async def getToBeCollect_task(session):
    """
    查询用户信息
    :return:
    """
    url = 'https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/getToBeCollect'
    params = {"sourceType": "android", "gatherType": "task"}
    body = 'reqData={}'.format(quote(json.dumps(params)))
    data = await post(session, url, body)
    if data['resultCode'] == 0 and data['resultData']['code'] == '0000':
        print(f"""获取任务列表{data['resultData']['info']}""")
        taskRewardInfoList = data['resultData']['taskRewardInfoRes']['taskRewardInfoList']
        for task in taskRewardInfoList:
            if task['status'] == 5:
                print(f"""任务:{task['taskName']}, 今日已完成!""")
                continue
            if task['status'] == 4:
                print(f"""任务:{task['taskName']}, 奖励待领取!""")
                receiveId1 = task['receiveId']
                await asyncio.sleep(1)
                await collect1(session, task, receiveId1)
            if task['status'] == 0 and task['taskType'] == 4 or task['taskType'] == 2:
                data = await receiveFqTask(session, task)
                await asyncio.sleep(7)
                if data['resultCode'] == 0 and data['resultData']['resultCode'] == '0000':
                    print(f"""浏览任务{data['resultData']['value']['taskName']}：{data['resultData']['resultMsg']}""")
                    data = await incrAndRewardTask(session, task)
                    if data['resultCode'] == 0 and data['resultData']['resultCode'] == '0000':
                        print(f"""任务回调：{data['resultData']['resultMsg']}""")
                        receiveId = data['resultData']['value']['receiveId']
                        await asyncio.sleep(0.5)
                        await collect1(session, task, receiveId)
                    elif data['resultCode'] == 0 and data['resultData']['resultCode'] == '1001':
                        print(f"""任务回调：{data['resultData']['resultMsg']}""")
                    else:
                        print(f"""任务回调异常：{data}""")
                elif data['resultCode'] == 0 and data['resultData']['resultCode'] == '1001':
                    print(f"""浏览任务：{data['resultData']['resultMsg']}""")
                else:
                    print(f"""浏览任务：{data}""")
    elif data['resultCode'] == 0 and data['resultData']['code'] == '1001':
        print(f"""获取任务列表{data['resultData']['info']}""")
        return data['resultData']['info']
    else:
        print(f"""获取任务列表异常{data}""")
    return 999


# https://ms.jr.jd.com/gw/generic/zc/h5/m/receiveFqTask HTTP/1.1
async def receiveFqTask(session, task):
    """
    查询用户信息
    :return:
    """
    await asyncio.sleep(0.5)
    try:
        url = 'https://ms.jr.jd.com/gw/generic/zc/h5/m/receiveFqTask'
        params = {"channelCode": task['channelCode'], "taskCode": task['taskCode'], "deviceInfo": {}}
        body = 'reqData={}'.format(quote(json.dumps(params)))
        data = await post(session, url, body)
        return data
    except Exception as e:
        print(e.args)


# POST https://ms.jr.jd.com/gw/generic/zc/h5/m/incrAndRewardTask HTTP/1.1
async def incrAndRewardTask(session, task):
    """
    查询用户信息
    :return:
    """
    await asyncio.sleep(0.5)
    try:
        url = 'https://ms.jr.jd.com/gw/generic/zc/h5/m/incrAndRewardTask'
        params = {"channelCode": task['channelCode'], "taskCode": task['taskCode'], "deviceInfo": {}}
        body = 'reqData={}'.format(quote(json.dumps(params)))
        data = await post(session, url, body)
        return data
    except Exception as e:
        print(e.args)


# POST https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/collect HTTP/1.1
async def collect1(session, task, receiveId):
    """
    查询用户信息
    :return:
    """
    url = 'https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/collect'
    params = {"sourceType": "android", "contributeNums": task['rewardAmount'], "contributeType": task['contributeType'],
              "receiveId": receiveId, "extMap": {"bannerName": task['taskName']}, "deviceInfo": {}, "inviteCode": ""}
    body = 'reqData={}'.format(quote(json.dumps(params)))
    data = await post(session, url, body)
    if data['resultCode'] == 0 and data['resultData']['code'] == '0000':
        print(f"""领取任务奖励：{data['resultData']['info']},获得{task['rewardAmount']}g能量""")
        return data
    elif data['resultCode'] == 0 and data['resultData']['code'] == '0001':
        print(f"""领取任务奖励：{data['resultData']['info']}""")
        return data['resultData']['info']
    else:
        print(f"""领取任务奖励：{data}""")
    return 999


# POST https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/getToBeCollect HTTP/1.1  查询有没有能量收取
async def getToBeCollect(session):
    """
    查询用户信息
    :return:
    """
    url = 'https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/getToBeCollect'
    params = {"sourceType": "android", "gatherType": "normal"}
    body = 'reqData={}'.format(quote(json.dumps(params)))
    data = await post(session, url, body)
    await asyncio.sleep(1)
    if data['resultCode'] == 0 and data['resultData']['code'] == '0000':
        if data['resultData']['signTaskContributeInfoRes']['code'] == '0000':
            print(f"""开始执行每日打卡任务""")
            for item in data['resultData']['signTaskContributeInfoRes']['taskContributeInfoList']:
                contributeNums = item['contributeG']
                contributeType = item['contributeType']
                await collect(session, contributeNums, contributeType)
        elif data['resultData']['signTaskContributeInfoRes']['code'] == '2010':
            print(f"""每日打卡任务：{data['resultData']['signTaskContributeInfoRes']['info']}""")
        else:
            print(f"""每日打卡任务异常：{data}""")
        if data['resultData']['contributeInfoRes']['code'] == '0000':
            print(f"""开始收取订单能量""")
            contributeNums = data['resultData']['contributeInfoRes']['partContributeInfoMap']['2']['partContributeGNums']
            contributeType = data['resultData']['contributeInfoRes']['partContributeInfoMap']['2']['contributeType']
            await collect(session, contributeNums, contributeType)
        elif data['resultData']['contributeInfoRes']['code'] == '2004':
            print(f"""收取订单能量：{data['resultData']['contributeInfoRes']['info']}""")
        else:
            print(f"""收取订单能量异常：{data}""")
    else:
        print(f"""查询能量收取异常{data}""")
    return 999


# POST https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/collect HTTP/1.1
async def collect(session, contributeNums, contributeType):
    """
    查询用户信息
    :return:
    """
    invoteCode = await getInviteCode12(session)
    url = 'https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/collect'
    params = {"sourceType": "android", "contributeNums": contributeNums, "contributeType": contributeType,
              "receiveId": None,
              "deviceInfo": {}, "inviteCode": invoteCode}
    body = 'reqData={}'.format(quote(json.dumps(params)))
    data = await post(session, url, body)
    if data['resultCode'] == 0 and data['resultData']['code'] == '0000':
        msg(f"""收取能量：{data['resultData']['info']}""")
        return data
    elif data['resultCode'] == 0 and data['resultData']['code'] == '1001':
        msg(f"""收取能量：{data['resultData']['info']}""")
        return data['resultData']['info']
    else:
        print(f"""收取能量异常{data}""")
    return 999

# POST https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/contribute1 HTTP/1.1   捐赠公益能量
async def getInviteCode12(session):
    """
    查询用户信息
    :return:
    """
    await asyncio.sleep(2)
    try:
        url = 'https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/getInviteCode12'
        params = {"sourceType":"h5"}
        body = 'reqData={}'.format(quote(json.dumps(params)))
        data = await post(session, url, body)
        if data['resultCode'] == 0 and data['resultData']['code'] == '0000':
            print(f"""{data['resultData']['info']}""")
        elif data['resultCode'] == 0 and data['resultData']['code'] == '2013':
            print(f"""{data['resultData']['info']}""")
        else:
            print(f"""捐赠公益能量异常{data}""")
        return data['resultData']['invoteCode']
    except Exception as e:
        print(e.args)


# POST https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/showUserAchievementInfo1 HTTP/1.1  公益成就获取
async def showUserAchievementInfo1(session):
    """
    查询用户信息
    :return:
    """
    url = 'https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/showUserAchievementInfo1'
    params = {"sourceType": "android", "queryType": 2}
    body = 'reqData={}'.format(quote(json.dumps(params)))
    data = await post(session, url, body)
    await asyncio.sleep(0.5)
    if data['resultCode'] == 0 and data['resultData']['code'] == '0000':
        print(f"""公益成就获取{data['resultData']['info']}""")
        msg(
            f"""{data['resultData']['nikeName']}：可捐赠能量{data['resultData']['canContributeNums']}，累计捐助公益能量{data['resultData']['contributeG']}，累计收能量{data['resultData']['collectGTotal']}，兑换订单{data['resultData']['collectOrderTotal']}笔，已参与项目{data['resultData']['collectOrderTotal']}项""")
        contribute_num = data['resultData']['canContributeNums']
        if contribute_num > 0:
            await queryItemList(session, contribute_num)
        else:
            print(f"""没有能量可以捐赠""")
    elif data['resultCode'] == 0 and data['resultData']['code'] == '1001':
        print(f"""公益成就获取{data['resultData']['info']}""")
        return data['resultData']['info']
    else:
        print(f"""公益成就获取异常{data}""")
    return 999


# POST https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/queryItemList HTTP/1.1  获取公益活动
async def queryItemList(session, contribute_num):
    """
    查询用户信息
    :return:
    """
    url = 'https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/queryItemList'
    params = {"sourceType": "android"}
    body = 'reqData={}'.format(quote(json.dumps(params)))
    data = await post(session, url, body)
    await asyncio.sleep(0.5)
    if data['resultCode'] == 0 and data['resultData']['code'] == '0000':
        print(f"""获取公益活动：{data['resultData']['info']}""")
        itemResList = data['resultData']['itemResList']
        for item in itemResList:
            if item['mainItem'] == True:
                print(f"""公益活动：{item['itemName']}筹集进度已完成""")
                continue
            if item['mainItem'] == False:
                if contribute_num >= 30:
                    contributeNums = 10
                elif contribute_num >= 15:
                    contributeNums = 5
                elif contribute_num >= 3:
                    contributeNums = 1
                else:
                    print(f"""公益能量不足""")
                    break
                data = await contribute1(session, item, contributeNums)
                if data['resultCode'] == 0 and data['resultData']['code'] == '0000':
                    msg(f"""捐赠公益能量{item['itemName']}：{data['resultData']['info']}""")
                    continue
                elif data['resultCode'] == 0 and data['resultData']['code'] == '2013':
                    print(f"""捐赠公益能量{item['itemName']}：{data['resultData']['info']}""")
                else:
                    print(f"""捐赠公益能量异常{data}""")
    elif data['resultCode'] == 0 and data['resultData']['code'] == '1001':
        print(f"""获取公益活动：{data['resultData']['info']}""")
        return data['resultData']['info']
    else:
        print(f"""捐赠公益能量异常{data}""")
    return 999


# POST https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/contribute1 HTTP/1.1   捐赠公益能量
async def contribute1(session, item, contributeNums):
    """
    查询用户信息
    :return:
    """
    await asyncio.sleep(2)
    try:
        url = 'https://ms.jr.jd.com/gw/generic/cxyfb/h5/m/contribute1'
        params = {"itemId": item['itemId'], "inviteCode": "", "sourceType": "android", "contributeNums": contributeNums,
                  "deviceInfo": {}}
        body = 'reqData={}'.format(quote(json.dumps(params)))
        data = await post(session, url, body)
        return data
    except Exception as e:
        print(e.args)


async def run():
    """
    程序入口
    :return:
    """
    scriptName = '订单公益'
    print(scriptName)
    cookiesList, userNameList, pinNameList = getCk.iscookie()
    user_num = 1
    for ck, userName in zip(cookiesList, userNameList):
        ck = ck.rstrip(';')
        ck = dict(item.split("=") for item in ck.split(";"))
        print(f"""账号{user_num}:{userName}""")
        headers = await get_headers()
        async with aiohttp.ClientSession(headers=headers, cookies=ck) as session:
            await getToBeCollect(session)
            await asyncio.sleep(1)
            await getToBeCollect_task(session)
            await asyncio.sleep(1)
            await showUserAchievementInfo1(session)
        user_num += 1
    if isNotice:
        send(scriptName, msg_info)
    else:
        print("\n", scriptName, "\n", msg_info)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

