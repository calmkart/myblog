---
title: "Django sso server(一个用户友好的的单点登录系统)"
date: 2018-09-28
categories: 
  - "计算机"
tags: 
  - "django"
  - "python"
  - "sso"
  - "单点登录"
---

最近写了一个单点登录系统,这里做一些总结.

[![](images/5C45207A-AF09-475D-ACD6-E732CFE1596D.png)](http://www.calmkart.com/wp-content/uploads/2018/09/5C45207A-AF09-475D-ACD6-E732CFE1596D.png) github地址:(欢迎来star一发^\_^) [https://github.com/calmkart/Django-sso-server](https://github.com/calmkart/Django-sso-server) <!--more-->

### 1.流程原理

#### <1>.系统管理流程

管理员在初始化系统时，填写ldap相关设置以及管理员账号相关设置，之后管理员账号可以在管理员后台调整相关配置 其中: a.系统初始化时将自动生成rsa公私钥,系统中所有涉及的密码,都会经过aes加密存放在数据库中,包括rsa私钥也会经过aes加密存放 b.在取用密码时将调用aes解密,加密的salt写在了common/crypto.py中,也可以自己替换

#### <2>.用户流程

用户登录sso系统，验证ldap账号成功后，将用户信息以

```
now = time.time()
user_info = "{0}|||||{1}".format(ldap_username, now)

```

的形式,通过rsa公钥加密写入cookie中，key为sso\_user

```
response.set_cookie('sso_user', rsa.crypto(
                public_key, user_info), domain=options.objects.all()[0].cookie_domain)
```

其他需要接入sso系统的子系统可以通过sso系统的api，来判断用户是否可以登录

```
url:      /api/auth
method:   POST
post_json_data:  {"sso_user":cookie}
return:     {"status":True/False, "msg":username}

```

本sso系统已提供了相关装饰器，可在管理后台-添加站点的帮助栏查看

```
import requests

def auth_login(func):
'''
装饰器,用于需要登录的views functions,将读取cookie并调用sso的api获取username

也可手动编写相关装饰器
sso系统的登录鉴权api为"http://sso域名/api/auth"(如"http://sso.calmkart.com/api/auth")
用POST方法以json形式将sso_cookie传给上述api,
返回{"status":True, "msg":{username}}则登录成功
否则{"status":False, "msg":{exception}}则登录失败

'''
    def _auth(request):
        cookie = request.COOKIES.get("sso_user", "")
        if cookie=="":
            return HttpResponseRedirect("{http://sso站域名/}")
        r = request.post("{http://sso站域名/api/auth}",data={"sso_cookie":cookie})
        if r.json()["status"]==False:
            return HttpResponseRedirect("{http://sso站域名}")
        else:
            username = r.json()["msg"]
            if username == "" or username == "error":
                return HttpResponseRedirect("{http://sso站域名/}")
            else:
                return func(request, username)
    return _auth

```

用户拥有cookie后登陆系统，系统将解cookie，并获取当前时间，若时间不超过最大时间，则返回username

#### <3>.企业扫码登陆流程

在管理后台配置企业微信扫码登陆相关参数，通过企业微信相关js api，生成二维码，用户扫码后，企业微信后台将用户请求重定向到/api/wxlogin  (method:get)上，并加上携带有用户username信息的code参数，成功则写cookie。

 

### 2.common相关模块原理

参见本blog其他博文

#### <1>[关于django的图片验证码](http://www.calmkart.com/?p=332)

#### <2>[关于python操作ldap](http://www.calmkart.com/?p=355)

#### <3>[关于python操作rsa,aes加解密](http://www.calmkart.com/?p=353)

---

## 历史评论 (9 条)

*以下评论来自原 WordPress 站点，仅作存档展示。*

> **wzzzx** (2019-03-04 15:01)
>
> 请问idap是啥哦，百度谷歌都看不懂

  > ↳ **calmkart** (2019-03-07 10:55)
  >
  > ldap
  > https://zh.wikipedia.org/zh-hans/%E8%BD%BB%E5%9E%8B%E7%9B%AE%E5%BD%95%E8%AE%BF%E9%97%AE%E5%8D%8F%E8%AE%AE

> **( 曰..曰 )** (2019-04-18 17:23)
>
> 牛逼轰轰的彭董，不知道psc还招不招实习生，求大佬赏口饭吃啊

  > ↳ **calmkart** (2019-04-19 11:23)
  >
  > 彭董快饿死了，总裁谢行行好吧

> **lixueming** (2019-06-01 15:23)
>
> 大神好，我是19届的应届生，今年校招拿了些offer，都是跟Python相关的，我对Python的熟悉程度只是会用，算不上很了解，比较纠结的是，一个offer是偏运维开发，一个是做广告系统业务研发，不知道这2个方向以后的发展怎么样，会不会有什么坑呢，烦请大神指点下，不胜感激！

  > ↳ **calmkart** (2019-06-03 10:35)
  >
  > 看公司,python的业务开发其实面不太广,但在算法方面应用比较多.
  > 纯业务开发写来写去写久了很烦,但是运开也有很多方向,总的来说如果是一般运维前景是肯定不如开发的
  > 要是能做更有技术含量的东西,比如paas云,或者去google之类的sre,肯定比一般开发要强很多.
  > 运开的使命其实就是革了传统op的命,开发既运维。
  > 语言也不是太重要,python/c/c++/js/go肯定都要会的.
  > 应届还是更多考虑公司吧.

> **路过** (2019-06-16 20:39)
>
> 这个不同域名可以支持吗， 比如 sso.abc.com 和 client.efg.com之间可以实现吗

  > ↳ **calmkart** (2019-06-17 13:21)
  >
  > 这个项目的实现方式是基于cookie携带信息的，所以不支持跨域登陆，要支持跨域需要用其他手段实现。

    > ↳ **路过** (2019-06-17 20:35)
    >
    > 好的，谢谢。
    >
    > 我还是尝试走跳转把token带过去再验证。
