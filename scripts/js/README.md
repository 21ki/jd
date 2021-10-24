# [聚看点](https://www.kejiwanjia.com/jiaocheng/28426.html)
安卓在抓包历史中搜openid，ios在www.xiaodouzhuan.cn链接上看请求头部的xz_jkd_appkey就可以（注意ios后面的!IOS!5.6.5是不需要的复制的）


#青龙面板配置文件填写参数
```
#单账号示例
export jkdhd='{"openid": "参数1"}'
export jkdck='{"Cookie":"xz_jkd_appkey=参数1"}'
#多账号用@隔开 示例
export jkdhd='{"openid": "参数1"}'@'{"openid": "参数2"}'
export jkdck='{"Cookie":"xz_jkd_appkey=参数1"}'@'{"Cookie":"xz_jkd_appkey=参数2"}'
```