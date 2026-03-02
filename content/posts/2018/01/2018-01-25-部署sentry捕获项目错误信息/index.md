---
title: "部署sentry捕获项目错误信息"
date: 2018-01-25
description: "sentry是一款专用于捕捉项目错误信息的分布式开源软件，可以轻松的捕捉到不同项目的错误信息并汇总，方便实时查看上下文排错以及报警等。 最终效果图如下："
categories: 
  - "计算机"
tags: 
  - "flask"
  - "sentry"
  - "测试"
  - "运维"
---

sentry是一款专用于捕捉项目错误信息的分布式开源软件，可以轻松的捕捉到不同项目的错误信息并汇总，方便实时查看上下文排错以及报警等。 最终效果图如下： ![](images/sentry1.jpg) ![](images/sentry2.jpg) ![](images/sentry3.jpg) <!--more--> 首先，sentry和ELK的不同之处在于，虽然都基于LOG的追踪，但sentry主要关注错误的捕获和上下文重出现报警，而ELK主要关注日志的处理。

#### 1.sentry的部署

官方文档 [https://docs.sentry.io/](https://docs.sentry.io/) 大致来说，主要分为如下几个步骤：

```bash
#安装postgresql
apt-get install postgresql
apt-get install postgresql-contrib

#安装celery，redis
pip install celery
apt-get install redis-server

#安装需要的包
apt-get install python-setuptools python-dev libxslt1-dev gcc libffi-dev libjpeg-dev libxml2-dev libxslt-dev libyaml-dev libpq-dev

#安装sentry，推荐使用venv环境
pip install sentry

#生成配置文件,也可制定配置文件路径
#sentry init /etc/sentry 
sentry init

#配置数据库
sudo -u postgres psql
create user admin with password 'admin';
create database sentry owner admin;
grant all privileges on database sentry to admin;

#提升该用户superuser权限
alter role admin superuser;

#修改sentry的相关配置，配置数据库相关设置，与上数据库设置相符合
vi /root/.sentry/sentry.conf.py

#初始化数据库，可以制定配置文件路径也可默认
#SENTRY_CONF=/etc/sentry sentry upgrade
sentry upgrade

#添加celery用root用户跑的环境变量
export C_FORCE_ROOT="true"

#最后创建用户
sentry createuser
```

在upgrade过程中可能会出现错误，根据具体错误类型判断如何排错，然后删掉数据库后重建数据库，再upgrade即可，一般都是数据库权限问题。

#### 2.sentry的使用

主要要跑3个任务，如下

```bash
#SENTRY_CONF=/etc/sentry sentry run web
sentry run web
#SENTRY_CONF=/etc/sentry sentry run worker
sentry run worker
#SENTRY_CONF=/etc/sentry sentry run cron
sentry run cron

```

我在测试环境中是用gosuv来跑的，效果如图： ![](images/gosuv.jpg) 其中要注意的是，如果任务直接用

```bash
sentry run web

```

这样来跑的话，会找不到配置文件，所以需要配置成如下结构： ![](images/gosuv2.jpg) 同时，还跑了一个用于测试监控捕获错误的flask程序，其中用到了venv，所以gosuv也好，supervisor也好，都需要做成如下设置

```bash
#找到venv的虚拟环境，用虚拟环境的bin运行项目
./venv/bin/python runserver.py
```

#### 3.sentry web的应用和配置

默认起的sentry web占用的是9000端口，也可以自己修改端口号。 登陆ip:9000，输入刚才设置的邮箱账号密码进入sentry，填一下相关设置 点击右上角new project,选择你需要监控错误的对象，这里选择flask，然后会出现 ![](images/sentry4.jpg) 主要关注这个DSN key，在已有的项目可以在这里查看 ![](images/sentry5.jpg)

然后首先在客户端安装maven\[flask\]

```bash
pip install raven[flask]
```

最后在flask程序里添加如下

```python
#__init__.py里设置app，故添加如下
from raven.contrib.flask import Sentry
sentry = Sentry(app, 
 dsn='http://f1010071f12c47768dc6b5a4700d9c2e:5643252bcc70471eb5232a632f3ea133@10.32.80.118:9000//2'
 )

#views.py里添加如下
from flask_security import login_required, current_user
from hello import app
from hello import sentry

@app.route('/error')
def error():
    try:
        1/0
    except ZeroDivisionError:
        sentry.captureException()
        return 'error'

@app.route('/raise')
def auto_raise():
    raise IndexError

@app.route('/log')
def log():
    sentry.captureMessage('hello, world!')
    return 'logging'
```

类似如图结构： ![](images/flask.jpg)

然后就可以在sentry中即时捕捉到对应的错误和logging了
