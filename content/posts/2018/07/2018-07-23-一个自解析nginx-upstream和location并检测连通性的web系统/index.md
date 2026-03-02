---
title: "一个自解析nginx upstream和location并检测连通性的web系统"
date: 2018-07-23
description: "最近做的一个小web系统，主要的思路是，怎样才能将nginx集群的海量配置文件,包括server和upstream及location等完全对象化 想做的东西就类似于httpdns，将nginx的海量配置文件对象化，或者考虑能不能数据库化..."
categories:
  - "计算机"
tags:
  - "nginx"
  - "运维开发"
---

最近做的一个小web系统，主要的思路是，怎样才能将nginx集群的海量配置文件,包括server和upstream及location等完全对象化 想做的东西就类似于httpdns，将nginx的海量配置文件对象化，或者考虑能不能数据库化 现在的功能只是解析所有nginx配置文件,自动读取upstream列表和location中proxy_pass,然后做连接性追踪 当然,追踪列表也可自定义添加,在admin后台配置即可 最终效果图 <!-- 图片已丢失: custom.png --> <!-- 图片已丢失: back.png --> <!--more--> git地址 [https://github.com/calmkart/check_port](https://github.com/calmkart/check_port)

```nginx
#大致部署过程
pip install -r pip.text
#创建checkport数据库
#修改settings.py中的数据库配置
python manage.py makemigrations
python manage.py migrate
#安装redis,修改settings.py中的redis配置
#修改readnginx的handle.py和handle_test.py中的CONFIG_PATH以及GIT_PATH(用于自动解析和更新nginx配置)
#用supervisor启动系统
supervisord -c checkport/supervisord.conf
#此外,flower需要用nginx做转发,参考配置文件如下
location ~ ^/flower/? {
rewrite ^/flower/?(.*)$ /$1 break;

sub_filter '="/' '="/flower/';
sub_filter_last_modified on;
sub_filter_once off;

# proxy_pass http://unix:/tmp/flower.sock:/;
proxy_pass http://xxxxxxxxxxxxxxxx;
proxy_redirect off;
proxy_set_header Host $host;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_http_version 1.1;
}

其中三种常见操作为:
1.将nginx配置文件列表pull到最新
2.自动读取和解析nginx配置文件,并将获取的upstream以及proxy_pass列表写进数据库
3.探测数据库中所有需要探测的IP:PORT对象实例

可在后台管理->数据更新中手动按键更新
也可在admin后台配置Periodic tasks的celery beat定时任务
其中:
1.readnginx.tasks.git_pull_config 任务更新nginx配置文件仓库
2.pubstatus.tasks.get_status 任务获取所有IP:PORT对象状态
3.readnginx.tasks.read_nginx 任务度读取nginx配置文件并解析,更新数据库IP:PORT对象列表
可根据需求设置定时任务周期
通过flower后台可以查看任务执行情况

自定义追踪checkport的IP:PORT列表通过admin后台添加instance即可实现
```
