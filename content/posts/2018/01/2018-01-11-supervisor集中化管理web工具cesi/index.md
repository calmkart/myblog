---
title: "supervisor集中化管理web工具cesi"
date: 2018-01-11
categories: 
  - "计算机"
tags: 
  - "supervisor"
  - "运维"
---

linux进程管理器supervisor是会经常被用到的，但服务器多了之后，每个服务器的进程也不方便管理。同时，supervisor自带的web界面比较简陋，所以尝试了一下官网推荐的一些第三方开源软件，推荐一下这个cesi。 最终效果如下： [![](images/1.jpg)](http://www.calmkart.com/wp-content/uploads/2018/01/1.jpg) [![](images/2.jpg)<!--more-->](http://www.calmkart.com/wp-content/uploads/2018/01/2.jpg)

1.首先是关于supervisor 通过apt或pip安装都可以

```
apt-get install supervisor
#pip install supervisor
echo_supervisord_conf > /etc/supervisor/supervisord.conf
```

关于supervisor配置文件

```
[unix_http_server]
#这里配置是否用unix socket通信来让supervisor与supervisorctl做通信

[inet_http_server]
#这里是用的http的方式做通信

[supervisorctl]
#这里选择supervisorctl到底用以上两种中的哪种方式来与supervisor通信，选择一种即可，记得填写密码

[program:pro_name]
stdout_logfile = {path}
redirect_stderr = true  ;让stderr也写入stdout中

```

常用操作

```
supervisorctl reload #重启加载supervisor配置文件
supervisorctl update #只增加新增的配置文件

```

2.关于cesi

项目地址：[https://github.com/Gamegos/cesi](https://github.com/Gamegos/cesi) 安装cesi

```
apt-get install sqlite3 python python-flask
git clone https://github.com/Gamegos/cesi
cd cesi
sqlite3 ./userinfo.db < userinfo.sql
cp cesi.conf /etc/cesi.conf

```

配置cesi.conf,我的配置如下，一看就懂了

```
[node:118]
username = ***
password = ***
host = 127.0.0.1
port = 9001

[node:calmkart]
username = ***
password = ***
host = 45.76.71.69
port = 9001

[node:121]
username = ***
password = ***
host = *.*.*.121
port = 9001

[environment:my_env]
members = 118,calmkart,121

[cesi]
database = /root/cesi/userinfo.db
activity_log = /var/log/cesi.log
host = 0.0.0.0
```

用supervisor运行cesi,配置文件如下

```
[program:cesi]
directory = /root/cesi/cesi/
command = python web.py
autostart = true
startsecs = 5
autorestart = true
startretries = 3
user = root
redirect_stderr = true
stdout_logfile = /var/log/cesi1.log
```

开启任务

```
supervisorctl start cesi
```

默认账号密码：admin,admin 端口需要改的自己去web.py里面改 you get it

本测试服地址： [http://cesi.calmkart.com](http://cesi.calmkart.com) 此外，其他常用的supervisor相关第三方工具还有 suponoff gosuv

---

## 历史评论 (3 条)

*以下评论来自原 WordPress 站点，仅作存档展示。*

> **qhh0205** (2018-07-18 23:00)
>
> 你好，cesi 支持管理多个服务器的进程吗？我看你截图貌似支持管理多个服务器的。我用默认的supervisor web UI，不支持管理多个服务器的supervisor。

  > ↳ **qhh0205** (2018-07-18 23:26)
  >
  > sorry，刚没仔细看，是支持的

> **potoo** (2019-05-19 16:49)
>
> 你好，我看你提供的[测试地址](http://cesi.calmkart.com)的 web 效果不一样，是你自己修改了吗? 你可以说下修改的方法吗？ 我也在用 cesi，但是 cesi 移动端页面显示有问题，想自己修改下页面，但是不知道在哪里修改。
