---
title: "saltshaker--一个salt的webui"
date: 2018-07-06
categories: 
  - "计算机"
tags: 
  - "django"
  - "salt"
  - "saltstack"
---

salt的webui,官方的是halite,但已经被放弃了，不维护很久了 尝试过其他几个star比较的开源实现,比如saltpad,但要么就是bug满天飞,要么就是技能栈不符难以二次开发 最后发现了一个开源实现叫saltshaker的不错,最终效果如下 [![](images/企业微信截图_82481f1c-b153-4fb5-928f-2b98163e9635.png)](http://www.calmkart.com/wp-content/uploads/2018/07/企业微信截图_82481f1c-b153-4fb5-928f-2b98163e9635.png) <!--more-->

官方项目地址 [https://github.com/yueyongyue/saltshaker](https://github.com/yueyongyue/saltshaker) 部署文档见 install.txt

大致总结过程如下,非详情.

```
git clone https://github.com/yueyongyue/saltshaker.git
pip install virtualenv
virtualenv env
source env/bin/activate
yum install salt-api.noarch

salt-api --version
pip install cherrypy==3.8.0
useradd -M -s /sbin/nologin admin
passwd admin
vim /etc/salt/master.d/saltapi.conf
systemctl restart salt-master.service
systemctl restart salt-api.service
systemctl status salt-api.service
systemctl status salt-master.service
lsof -i:50075
pip install Django==1.8.4
pip install django-crontab

yum install python-devel.x86_64
yum install mysql-devel
yum install MySQL-python
yum install gcc

pip install mysql-python

查源码，改dashboard/views里index函数checkport的端口

```

几个容易踩坑的地方:

1.centos7.4用pip安装mysql-python的时候，需要先安装python-devel,mysql-devel,MySQL-python,gcc,否则会报错

2.supervisor要自己装，相关配置自己写一下，也容易

3.如果salt-api等几个部件没有运行在默认端口，那么启动saltshaker后在首页会显示down的状态，需要修改dashboard/views.py里的index函数checkport里的端口号.

4.如果salt-master版本比较高(大于2015.x)，官方yum源的salt-api就没有与之对应的版本了，需要自己下载salt-api的新包，我是自建的yum源，然后

```
createrepo <path>
createrepo --update <path> 

```

更新仓库信息，安装最新的包

5.django crontab在settings.py里被注释掉了3个，得把注释去掉，然后把所有django crontab跑起来.

最后，这个东西感觉也不是很完善好用，不过是django的，二次开发也很容易，有机会再自己来改改。
