---
title: "利用nginx_upload_module搭建http文件服务器"
date: 2018-04-24
tags: 
  - "nginx"
---

服务端主要就是用的nginx-upload-module和nginx-fancyindex两个nginx模块做接收，然后python后端做处理 然后客户端的编写分为两部分,一部分是python客户端,用的requests库,另一部分是web客户端,用的是Huploadify框架

结果大致如下: ![](images/9F609413-78FF-43FD-96F7-7B63BC01B37B.png)![](images/企业微信截图_4a62da5a-4642-4639-b2b6-8b32827c5195.png) <!--more-->

大致画一下前后端结构

client.py --> nginx-upload-module(temp) -->python module

nginx-upload-page --> nginx-upload-module(temp) ---> python module 详情比较简单,不细述.

源代码git地址: [https://github.com/calmkart/nginx\_upload](https://github.com/calmkart/nginx_upload) [https://github.com/calmkart/nginx\_upload\_page](https://github.com/calmkart/nginx_upload_page)
